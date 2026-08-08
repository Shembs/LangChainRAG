# 导入必要的库
import streamlit as st
import os
from models_config import (
    PROVIDERS,
    get_provider_list,
    get_provider_display_map,
    get_models_by_provider,
    create_client,
    get_extra_params,
)


# 页面的基础配置
st.set_page_config(
    page_title="AI聊天助手",
    page_icon=":😺",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

# 大标题
st.title("AI聊天助手")

# logo
st.logo("Image/logo.png")

# ==================== 侧边栏区域 ====================
with st.sidebar:
    st.title("⚙️ 设置面板")

    # ---- 侧边栏：模型提供商选择 ----
    provider_list = get_provider_list()
    display_map = get_provider_display_map()
    selected_provider = st.selectbox(
        "选择模型提供商",
        options=provider_list,
        format_func=lambda pid: display_map[pid],
        index=0,
        help="选择要使用的AI模型提供商"
    )

    # ---- 侧边栏：该提供商下的模型选择 ----
    models = get_models_by_provider(selected_provider)
    model_name = st.selectbox(
        "选择模型",
        options=models,
        index=0,
        help="选择要调用的AI模型"
    )

    # ---- 侧边栏：API Key 状态提示 ----
    api_key_env = PROVIDERS[selected_provider]["api_key_env"]
    api_key = os.environ.get(api_key_env)
    if api_key:
        st.success(f"✅ {api_key_env} 已配置")
    else:
        st.error(f"❌ 未检测到 {api_key_env}，请设置环境变量")

    # ---- 侧边栏：Temperature 参数 ----
    temperature = st.slider(
        "Temperature (创造性)",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="值越高，回答越有创造性；值越低，回答越稳定"
    )

    # ---- 侧边栏：自定义系统提示词 ----
    system_prompt = st.text_area(
        "系统提示词",
        value="你叫小新是一个温柔的AI助手，帮助用户解决问题",
        height=120,
        help="定义AI助手的角色和行为"
    )

    # ---- 侧边栏：清空聊天记录 ----
    st.divider()
    if st.button("🗑️ 清空聊天记录", use_container_width=True):
        st.session_state.message = []
        st.rerun()

    # ---- 侧边栏：关于信息 ----
    st.divider()
    st.caption(f"当前提供商: {display_map[selected_provider]}")
    st.caption("AI聊天助手 v2.0")

# ==================== 侧边栏区域结束 ====================


# 初始化聊天记录
if "message" not in st.session_state:
    st.session_state.message = []

# 展示聊天记录
for message in st.session_state.message:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    elif message["role"] == "assistant":
        st.chat_message("assistant").write(message["content"])

# 聊天输入框
prompt = st.chat_input("您想问的问题是：")
if prompt:
    # 检查 API Key 是否已配置
    if not api_key:
        st.error(f"请先设置环境变量 `{api_key_env}` 后再使用 {display_map[selected_provider]} 的模型。")
        st.stop()

    st.chat_message("user").write(prompt)
    print("----------------->这是调用AI模型的代码", prompt)

    # 添加用户消息到聊天记录
    st.session_state.message.append({"role": "user", "content": prompt})

    # 根据选中的提供商动态创建客户端
    client = create_client(selected_provider)

    # 获取该提供商的额外参数
    extra_params = get_extra_params(selected_provider)

    # 构建 API 调用参数
    api_kwargs = {
        "model": model_name,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            *st.session_state.message
        ],
        "stream": True,
    }

    # 合并提供商特有的额外参数（如 DeepSeek 的 thinking）
    api_kwargs.update(extra_params)

    print("调用参数:", {k: v for k, v in api_kwargs.items() if k != "messages"})

    # 调用AI模型
    response = client.chat.completions.create(**api_kwargs)

    # 流式输出
    response_message = st.empty()

    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    # 添加助手消息到聊天记录
    st.session_state.message.append({"role": "assistant", "content": full_response})