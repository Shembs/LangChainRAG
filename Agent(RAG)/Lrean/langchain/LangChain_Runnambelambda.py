# RunnambeLambda

# 通用提示词模板,zero-shot思想，不提供示例，只提供模板，基于PromptTemplate类实现
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# 实现字符串解析器
str_parser = StrOutputParser()

# 函数的入参：AIMessage -> dict ({"name":"xxx"}),可以将匿名函数直接存放在chain链中
runnable = RunnableLambda(lambda ai_msg:{"name":ai_msg.content})

# 调用.format方法，将模板中的占位符替换为实际值
prompt_template = PromptTemplate.from_template(
    "{last_name}和他的妻子{spouse_name}，刚生了{gender}，你帮我起一个名字，简单回答"
)

# 第二个提示词模板
second_prompt = PromptTemplate.from_template(
    "姓名：{name}，请帮我解释其含义"
)

# 模型的调用
model = ChatDeepSeek(model="deepseek-chat")

# 链的定义
chain = prompt_template | model | runnable |second_prompt | model | str_parser


for chunk in chain.stream(input={"last_name":"王健","spouse_name":"任怡雪","gender":"女儿"}):
    print(chunk,end="",flush=True)


