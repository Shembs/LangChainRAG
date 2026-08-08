from rag import RagService
import streamlit as st
import config_data as config

# ── 页面配置 ─────────────────────────────────────────────
st.set_page_config(
    page_title="智能客服",
    page_icon=":material/support_agent:",
    layout="centered",
)

# ── 侧边栏 ───────────────────────────────────────────────
with st.sidebar:
    st.caption(":material/smart_toy: **智能客服助手**")
    st.caption("基于 RAG 的知识库问答系统")

    st.space("medium")

    with st.expander("会话信息", icon=":material/info:"):
        st.caption(f"当前会话 ID")
        st.code(config.session_config["configurable"]["session_id"], language=None)

    st.space("medium")

    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button(":material/delete: 清空对话", width="stretch"):
            st.session_state["message"] = [
                {"role": "assistant", "content": "你好，请问有什么可以帮助你的吗？"}
            ]
            st.rerun()
    with col_b:
        if st.button(":material/refresh: 刷新", width="stretch"):
            st.rerun()

    st.divider()
    st.caption("v1.0 · DeepSeek · DashScope")

# ── 标题 ─────────────────────────────────────────────────
with st.container(horizontal_alignment="center"):
    st.title(":material/support_agent: 智能客服", text_alignment="center")
    st.caption("有什么可以帮助你的吗？请随时提问", text_alignment="center")

st.space("small")

# ── 初始化 ───────────────────────────────────────────────
if "message" not in st.session_state:
    st.session_state["message"] = [
        {"role": "assistant", "content": "你好，请问有什么可以帮助你的吗？"}
    ]

if "rag_service" not in st.session_state:
    st.session_state["rag_service"] = RagService()

# ── 建议提问（仅在对话开始前显示）─────────────────────────
SUGGESTIONS = {
    ":material/help: 介绍一下你的功能": "介绍一下你的功能",
    ":material/search: 帮我搜索知识库": "帮我搜索知识库中的内容",
    ":material/description: 文档里有哪些内容": "帮我总结一下知识库中的主要内容",
    ":material/contact_support: 常见问题有哪些": "常见问题有哪些",
}

if len(st.session_state["message"]) <= 1:
    st.caption(":material/lightbulb: 试试以下问题：")
    selected = st.pills(
        "建议提问",
        list(SUGGESTIONS.keys()),
        label_visibility="collapsed",
    )
    if selected:
        # 将选中的问题作为待处理 prompt，rerun 后统一处理
        st.session_state["pending_prompt"] = SUGGESTIONS[selected]
        st.rerun()

# ── 显示历史消息 ─────────────────────────────────────────
for message in st.session_state["message"]:
    avatar = (
        ":material/person:"
        if message["role"] == "user"
        else ":material/smart_toy:"
    )
    with st.chat_message(message["role"], avatar=avatar):
        st.write(message["content"])

# ── 用户输入（来自 pills 或 chat_input）─────────────────
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")
else:
    prompt = st.chat_input(
        "请输入你的问题…",
        submit_mode="disable",
    )

if prompt:
    # 显示用户消息并保存
    with st.chat_message("user", avatar=":material/person:"):
        st.write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    # 获取并流式显示助手回复
    with st.chat_message("assistant", avatar=":material/smart_toy:"):
        with st.spinner("正在思考…"):
            res_stream = st.session_state["rag_service"].chain.stream(
                {"input": prompt},
                config.session_config,
            )
        full_response = st.write_stream(res_stream)

    # 保存完整回复
    st.session_state["message"].append(
        {"role": "assistant", "content": full_response}
    )
