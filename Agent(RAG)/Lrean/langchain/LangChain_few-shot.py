# 通用提示词模板,few-shot思想，提供示例
# 基于FewShotPromptTemplate类实现

from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import FewShotPromptTemplate,PromptTemplate

# 示例模板
example_prompt = PromptTemplate.from_template("单词：{word}，反义词：{antonym}")

# 示例动态数据注入，要求是list内部套字典
examples_data = [
    {"word":"大","antonym":"小"},
    {"word":"长","antonym":"短"},
]

# 定义few-shot提示词模板
few_shot_template =FewShotPromptTemplate(
    example_prompt=example_prompt,     #示例模板
    examples = examples_data,         #示例列表
    prefix="告诉我单词的反义词，我提供如下的示例：",               #前缀
    suffix="基于以上示例，单词{input_word}的反义词是：",          #后缀
    input_variables=["input_word"],      #输入变量列表
)

prompt_text = few_shot_template.invoke({"input_word":"左"}).to_string()
print(prompt_text)

# 调用模型
model = ChatDeepSeek(model="deepseek-chat")

# 打印模型回复
print(model.invoke(input=prompt_text).content)






