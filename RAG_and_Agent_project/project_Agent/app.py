"""
扫地机器人智能助手 — Streamlit 前端（美化版）

基于 ReAct Agent 的对话式助手，支持流式输出和多轮对话。
- 淡色主题 UI
- 侧边栏：知识库上传管理 + 默认快捷问题
- 知识库无匹配时自动回退到 AI 大模型回答

运行方式: streamlit run app.py
"""

from datetime import datetime
from pathlib import Path
from typing import Generator

import streamlit as st

from agent.react_agent import ReactAgent
from utils.kb_upload import (
    save_uploaded_file,
    refresh_knowledge_base,
    get_kb_file_list,
)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
PAGE_TITLE: str = "🤖 扫地机器人智能客服"
PAGE_ICON: str = "🤖"
ASSISTANT_AVATAR: str = "🤖"
USER_AVATAR: str = "👤"
LOADING_TEXT: str = "智能客服思考中……"

# Session state 键名
KEY_AGENT: str = "agent"
KEY_MESSAGES: str = "messages"
KEY_PENDING_QUESTION: str = "pending_question"
KEY_UPLOAD_STATUS: str = "upload_status"

# 预设快捷问题
DEFAULT_QUESTIONS: list[dict[str, str]] = [
    {"icon": "🧹", "label": "扫地机器人如何保养？", "question": "扫地机器人在日常使用中应该如何保养和维护？"},
    {"icon": "🏠", "label": "小户型选什么机器人？", "question": "小户型适合哪种扫地机器人？有什么推荐？"},
    {"icon": "🔧", "label": "常见故障怎么排查？", "question": "扫地机器人常见故障有哪些？怎么排查和解决？"},
    {"icon": "🛒", "label": "如何选购扫地机器人？", "question": "选购扫地机器人时应该关注哪些参数和功能？"},
    {"icon": "🔋", "label": "电池不耐用怎么办？", "question": "扫地机器人电池不耐用了怎么办？如何延长电池寿命？"},
    {"icon": "🌧️", "label": "潮湿环境能用吗？", "question": "在南方潮湿地区使用扫地机器人需要注意什么？"},
]

# ---------------------------------------------------------------------------
# 自定义 CSS — 淡色主题
# ---------------------------------------------------------------------------
CUSTOM_CSS: str = """
<style>
    /* ===== 全局 ===== */
    .stApp {
        background-color: #F5F6FA;
    }

    /* ===== 侧边栏 ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E8F0FE 0%, #F0F4FA 100%);
        border-right: 1px solid #DEE5ED;
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #2C3E50;
        font-weight: 700;
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #34495E;
        font-weight: 600;
        font-size: 0.95rem;
        margin-top: 1rem;
    }

    /* 侧边栏按钮 */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #D6E4F0;
        background: #FFFFFF;
        color: #2C3E50;
        font-size: 0.85rem;
        padding: 0.5rem 0.75rem;
        transition: all 0.2s ease;
        text-align: left;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #D6EAF8;
        border-color: #85C1E9;
        transform: translateX(2px);
    }
    [data-testid="stSidebar"] .stButton > button:active {
        background: #AED6F1;
    }

    /* 侧边栏上传区域 */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        padding: 0.5rem 0;
    }

    /* 侧边栏分割线 */
    [data-testid="stSidebar"] hr {
        border-color: #D6E4F0;
        margin: 1rem 0;
    }

    /* ===== 主聊天区 ===== */
    .main-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .main-header h1 {
        color: #2C3E50;
        font-weight: 700;
        font-size: 2rem;
        margin-bottom: 0.25rem;
    }
    .main-header p {
        color: #7F8C8D;
        font-size: 0.9rem;
    }

    /* 聊天消息容器 */
    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    /* 聊天输入框 */
    [data-testid="stChatInput"] textarea {
        border-radius: 12px !important;
        border: 1px solid #D6E4F0 !important;
        background: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #85C1E9 !important;
        box-shadow: 0 2px 12px rgba(133,193,233,0.25) !important;
    }

    /* ===== 欢迎页面卡片 ===== */
    .welcome-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        margin: 2rem auto;
        max-width: 600px;
    }
    .welcome-card .icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .welcome-card h2 {
        color: #2C3E50;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .welcome-card p {
        color: #7F8C8D;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    .welcome-card .hint-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
        margin-top: 1.5rem;
    }
    .welcome-card .hint-chip {
        background: #EBF5FB;
        color: #2980B9;
        border-radius: 20px;
        padding: 0.35rem 0.9rem;
        font-size: 0.8rem;
        border: 1px solid #D6EAF8;
    }

    /* ===== 自定义 toasts ===== */
    .upload-toast {
        padding: 0.75rem 1rem;
        border-radius: 10px;
        font-size: 0.85rem;
        margin: 0.5rem 0;
    }
    .upload-toast.success {
        background: #D5F5E3;
        color: #1E8449;
        border: 1px solid #A9DFBF;
    }
    .upload-toast.error {
        background: #FADBD8;
        color: #C0392B;
        border: 1px solid #F1948A;
    }

    /* ===== 页脚 ===== */
    .sidebar-footer {
        position: fixed;
        bottom: 0;
        padding: 1rem;
        font-size: 0.75rem;
        color: #95A5A6;
        text-align: center;
        width: calc(var(--sidebar-width) - 2rem);
    }

    /* ===== 滚动条 ===== */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #CBD5E0; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #A0AEC0; }
</style>
"""

