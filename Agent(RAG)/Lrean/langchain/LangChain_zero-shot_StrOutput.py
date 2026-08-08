# 通用提示词模板,zero-shot思想，不提供示例，只提供模板，基于PromptTemplate类实现
from langchain_core.messages import AIMessage
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import PromptTemplate
# strouputparser是字符串解析器
from langchain_core.output_parsers import StrOutputParser

# 实现字符串解析器
parser = StrOutputParser()

# 调用.format方法，将模板中的占位符替换为实际值
prompt_template = PromptTemplate.from_template(
    "{last_name}和他的妻子{spouse_name}，刚生了{gender}，你帮我起一个名字，简单回答"
)
# prompt_text = prompt_template.format(last_name="张三",gender="女孩")
# print(prompt_text)

model = ChatDeepSeek(model="deepseek-chat")
# res = model.invoke(input=prompt_text)
# print(res.content)

# 链的定义
chain = prompt_template | model | parser | model


res:AIMessage = chain.invoke(input={"last_name":"王健","spouse_name":"任怡雪","gender":"女儿"})

print(res.content)
