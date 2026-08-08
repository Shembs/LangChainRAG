import streamlit as st

# 设置页面的配置项
st.set_page_config(
    page_title="StreamlitAISpeak",
    page_icon="🧊",
    # 网页布局
    layout="wide",
    # 侧边栏状态
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# 这是一个Streamlit AI Speak页面!"
    }
)

# 大标题
st.title("Streamlit AIspeak")
st.header("Streamlit AIspeak,一级")
st.subheader("Streamlit AIspeak，二级")

# 段落文字
st.write("Hello World")

# 图片
st.image("../AIspeak/Image/01.png")

# 音频
# st.audio() # 引入音频

# 视频
# st.video() # 引入视频

# logo
st.logo("../AIspeak/Image/02.png")

# 表格
student_data = {
    "姓名": ["王林","抽象","水泥","卡死"],
    "学号":["223101","223102","223103","223104"],
    "总分":["270","255","284","287"]
}
st.table(student_data)

# 输入框
name = st.text_input("请输入姓名")
st.write(f"姓名是：{name}")

# 输入密码（type设置password）
password = st.text_input("请输入密码",type="password")
st.write(f"密码是：{password}")

# 单选按钮
gander = st.radio("请输入您的性别",["男","女","不愿透露"],index=2)
st.write(f"性别为:{gander}")
