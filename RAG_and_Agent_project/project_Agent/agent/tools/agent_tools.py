
"""
智能体工具，用于执行智能体任务
"""
# 修正1: 移除未使用的 fetch_extensions 导入（langchain-community 已标记为弃用）
from langchain_core.tools import tool
from RAG.rag_service import RagSummarizerService
import random
import csv
from utils.config_handler import agent_conf
from utils.path_tool import get_abs_path
import os
from utils.logger_handler import logger


rag = RagSummarizerService()

# 用户ID池（用于模拟随机获取用户）
_USER_IDS = ["1001","1002","1003","1004","1005","1006","1007","1008","1009","1010","1011","1012","1013","1014","1015"]
# 月份池（用于模拟随机获取月份）
_MONTH_ARR = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]


external_data = {}

@tool(description="用于对文档进行总结，用户提问后，根据文档内容生成总结")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)

@tool(description="用于获取城市的天气，用户提问后，根据城市名称获取天气信息")
def get_weather(city: str) -> str:
    return f"{city}的天气是晴朗的，温度是25摄氏度"

@tool(description="获取用户所在城市的名称，以纯字符串的形式返回")
def get_user_city() -> str:
    return random.choice(["北京", "上海", "广州", "深圳", "成都", "西安"])

# 修正6: 函数名 get_user_city_id 误导（实际返回 user_id 而非 city_id），
#        改为 get_user_id 更准确
@tool(description="用于获取用户的ID，以纯字符串的形式返回")
def get_user_id() -> str:
    return random.choice(_USER_IDS)

@tool(description="用于获取当前月份，以纯字符串的形式返回")
def get_current_month() -> str:
    return random.choice(_MONTH_ARR)

def generate_external_data():
    if not external_data:
        external_data_path = get_abs_path(agent_conf["external_data_path"])
        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件不存在: {external_data_path}")

        # 修正2: 使用 csv.reader 正确解析 CSV（原代码手动 split(",") 无法处理双引号包裹的字段，
        #        导致 external_data 的键为 '"1001"'（带引号）而查询键为 '1001'（无引号），永远 KeyError）
        # 修正3: 直接迭代 csv.reader，避免 f.readlines() 一次性读入全部内存
        with open(external_data_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # 跳过标题行
            for row in reader:
                if len(row) < 6:
                    continue

                # 修正4: 局部变量 user_ids → uid（避免遮蔽全局 _USER_IDS 列表）
                #        局部变量 time → time_key（避免遮蔽标准库 time 模块名）
                uid: str = row[0].strip()
                feature: str = row[1].strip()
                efficiency: str = row[2].strip()
                consumable: str = row[3].strip()
                comparison: str = row[4].strip()
                time_key: str = row[5].strip()

                if uid not in external_data:
                    external_data[uid] = {}

                external_data[uid][time_key] = {
                    "特征": feature,
                    "效率": efficiency,
                    "消耗": consumable,
                    "比较": comparison,
                }


@tool(description="从外部系统中获取指定用户在指定月份的使用记录，以纯字符串的形式返回，如果没有获取到直接返回空字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    generate_external_data()

    try:
        return external_data[user_id][month]
    except KeyError:
        # 修正5: logger 中打印函数对象 → 改为有意义的描述字符串
        logger.warning(f"外部数据中没有用户{user_id}在{month}的使用记录")
        return ""

@tool(description="用于报告当前模型调用的提示切换")
def fill_content_for_report():
    return "fill_content_for_report已调用"

