from typing import Optional, Dict, Any, List
from openai import OpenAI
from typing_inspection.typing_objects import is_final

from agent.utils.nacos_val import get_system_config_from_nacos
from agent.utils.dde_logger import dde_logger as logger


def build_messages(
        system: Optional[str],
        history: Optional[List[List[str]]],
        chat_content: str
) -> List[Dict[str, str]]:
    """构建符合OpenAI格式的消息列表"""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})

    if history:
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})

    messages.append({"role": "user", "content": chat_content})
    return messages


def create_client(llm_config: Dict[str, Any]) -> OpenAI:
    """创建OpenAI客户端实例"""
    return OpenAI(
        api_key=llm_config["api_key"],
        base_url=llm_config["url"]
    )


async def handle_stream_output(rid: str, stream, request_increase_mode: bool):
    current_content = []
    current_reasoning = []

    system_config = get_system_config_from_nacos()
    log_mode = system_config["llm_config"]["log_mode"]  # 支持 original+all、original+simple、original、all、simple、none
    final_content = ""
    final_reasoning = ""
    i = 0
    for chunk in stream:
        if "original" in log_mode:
            logger.info(f"llm_client, rid = {rid} , chunk = {chunk}")
        if not chunk.choices or chunk.choices[0].delta is None:
            continue
        content = getattr(chunk.choices[0].delta, 'content', '') or ''
        reasoning_content = getattr(chunk.choices[0].delta, 'reasoning_content', '') or ''
        if content == "" and reasoning_content == "":
            continue
        if request_increase_mode:
            log_llm_output(content, reasoning_content, rid, i)
            final_content = content
            final_reasoning = reasoning_content
            yield {
                "content": content,
                "reasoning_content": reasoning_content
            }
        else:
            current_content.append(content)
            current_reasoning.append(reasoning_content)
            all_content = ''.join(current_content)
            all_reasoning = ''.join(current_reasoning)
            final_content = all_content
            final_reasoning = all_reasoning
            log_llm_output(all_content, all_reasoning, rid, i)
            yield {
                "content": all_content,
                "reasoning_content": all_reasoning
            }
        i = i + 1
    log_llm_output(final_content, final_reasoning, rid, i, True)


def log_llm_output(content, reasoning_content, rid: str, i: int, is_final_chunk=False):
    system_config = get_system_config_from_nacos()
    log_mode = system_config["llm_config"]["log_mode"]
    if "all" in log_mode or is_final_chunk or i == 0:
        logger.info(f"llm_client, i = {i} , is_final_chunk = {is_final_chunk} , rid = {rid} , content = {content} , reasoning_content = {reasoning_content} ")
    elif "simple" in log_mode:
        log_length = system_config["llm_config"]["log_length"]
        log_content = content
        log_reasoning_content = reasoning_content
        split_len = int(log_length / 2)
        if len(log_content) > log_length:
            log_content = log_content[:split_len] + "[...]" + log_content[-split_len:]
        if len(log_reasoning_content) > log_length:
            log_reasoning_content = log_reasoning_content[:split_len] + "[...]" + log_reasoning_content[-split_len:]
        logger.info(f"llm_client, i = {i} , is_final_chunk = {is_final_chunk} , rid = {rid} , log_content = {log_content} ,  log_reasoning_content = {log_reasoning_content} ")


def get_llm_config(service_url: str) -> Dict[str, Any]:
    """获取LLM服务配置，支持服务标签和URL匹配"""
    system_config = get_system_config_from_nacos()
    service_type_configs = system_config["llm_config"]["service_config"]
    default_config = system_config["llm_config"]["default_service_config"]

    result_config = default_config.copy()
    tag = "default"

    # 解析带标签的服务URL
    if "::" in service_url:
        parts = service_url.split("::")
        if len(parts) == 2:
            result_config["url"] = parts[0]
            tag = parts[1]
        else:
            raise ValueError(f"无效的带标签服务URL格式: {service_url}")
    else:
        result_config["url"] = service_url

    # 查找匹配的服务类型配置
    for config in service_type_configs:
        for url_match in config["url_match"]:
            if url_match in service_url and tag == config["tag"]:
                result_config.update({
                    k: v for k, v in config.items()
                    if k in ["model", "api_key", "think_able", "param", "feature"] and v is not None
                })
                break

    return result_config