# ---------------------------------------------------------------------------
# 页面配置
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# 注入自定义 CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------
def stream_with_cache(
    generator: Generator[str, None, None],
    cache: list[str],
) -> Generator[str, None, None]:
    """流式传递生成器内容，同时将每个 chunk 缓存到列表中。"""
    for chunk in generator:
        cache.append(chunk)
        yield chunk


def handle_default_question(question: str) -> None:
    """Callback：将预设问题写入 session state，触发聊天处理。"""
    st.session_state[KEY_PENDING_QUESTION] = question


def clear_chat_history() -> None:
    """Callback：清空聊天记录。"""
    st.session_state[KEY_MESSAGES] = []


def get_file_icon(filename: str) -> str:
    """根据文件扩展名返回对应图标。"""
    ext = Path(filename).suffix.lower()
    icons = {".txt": "📄", ".pdf": "📕", ".docx": "📘"}
    return icons.get(ext, "📎")


# ---------------------------------------------------------------------------
# Session State 初始化
# ---------------------------------------------------------------------------
if KEY_AGENT not in st.session_state:
    st.session_state[KEY_AGENT] = ReactAgent()

if KEY_MESSAGES not in st.session_state:
    st.session_state[KEY_MESSAGES] = []

if KEY_PENDING_QUESTION not in st.session_state:
    st.session_state[KEY_PENDING_QUESTION] = None

if KEY_UPLOAD_STATUS not in st.session_state:
    st.session_state[KEY_UPLOAD_STATUS] = None


