"""
加载prompt模板文件

注意：所有 load_*_prompt() 函数使用 with 语句打开文件，
确保文件句柄在使用完毕后自动关闭，避免资源泄漏。
返回值为字符串类型，可直接作为 prompt 内容使用。
"""

from utils.config_handler import prompts_conf
from utils.path_tool import get_abs_path
from utils.logger_handler import logger


def load_system_prompts():
    """加载系统提示模板

    Returns:
        str: 系统提示文本内容
    """
    try:
        system_prompt_path = get_abs_path(prompts_conf["main_prompt_path"])
    except KeyError as e:
        logger.error(f"配置文件中缺少{e}")
        raise e

    try:
        # 使用 with 语句打开文件：读取完成后自动关闭文件句柄，防止资源泄漏
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"加载系统提示模板失败: {e}")
        raise e


def load_rag_prompts():
    """加载RAG提示模板

    Returns:
        str: RAG提示文本内容
    """
    try:
        rag_prompt_path = get_abs_path(prompts_conf["rag_prompt_path"])
    except KeyError as e:
        logger.error(f"配置文件中缺少{e}")
        raise e

    try:
        with open(rag_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"加载RAG提示模板失败: {e}")
        raise e


def load_report_prompts():
    """加载报告提示模板

    Returns:
        str: 报告提示文本内容
    """
    try:
        report_prompt_path = get_abs_path(prompts_conf["report_prompt_path"])
    except KeyError as e:
        logger.error(f"配置文件中缺少{e}")
        raise e

    try:
        with open(report_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"加载报告提示模板失败: {e}")
        raise e


if __name__ == '__main__':
    print(load_rag_prompts())
