"""
ReAct Agent 封装模块

基于 LangChain create_agent 构建的智能体，集成中间件（工具监控、模型调用日志、
动态 prompt 切换）和多个业务工具（RAG 总结、天气查询、用户数据等）。
"""

from typing import Generator

from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (
    rag_summarize,
    get_user_id,
    get_user_city,
    get_weather,
    get_current_month,
    fetch_external_data,
    fill_content_for_report,
)
from agent.tools.middleware import (
    monitor_tool,
    log_before_model,
    report_prompt_switch,
)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
_STREAM_MODE: str = "values"
_DEFAULT_CONTEXT: dict[str, bool] = {"report": False}

# 业务工具列表（不包含中间件）
_AGENT_TOOLS: list = [
    get_user_id,
    get_user_city,
    rag_summarize,
    get_weather,
    get_current_month,
    fetch_external_data,
    fill_content_for_report,
]

# 中间件列表
_AGENT_MIDDLEWARE: list = [
    monitor_tool,
    log_before_model,
    report_prompt_switch,
]


class ReactAgent:
    """ReAct 智能体，封装了 LangChain create_agent 的创建和流式调用。

    使用示例:
        agent = ReactAgent()
        for chunk in agent.execute_stream("今天天气怎么样？"):
            print(chunk, end="", flush=True)
    """

    def __init__(self) -> None:
        self.agent = create_agent(
            model=chat_model,
            tools=_AGENT_TOOLS,
            system_prompt=load_system_prompts(),
            middleware=_AGENT_MIDDLEWARE,
        )

    def execute_stream(self, query: str) -> Generator[str, None, None]:
        """以流式方式执行用户查询，逐段产出模型回复文本。

        Args:
            query: 用户输入的查询字符串。

        Yields:
            str: 模型输出的文本片段（每次 yield 一个消息内容块 + 换行）。
        """
        input_dict: dict[str, list[dict[str, str]]] = {
            "messages": [
                {"role": "user", "content": query},
            ],
        }

        for chunk in self.agent.stream(
            input_dict,
            stream_mode=_STREAM_MODE,
            context=_DEFAULT_CONTEXT,
        ):
            latest_message = chunk["messages"][-1]
            content = latest_message.content

            # 跳过空内容（如仅含 tool_calls 的 AIMessage）
            if not content:
                continue

            # content 可能是 str（纯文本）或 list[dict]（多模态内容块）
            if isinstance(content, list):
                content = "".join(
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict)
                )

            yield content + "\n"


if __name__ == "__main__":
    agent = ReactAgent()
    for chunk in agent.execute_stream("扫地机器人在我所在的地区如何保养"):
        print(chunk, end="", flush=True)
