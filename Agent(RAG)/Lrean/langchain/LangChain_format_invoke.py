# format和invoke

from langchain_core.prompts import PromptTemplate  #通用提示词模板
from langchain_core.prompts import FewShotPromptTemplate  #零样本提示词模板
from langchain_core.prompts import ChatPromptTemplate  #聊天提示词模板


template = PromptTemplate.from_template("我的邻居是{neighbor},最喜欢的是{favorite}")

# format方法返回的是字符串
res = template.format(neighbor="张三",favorite="足球")
print(res,type(res))

# invoke方法返回的是PromptTemplate对象
res2 = template.invoke({"neighbor":"张三","favorite":"足球"})
print(res2,type(res2))



