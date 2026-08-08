# 调用官方API
# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

# 创建与大模型进行对话的客户端
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

# 与大模型进行交互
response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content": "你叫小新是一个温柔的AI助手，帮助用户解决问题"},
        {"role": "user", "content": "你好，你是谁"},
    ],
    stream=False,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}}
)

# 输出大模型返回的结果
print(response.choices[0].message.content)