# ===========================================================================
# 侧边栏
# ===========================================================================
with st.sidebar:
    # ---- Logo / 标题 ----
    st.markdown(
        '<div style="text-align:center;padding:0.5rem 0 1rem 0;">'
        '<span style="font-size:2.5rem;">🤖</span>'
        '<h2 style="margin:0.25rem 0;color:#2C3E50;">智能客服助手</h2>'
        '<p style="font-size:0.8rem;color:#7F8C8D;">扫地机器人 · 专业知识库</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ---- 知识库管理（可折叠） ----
    with st.expander("📚 知识库管理", expanded=True):
        uploaded_files = st.file_uploader(
            "上传知识文档（支持 .txt / .pdf / .docx）",
            type=["txt", "pdf", "docx"],
            accept_multiple_files=True,
            help="上传文件将自动保存到 data/ 目录，并触发向量库增量索引",
            key="kb_uploader",
        )

        if uploaded_files:
            saved_count = 0
            for uf in uploaded_files:
                saved_path = save_uploaded_file(uf)
                if saved_path:
                    saved_count += 1

            if saved_count > 0:
                # 触发向量库增量索引
                result = refresh_knowledge_base()
                if result["success"]:
                    st.session_state[KEY_UPLOAD_STATUS] = {
                        "type": "success",
                        "msg": f"✅ 已上传 {saved_count} 个文件，知识库索引已更新",
                    }
                else:
                    st.session_state[KEY_UPLOAD_STATUS] = {
                        "type": "error",
                        "msg": f"⚠️ 文件已保存但索引更新失败: {result['message']}",
                    }
            else:
                st.session_state[KEY_UPLOAD_STATUS] = {
                    "type": "error",
                    "msg": "❌ 文件上传失败，请检查文件类型是否为 .txt / .pdf / .docx",
                }

            # 清除上传器状态，避免重复处理
            st.rerun()

        # 显示上传状态
        upload_status = st.session_state.get(KEY_UPLOAD_STATUS)
        if upload_status:
            css_class = "success" if upload_status["type"] == "success" else "error"
            st.markdown(
                f'<div class="upload-toast {css_class}">{upload_status["msg"]}</div>',
                unsafe_allow_html=True,
            )
            # 显示一次后清除
            st.session_state[KEY_UPLOAD_STATUS] = None

        # 已上传文件列表
        kb_files = get_kb_file_list()
        if kb_files:
            with st.expander(f"📋 已上传文件（{len(kb_files)}）", expanded=False):
                for f in kb_files:
                    st.markdown(
                        f'{get_file_icon(f["name"])} `{f["name"]}` '
                        f'<span style="color:#95A5A6;font-size:0.75rem;">({f["size_kb"]} KB)</span>',
                        unsafe_allow_html=True,
                    )
        else:
            st.caption("📭 暂无已上传文件")

    # ---- 快捷提问（可折叠） ----
    with st.expander("💬 快捷提问", expanded=True):
        for item in DEFAULT_QUESTIONS:
            st.button(
                f'{item["icon"]}  {item["label"]}',
                key=f"default_q_{item['label']}",
                on_click=handle_default_question,
                args=(item["question"],),
                use_container_width=True,
            )

    # ---- 操作区（可折叠） ----
    with st.expander("⚙️ 操作", expanded=True):
        st.button(
            "🗑️  清空对话",
            key="clear_chat",
            on_click=clear_chat_history,
            use_container_width=True,
        )

    # ---- 底部信息 ----
    st.divider()
    st.markdown(
        '<div style="font-size:0.72rem;color:#AAB7C4;text-align:center;padding:0.5rem 0;">'
        '🧠 ReAct Agent + RAG<br>'
        'DeepSeek · ChromaDB · LangChain<br>'
        '<span style="font-size:0.65rem;">v2.0 </span>'
        '</div>',
        unsafe_allow_html=True,
    )


# ===========================================================================
# 主界面
# ===========================================================================

# ---- 页面标题 ----
st.markdown(
    '<div class="main-header">'
    '<h1>🤖 扫地机器人智能客服</h1>'
    '<p>基于 ReAct Agent 的对话式助手 · 专业扫地机器人知识库 · 流式实时回复</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ---- 欢迎界面（无消息时显示） ----
if not st.session_state[KEY_MESSAGES]:
    st.markdown(
        '<div class="welcome-card">'
        '<div class="icon">🏠</div>'
        '<h2>欢迎使用智能客服助手</h2>'
        '<p>我是您的专属扫地机器人客服助手，可以帮您解答<br>'
        '选购、使用、保养、故障排查等各类问题。</p>'
        '<div class="hint-row">'
        + "".join(
            f'<span class="hint-chip">{q["icon"]} {q["label"]}</span>'
            for q in DEFAULT_QUESTIONS[:4]
        )
        + '</div>'
        '<p style="margin-top:1rem;font-size:0.8rem;color:#AAB7C4;">'
        '👈 也可以在左侧边栏中点击快捷问题，或直接在下方输入您的问题</p>'
        '</div>',
        unsafe_allow_html=True,
    )

# ---- 渲染历史消息 ----
for msg in st.session_state[KEY_MESSAGES]:
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        st.write(msg["content"])
        if msg.get("timestamp"):
            st.caption(msg["timestamp"])

# ---- 聊天输入框 ----
user_input: str | None = st.chat_input(
    placeholder="请输入您的扫地机器人相关问题……",
)

# ---- 处理预设问题（通过 callback 设置的 pending_question） ----
if st.session_state.get(KEY_PENDING_QUESTION):
    user_input = st.session_state[KEY_PENDING_QUESTION]
    st.session_state[KEY_PENDING_QUESTION] = None


# ---- 用户输入处理 ----
if user_input:
    now_str = datetime.now().strftime("%H:%M")

    # 显示并保存用户消息
    with st.chat_message("user", avatar=USER_AVATAR):
        st.write(user_input)
        st.caption(now_str)
    st.session_state[KEY_MESSAGES].append(
        {
            "role": "user",
            "content": user_input,
            "avatar": USER_AVATAR,
            "timestamp": now_str,
        }
    )

    response_chunks: list[str] = []

    with st.spinner(LOADING_TEXT):
        try:
            response_stream = st.session_state[KEY_AGENT].execute_stream(user_input)
            with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
                st.write_stream(
                    stream_with_cache(response_stream, response_chunks)
                )
        except Exception as exc:
            error_msg = f"❌ 处理请求时出错: {exc}"
            st.error(error_msg)
            st.session_state[KEY_MESSAGES].append(
                {
                    "role": "assistant",
                    "content": error_msg,
                    "avatar": ASSISTANT_AVATAR,
                    "timestamp": now_str,
                }
            )
        else:
            full_response = "".join(response_chunks) if response_chunks else ""
            if full_response.strip():
                st.session_state[KEY_MESSAGES].append(
                    {
                        "role": "assistant",
                        "content": full_response,
                        "avatar": ASSISTANT_AVATAR,
                        "timestamp": now_str,
                    }
                )
            st.rerun()
