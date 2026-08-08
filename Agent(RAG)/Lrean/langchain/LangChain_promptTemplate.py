# 聊天提示词模板
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_deepseek import ChatDeepSeek

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system","你是一个专业的翻译"),
        MessagesPlaceholder("history"),  # 历史消息
        ("human","帮我翻译：北京的天气")  # 人输入
    ]
)

history_data = [
    ("human","你好"),
    ("ai","你好，有什么我可以帮助你的吗？"),
    ("human","你好，我想知道北京的天气"),
    ("ai","北京的天气是晴朗的"),
]

# 调用invoke方法
res_text = chat_prompt.invoke({"history":history_data}).to_string()

model = ChatDeepSeek(model="deepseek-chat")

res = model.invoke(res_text)
print(res.content)


