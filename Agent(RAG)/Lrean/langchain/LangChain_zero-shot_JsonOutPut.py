# 通用提示词模板,zero-shot思想，不提供示例，只提供模板，基于PromptTemplate类实现
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import PromptTemplate
# JsonOutputParser是将数据解析为dict输出，字典输出
from langchain_core.output_parsers import JsonOutputParser,StrOutputParser

# 实现字符串解析器
str_parser = StrOutputParser()

#实现json格式解析器
json_parser = JsonOutputParser()

# 调用.format方法，将模板中的占位符替换为实际值
prompt_template = PromptTemplate.from_template(
    "{last_name}和他的妻子{spouse_name}，刚生了{gender}，并封装为JSON格式返回给我"
    "要求是key是name，value是刚起的名字。请严格遵守格式要求"
)

# 第二个提示词模板
second_prompt = PromptTemplate.from_template(
    "姓名：{name}，请帮我解释其含义"
)

model = ChatDeepSeek(model="deepseek-chat")

# 链的定义
chain = prompt_template | model | json_parser | second_prompt | model | str_parser


for chunk in chain.stream(input={"last_name":"王健","spouse_name":"任怡雪","gender":"女儿"}):
    print(chunk,end="",flush=True)
