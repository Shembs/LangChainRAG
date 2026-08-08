# 聊天链
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_deepseek import ChatDeepSeek

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system","你是一个专业的天气助手"),
        MessagesPlaceholder("history"),  # 历史消息
        ("human","帮我查询：成都7月29日的天气")  # 人输入
    ]
)

history_data = [
    ("human","你好"),
    ("ai","你好，有什么我可以帮助你的吗？"),
    ("human","你好，我想知道北京的天气"),
    ("ai","北京的天气是晴朗的"),
]

model = ChatDeepSeek(model="deepseek-chat")

# 组成链,要求每一个组件都是Runnable接口的子类,顺序执行，前一个组件的输出作为下一个组件的输入
chain = chat_prompt | model

# 执行链,执行invoke或是stream方法，invoke方法返回的是一个ChatMessage对象
# result = chain.invoke({"history":history_data})
# print(result.content)

# stream流式输出
for chunk in chain.stream({"history":history_data}):
    print(chunk.content, end="",flush=True)

print(type(chain))
