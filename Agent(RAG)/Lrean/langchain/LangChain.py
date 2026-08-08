import os
# 大语言模型的调用LLM
# from langchain_deepseek import ChatDeepSeek

# 聊天模型的调用
from langchain_deepseek import ChatDeepSeek

# 消息简写可以省略SystemMessage,HumanMessage,AIMessage的定义
# from langchain_core.messages import HumanMessage,AIMessage,SystemMessage

# 文本嵌入模型
from langchain_deepseek import DeepSeekFaceEmbeddings

# 创建模型对象,不传model，默认使用text-embedding-ada-002模型，deep seek不支持文本嵌入模型
# embeddings = DeepSeekFaceEmbeddings()
# 不用invoke,stream方法调用模型，直接调用embed_query方法，返回嵌入向量

# print(embeddings.embed_query("你好"))
# print(embeddings.embed_documents(["你好","你好吗","你好吗？"]))





'''
# 大语言模型的调用
# 模型调用,model用于选择模型，api_key为使用AI的密钥，直接将密钥配置在环境变量中不需要在代码中呈现出来
DeepSeek = ChatDeepSeek(
    model="deepseek-chat",
)
# 使用invoke方法调用模型
# res = DeepSeek.invoke(input="你是什么大模型")

# 使用stream方法调用模型，流式输出
text = DeepSeek.stream(input="你好")
# 对模型的流式输出进行遍历，打印每个元素的内容
for chunk in text:
    print(chunk.content,end="",flush=True)
'''


# 聊天模型的调用
# DeepSeek = ChatDeepSeek(model="deepseek-chat")

# 定义消息序列,包含系统消息、用户消息、助手消息
# messages = [
#     SystemMessage(content="你是一个温柔体贴的助手，帮助用户解决问题以及陪伴用户"),
#     HumanMessage(content="你好"),
#     AIMessage(content="你好，我是你的助手，我可以帮助你解决问题以及陪伴你"),
#     HumanMessage(content="你认为我是一个什么样的人"),
# ]


# 消息简写
# messages = [
#     ("system","你是一个温柔体贴的助手，帮助用户解决问题以及陪伴用户"),
#     ("human","你好"),
#     ("ai","你好，我是你的助手，我可以帮助你解决问题以及陪伴你"),
#     ("human","你认为我是一个什么样的人"),
# ]
#
#
# res = DeepSeek.stream(input=messages)
# # 对模型的流式输出进行遍历，打印每个元素的内容
# for chunk in res:
#     print(chunk.content,end="",flush=True)





