"""
扫地机器人智能助手 — Streamlit 前端（美化版）

基于 ReAct Agent 的对话式助手，支持流式输出和多轮对话。
- 淡色主题 UI
- 侧边栏：多会话管理（新增 / 删除 / 切换）+ 默认快捷问题
- 知识库无匹配时自动回退到 AI 大模型回答
- 知识库上传与模型调整已移至后台管理界面（admin_frontend + admin_server）

运行方式: streamlit run app.py
"""

import json
import os
import uuid
from datetime import datetime
from typing import Generator

import streamlit as st

from agent.react_agent import ReactAgent
from utils.path_tool import get_abs_path

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
KEY_CONVERSATIONS: str = "conversations"
KEY_CURRENT_ID: str = "current_conv_id"
KEY_PENDING_QUESTION: str = "pending_question"

# 会话持久化路径
CHAT_HISTORY_DIR: str = get_abs_path("chat_history")
CHAT_HISTORY_FILE: str = os.path.join(CHAT_HISTORY_DIR, "conversations.json")

# 会话标题最大长度
_TITLE_MAX_LEN: int = 16

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
        background: linear-gradient(180deg, #1E2A45 0%, #26344F 100%);
        border-right: 1px solid #33405E;
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #FFFFFF;
        font-weight: 700;
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #E8EDF5;
        font-weight: 600;
        font-size: 0.95rem;
        margin-top: 1rem;
    }

    /* 侧边栏按钮 */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #3A4A6E;
        background: #2A3A5C;
        color: #E8EDF5;
        font-size: 0.85rem;
        padding: 0.5rem 0.75rem;
        transition: all 0.2s ease;
        text-align: left;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #33456B;
        border-color: #5B78A8;
        transform: translateX(2px);
    }
    [data-testid="stSidebar"] .stButton > button:active {
        background: #3D517A;
    }

    /* 侧边栏分割线 */
    [data-testid="stSidebar"] hr {
        border-color: #3A4A6E;
        margin: 1rem 0;
    }

    /* 侧边栏内联代码（如文件名） */
    [data-testid="stSidebar"] code {
        color: #D6E0F0;
        background-color: #33405E;
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

    /* ===== 页脚 ===== */
    .sidebar-footer {
        position: fixed;
        bottom: 0;
        padding: 1rem;
        font-size: 0.75rem;
        color: #9FB0CC;
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


# ---------------------------------------------------------------------------
# 会话管理
# ---------------------------------------------------------------------------
def _new_conversation() -> dict:
    return {
        "id": uuid.uuid4().hex,
        "title": "新对话",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "messages": [],
    }


def _conv_title(conv: dict) -> str:
    """根据会话首条用户消息生成标题，无消息时返回「新对话」。"""
    for msg in conv.get("messages", []):
        if msg.get("role") == "user":
            text = msg.get("content", "").strip().replace("\n", " ")
            return text[:_TITLE_MAX_LEN] + ("…" if len(text) > _TITLE_MAX_LEN else "")
    return "新对话"


def _load_conversations() -> list[dict]:
    if not os.path.isfile(CHAT_HISTORY_FILE):
        return []
    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_conversations() -> None:
    os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state[KEY_CONVERSATIONS], f, ensure_ascii=False, indent=2)


def new_conversation() -> None:
    """Callback：新增一个空会话并切换为当前会话。"""
    conv = _new_conversation()
    st.session_state[KEY_CONVERSATIONS].insert(0, conv)
    st.session_state[KEY_CURRENT_ID] = conv["id"]
    _save_conversations()


def delete_conversation(conv_id: str) -> None:
    """删除指定会话；若删除后无会话则自动补建一个空会话。"""
    convs = st.session_state[KEY_CONVERSATIONS]
    convs[:] = [c for c in convs if c["id"] != conv_id]
    if not convs:
        convs.append(_new_conversation())
    st.session_state[KEY_CURRENT_ID] = convs[0]["id"]
    _save_conversations()


def get_current_conversation() -> dict:
    """返回当前选中的会话。"""
    convs = st.session_state[KEY_CONVERSATIONS]
    cid = st.session_state[KEY_CURRENT_ID]
    for c in convs:
        if c["id"] == cid:
            return c
    return convs[0]


@st.dialog("删除会话")
def confirm_delete_dialog(conv_id: str):
    """删除会话前的二次确认对话框。"""
    target = next((c for c in st.session_state[KEY_CONVERSATIONS] if c["id"] == conv_id), None)
    title = _conv_title(target) if target else "当前会话"
    st.write(f"确认删除会话「{title}」吗？删除后聊天记录不可恢复。")

    col1, col2 = st.columns(2)
    if col1.button("确认删除", type="primary", use_container_width=True):
        delete_conversation(conv_id)
        st.rerun()
    if col2.button("取消", use_container_width=True):
        st.rerun()


# ---------------------------------------------------------------------------
# Session State 初始化
# ---------------------------------------------------------------------------
if KEY_AGENT not in st.session_state:
    st.session_state[KEY_AGENT] = ReactAgent()

if KEY_CONVERSATIONS not in st.session_state:
    st.session_state[KEY_CONVERSATIONS] = _load_conversations()
    if not st.session_state[KEY_CONVERSATIONS]:
        st.session_state[KEY_CONVERSATIONS] = [_new_conversation()]

if KEY_CURRENT_ID not in st.session_state:
    st.session_state[KEY_CURRENT_ID] = st.session_state[KEY_CONVERSATIONS][0]["id"]

if KEY_PENDING_QUESTION not in st.session_state:
    st.session_state[KEY_PENDING_QUESTION] = None


# ===========================================================================
# 侧边栏
# ===========================================================================
with st.sidebar:
    # ---- Logo / 标题 ----
    st.markdown(
        '<div style="text-align:center;padding:0.5rem 0 1rem 0;">'
        '<span style="font-size:2.5rem;">🤖</span>'
        '<h2 style="margin:0.25rem 0;color:#FFFFFF;">智能客服助手</h2>'
        '<p style="font-size:0.8rem;color:#B8C6DC;">扫地机器人 · 专业知识库</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ---- 会话管理（可折叠） ----
    with st.expander("💬 会话", expanded=True):
        st.button(
            "➕  新增对话",
            key="new_conversation",
            on_click=new_conversation,
            use_container_width=True,
        )

        conversations = st.session_state[KEY_CONVERSATIONS]
        option_ids = [c["id"] for c in conversations]
        # 若当前 id 不在列表中（理论上不会发生），回退到第一个会话
        if st.session_state[KEY_CURRENT_ID] not in option_ids:
            st.session_state[KEY_CURRENT_ID] = option_ids[0]

        # 单选按钮直接绑定到当前会话 id，切换即更新 KEY_CURRENT_ID
        st.radio(
            "选择会话",
            options=option_ids,
            format_func=lambda cid: _conv_title(
                next(c for c in conversations if c["id"] == cid)
            ),
            label_visibility="collapsed",
            key=KEY_CURRENT_ID,
        )

        if st.button(
            "🗑️  删除当前会话",
            key="delete_conversation",
            use_container_width=True,
        ):
            confirm_delete_dialog(st.session_state[KEY_CURRENT_ID])

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

    # ---- 底部信息 ----
    st.divider()
    st.markdown(
        '<div style="font-size:0.72rem;color:#8EA0BE;text-align:center;padding:0.5rem 0;">'
        '🧠 ReAct Agent + RAG<br>'
        'DeepSeek · ChromaDB · LangChain<br>'
        '<span style="font-size:0.65rem;">v2.0 </span>'
        '</div>',
        unsafe_allow_html=True,
    )


# ===========================================================================
# 主界面
# ===========================================================================
current_conv = get_current_conversation()
current_messages: list[dict] = current_conv["messages"]

# ---- 页面标题 ----
st.markdown(
    '<div class="main-header">'
    '<h1>🤖 扫地机器人智能客服</h1>'
    '<p>基于 ReAct Agent 的对话式助手 · 专业扫地机器人知识库 · 流式实时回复</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ---- 欢迎界面（无消息时显示） ----
if not current_messages:
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
for msg in current_messages:
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
    current_messages.append(
        {
            "role": "user",
            "content": user_input,
            "avatar": USER_AVATAR,
            "timestamp": now_str,
        }
    )

    # 首次提问时自动更新会话标题
    if current_conv["title"] == "新对话":
        current_conv["title"] = _conv_title(current_conv)

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
            current_messages.append(
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
                current_messages.append(
                    {
                        "role": "assistant",
                        "content": full_response,
                        "avatar": ASSISTANT_AVATAR,
                        "timestamp": now_str,
                    }
                )
            _save_conversations()
            st.rerun()
