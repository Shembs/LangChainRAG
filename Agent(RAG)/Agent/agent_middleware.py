from langchain.agents import create_agent
from langchain.agents.middleware import before_agent, after_agent, before_model, after_model, wrap_model_call, \
wrap_tool_call
from langchain_classic.agents import Agent
from langchain_deepseek import ChatDeepSeek
from langchain_core.tools import tool
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.runtime import Runtime

"""
拦截器的连接时间

1.agent执行前
2.agent执行后
3.model执行前
4.model执行后
5.工具执行中
6.模型执行中

"""

@tool(description="查询指定城市的天气")
def get_weather(city: str) -> str:
    """查询指定城市的天气"""
    return f"{city}的天气是晴朗"

@before_agent
def log_before_agent(state: AgentState,runtime:Runtime) -> None:
# 打印agent执行前的状态
    print(f" [before_agent] agent启动，并附带{len(state['messages'])}条消息")

@after_agent
def log_after_agent(state: AgentState,runtime:Runtime) -> None:
# 打印agent执行后的状态
    print(f" [after_agent] agent执行完成，共处理{len(state['messages'])}条消息")

@before_model
def log_before_model(state: AgentState,runtime:Runtime) -> None:
# 打印model执行前的状态
    print(f" [before_model] model开始处理，共处理{len(state['messages'])}条消息")

@after_model
def log_after_model(state: AgentState,runtime:Runtime) -> None:
# 打印model执行后的状态
    print(f" [after_model] model执行完成，共处理{len(state['messages'])}条消息")

@wrap_model_call
def model_call_hook(reqeuest,hander) -> None:
    # 打印model调用前的状态
    print(f" [model_call_hook] model开始调用，共处理{len(reqeuest['messages'])}条消息")

@wrap_tool_call
def tool_call_hook(reqeuest,hander) -> None:
    # 打印工具调用前的状态
    print(f" [tool_call_hook] 工具开始调用，共处理{len(reqeuest['messages'])}条消息")
    return hander(reqeuest)

if __name__ == "__main__":
    agent = create_agent(
        model=ChatDeepSeek(model="deepseek-chat"),
        tools=[get_weather],
        system_prompt="你是一个专业的助手，你的任务是回答用户的天气问题。"
    )

    for chunk in agent.stream(
        {
            "messages": [{"role": "user", "content": "你好，我想知道北京的天气"}],
        },
        stream_model="values"
    ):
        print(chunk)
