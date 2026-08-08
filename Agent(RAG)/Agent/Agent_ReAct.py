from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langchain_core.tools import tool


@tool(description="获取体重，返回值是整数，单位是千克")
def get_weight() -> int:
    return 65


@tool(description="获取身高，返回值是整数，单位是厘米")
def get_height() -> int:
    return 175

if __name__ == "__main__":
    agent = create_agent(
        model=ChatDeepSeek(model="deepseek-chat"),
        tools=[get_weight, get_height],
        system_prompt="你是一个专业的助手，你的任务是回答用户的体重和身高,计算用户的BMI值。"
    )

    for chunk in agent.stream(
        {
            "messages": [{"role": "user", "content": "你好，我想知道我的BMI值"}],
        },
        stream_model="values"
    ):
        print(chunk)
