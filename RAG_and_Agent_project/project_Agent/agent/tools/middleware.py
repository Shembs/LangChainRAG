from typing import Callable
from utils.prompt_loader import load_system_prompts, load_report_prompts
from langgraph.runtime import Runtime
from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command
from utils.logger_handler import logger



@wrap_tool_call
def monitor_tool(
        request:ToolCallRequest,
        handler:Callable[[ToolCallRequest], ToolMessage | Command],
)->ToolMessage | Command:
    logger.info(f"[tool monitor]执行工具: {request.tool_call['name']}")
    logger.info(f"[tool monitor]执行工具参数: {request.tool_call['args']}")

    try:
        result =  handler(request)
        logger.info(f"[tool monitor]工具执行结果: {request.tool_call['name']}调用成功")

        if request.tool_call['name'] == 'fill_content_for_report':
            request.runtime.context["prompt"] = True

        return result
    except Exception as e:
        logger.error(f"[tool monitor]工具执行结果: {request.tool_call['name']}调用失败, 错误信息: {e}")
        raise e


@before_model
def log_before_model(
        state:AgentState,
        runtime:Runtime,
):
    logger.info(f"[tool monitor]即将模型调用, 带有{len(state['messages'])}条消息")

    last_msg = state['messages'][-1]
    msg_type = last_msg.__class__.__name__
    content = last_msg.content
    content_str = content if isinstance(content, str) else str(content)
    logger.debug(f"[tool monitor]{msg_type} |  {content_str.strip()}")

    return None


@dynamic_prompt
def report_prompt_switch(request:ModelRequest):
    is_report = request.runtime.context.get("report", False)
    if is_report:
        return load_report_prompts()
    
    return load_system_prompts()
