from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langchain_core.tools import tool


# @tool
# def get_weather(city: str) -> str:
#     """查询指定城市的天气"""
#     return f"{city}的天气是晴朗"

@tool(description="获取股价，传入股票名称，返回字符串信息")
def get_price(name:str) -> str:
    """查询指定商品的价格"""
    return f"{name}的价格是100元"

@tool(description="获取股票信息，传入股票名称，返回字符串信息")
def get_info(name:str) -> str:
    """查询指定商品的信息"""
    return f"股票{name}，是一家A股上市股票，股票代码是000001.SZ"


if __name__ == "__main__":
    agent = create_agent(
        model=ChatDeepSeek(model="deepseek-chat"),
        tools=[get_price, get_info],
        system_prompt="你是一个专业的助手，你的任务是回答用户的股票问题。"
    )

    for chunk in agent.stream(
        {
            "messages": [{"role": "user", "content": "你好，我想知道股票000001.SZ的价格"}],
        },
        stream_model="values"
    ):
        print(chunk)
