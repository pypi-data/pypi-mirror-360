import json
from typing import Optional, List, Dict, Any, AsyncGenerator, TypedDict, Literal, Union
from agent.utils import llm_util
from agent.utils.nacos_val import get_system_config_from_nacos
from asgi_correlation_id import correlation_id
import uuid, time
from agent.utils.dde_logger import statis_log
from agent.utils.dde_logger import dde_logger as logger

class LLMRequest(TypedDict, total=False):
    """LLM请求参数对象"""
    service_url: str
    chat_content: str
    system: Optional[str]
    history: Optional[List[List[str]]]
    back_service_urls: Optional[List[str]]
    auto_use_system_back_service: bool
    rid: Optional[str]
    timeout: Optional[int]
    # 允许额外的参数
    extra_params: Dict[str, Any]


class LLMClient:

    @staticmethod
    def get_llm_property(service_url: str) -> Dict[str, Any]:
        return llm_util.get_llm_config(service_url)

    @staticmethod
    def get_base_common_model(model_name: str = "qwen72b"):
        system_config = get_system_config_from_nacos()
        base_common_model_config = system_config["llm_config"]["base_common_model"]
        qwen72b = base_common_model_config["qwen72b"]
        return base_common_model_config.get(model_name, qwen72b)

    async def llm_stream(
            self,
            request: LLMRequest,
            request_increase_mode: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式调用LLM服务 - 使用请求对象方式"""
        async for response in self._call_llm_service(
                request_increase_mode=request_increase_mode,
                **request
        ):
            yield response

    def llm_invoke(self, request: LLMRequest):
        system_config = get_system_config_from_nacos()
        default_timeout_invoke = system_config["llm_config"]["timeout"]["invoke"]
        log_mode = system_config["llm_config"]["log_mode"]

        service_url = request.get("service_url")
        back_service_urls = request.get("back_service_urls")
        auto_use_system_back_service = request.get("auto_use_system_back_service", True)
        system = request.get("system")
        history = request.get("history", [])
        chat_content = request.get("chat_content")
        extra_params = request.get("extra_params", {})
        timeout = request.get("timeout", default_timeout_invoke)
        rid = request.get("rid")
        all_urls = self._build_service_urls(service_url, back_service_urls, auto_use_system_back_service)
        errors = []
        if not rid:
            rid = correlation_id.get()
            if not rid:
                rid = "agent_"
        messages = llm_util.build_messages(system, history, chat_content)
        message_str = json.dumps(messages, ensure_ascii=False)
        message_len = len(message_str)
        if not "all" in log_mode and len(message_str) > 120:
            message_str = message_str[:60] + "[...]" + message_str[-60:]
        for url in all_urls:
            new_rid = rid + "_" + str(uuid.uuid4())
            model = ""
            filtered_params = {}
            try:
                logger.info(f"尝试连接服务URL: {url}")
                t1 = time.time()
                llm_config = llm_util.get_llm_config(url)
                client = llm_util.create_client(llm_config)
                params = llm_config.get("param", {})
                if extra_params:
                    params.update(extra_params)
                filtered_params = self._filter_supported_params(params)
                trace_info = {"rid": new_rid, "requestId": new_rid}
                filtered_params.update(trace_info)
                model = llm_config["model"]
                if "max_completion_tokens" in filtered_params:
                    filtered_params["max_tokens"] = filtered_params["max_completion_tokens"]
                response = client.chat.completions.create(
                    model=llm_config["model"],
                    messages=messages,
                    stream=False,
                    timeout=timeout,
                    extra_body=filtered_params
                )
                logger.info(f"llm_invoke response, rid: {new_rid}, url = {url} , filtered_params: {filtered_params} , message: {message_str} ,  response: {response}")
                if response.choices:
                    message = response.choices[0].message
                    content = message.content or ""
                    reasoning_content = getattr(message, "reasoning_content", "") or ""
                    is_valid = bool(content) or bool(reasoning_content)
                    if is_valid:
                        elapsed_time_ms = int((time.time() - t1) * 1000)
                        res = {
                            "content": content,
                            "reasoning_content": reasoning_content
                        }
                        res_str = json.dumps(res, ensure_ascii=False)
                        res_len = len(res_str)
                        statis_log("normal", "common_api", "default", "llm_client", "invoke_" + url, "success", elapsed_time_ms, url, new_rid, model, filtered_params, f"[{message_len}]{message_str}", f"[{res_len}]{res_str}")
                        return res
                    else:
                        statis_log("normal", "common_api", "default", "llm_client", "invoke_" + url, "fail", "response.choices response invalid", url, new_rid, model, filtered_params, f"[{message_len}]{message_str}")
                else:
                    statis_log("normal", "common_api", "default", "llm_client", "invoke_" + url, "fail", "response.choices empty", url, new_rid, model, filtered_params, f"[{message_len}]{message_str}")
            except Exception as e:
                statis_log("normal", "common_api", "default", "llm_client", "invoke_" + url, "exception", e, url, new_rid, model, filtered_params, f"[{message_len}]{message_str}")
                error_msg = f"服务URL {url} 调用失败: {str(e)}"
                logger.error(f"call llm exception, rid={new_rid}, url={url}, {error_msg}", exc_info=True)
                errors.append(error_msg)
        logger.error(f"call llm final fail, {errors}, rid_pre={rid}", exc_info=True)
        raise Exception(f"所有服务URL调用失败: {errors}, rid_pre={rid}")

    async def _call_llm_service(
            self,
            service_url: str,
            chat_content: str,
            system: Optional[str] = None,
            history: Optional[List[List[str]]] = None,
            back_service_urls: Optional[List[str]] = None,
            auto_use_system_back_service: bool = True,
            rid: Optional[str] = None,
            timeout: Optional[int] = None,
            request_increase_mode: bool = True,
            **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """内部方法：调用LLM服务，支持重试逻辑"""
        system_config = get_system_config_from_nacos()
        default_timeout_stream = system_config["llm_config"]["timeout"]["stream"]
        log_mode = system_config["llm_config"]["log_mode"]
        all_urls = self._build_service_urls(service_url, back_service_urls, auto_use_system_back_service)
        errors = []
        if not timeout:
            timeout = default_timeout_stream
        if not rid:
            rid = correlation_id.get()
            if not rid:
                rid = "agent_"
        messages = llm_util.build_messages(system, history, chat_content)
        message_str = json.dumps(messages, ensure_ascii=False)
        message_len = len(message_str)
        if not "all" in log_mode and len(message_str) > 120:
            message_str = message_str[:60] + "[...]" + message_str[-60:]
        first_valid_chunk_received = False

        for url in all_urls:
            new_rid = rid + "_" + str(uuid.uuid4())
            try:
                logger.info(f"尝试连接服务URL: {url}")
                llm_config = llm_util.get_llm_config(url)
                client = llm_util.create_client(llm_config)
                params = llm_config.get("param", {})
                params.update(kwargs.get("extra_params", {}))
                filtered_params = self._filter_supported_params(params)
                trace_info = {"rid": new_rid, "requestId": new_rid}
                filtered_params.update(trace_info)
                model = llm_config["model"]
                if "max_completion_tokens" in filtered_params:
                    filtered_params["max_tokens"] = filtered_params["max_completion_tokens"]

                t1 = time.time()

                # 内部异步生成器处理流式响应
                async def process_stream():
                    nonlocal first_valid_chunk_received
                    stream_response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        stream=True,
                        timeout = timeout,
                        extra_body=filtered_params
                    )
                    async for _item in llm_util.handle_stream_output(new_rid, stream_response, request_increase_mode):
                        yield _item
                        if not first_valid_chunk_received:
                            first_valid_chunk_received = True

                first_token_time = 0
                try:
                    is_ft = True
                    async for item in process_stream():
                        if is_ft:
                            first_token_time = int((time.time() - t1) * 1000)
                            is_ft = False
                        yield item

                    # 如果完整处理了所有chunk，记录成功日志并返回
                    if first_valid_chunk_received:
                        elapsed_time_ms = int((time.time() - t1) * 1000)
                        statis_log("normal", "stream_api", "default", "llm_client", "stream_" + url, "success",
                                   elapsed_time_ms, first_token_time, url, new_rid, model, filtered_params, message_str, message_len)
                        return
                except Exception as e:
                    if first_valid_chunk_received:
                        statis_log("normal", "stream_api", "default", "llm_client", "stream_" + url, "exception", e, "first valid chunk already received,and received exception, will not use backup llm service",
                                   url, all_urls, new_rid, model, filtered_params, message_str, message_len)
                        return
                    else:
                        # 首个有效chunk未接收，视为该URL失败
                        statis_log("normal", "stream_api", "default", "llm_client", "stream_" + url, "exception", e, "no chunk received, will use backup llm service",
                                   url, all_urls, new_rid, model, filtered_params, message_str, message_len)
                        continue
            except Exception as e:
                statis_log("normal", "stream_api", "default", "llm_client", "stream_" + url, "exception", e, url, new_rid, message_str, message_len)
                error_msg = f"服务URL {url} 调用失败: {str(e)}"
                logger.error(f"call llm exception, rid={new_rid}, url={url}, {error_msg}", exc_info=True)
                errors.append(error_msg)

        logger.error(f"call llm final fail, {errors}, rid_pre={rid}", exc_info=True)
        raise Exception(f"所有服务URL调用失败: {errors}, rid_pre={rid}")

    def _build_service_urls(
            self,
            primary_url: str,
            back_urls: Optional[List[str]],
            use_system_back: bool
    ) -> List[str]:
        system_config = get_system_config_from_nacos()
        system_back_service = system_config["llm_config"]["system_back_service"]
        """构建完整的服务URL列表，包括备用服务"""
        urls = [primary_url] + (back_urls or [])
        if use_system_back:
            if isinstance(system_back_service, list):
                urls.extend(system_back_service)
            else:
                urls.append(system_back_service)
        return urls

    def _filter_supported_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        system_config = get_system_config_from_nacos()
        llm_supported_params = system_config["llm_config"]["llm_supported_params"]
        """过滤掉LLM服务不支持的参数"""
        filtered = {k: v for k, v in params.items() if k in llm_supported_params}
        unsupported = {k: v for k, v in params.items() if k not in llm_supported_params}

        if unsupported:
            print(f"忽略不支持的参数: {unsupported}")

        return filtered


# 提供模块级API接口，保持向后兼容性
_client = LLMClient()
get_llm_property = _client.get_llm_property
get_base_common_model = _client.get_base_common_model
llm_stream = _client.llm_stream
llm_invoke = _client.llm_invoke
