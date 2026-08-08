import os,hashlib
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader,TextLoader


def get_file_md5_hex(filepath: str):         # 获取文件的md5值
    if not os.path.exists(filepath):
        logger.error(f"[md5计算]文件不存在: {filepath}")
        return
    if not os.path.isfile(filepath):
        logger.error(f"[md5计算]文件不是普通文件: {filepath}")
        return

    md5_obj = hashlib.md5()

    chunk_size = 4096               #规定分片大小 4KB
    try:
        with open(filepath,'rb') as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)

        md5_hex = md5_obj.hexdigest()
        return md5_hex

    except Exception as e:
        logger.error(f"[md5计算]文件{filepath}的md5值计算失败: {e}")
        return None


def listdir_with_allowed_type(path:str,allowed_types:tuple[str]):        # 列出目录下所有允许的文件类型
    files = []

    if not os.path.isdir(path):
        logger.error(f"[目录遍历]路径不是目录: {path}")
        # 修正1: 原代码 return allowed_types，将输入的扩展名元组返回给调用方，
        #        导致 vector_store.py 的 for path in allowed_file_paths 遍历字符串
        #        （如 '.pdf', '.txt'）而非文件路径，后续 get_file_md5_hex('.pdf') 会失败。
        #        应返回空列表，表示没有找到任何文件。
        return files

    for f in os.listdir(path):
        if f.endswith(allowed_types):
            files.append(os.path.join(path,f))

    # 修正2: 原代码 return tuple(files) 返回元组，但类型注解声明为 list[str]，
    #        改为返回列表以保持类型一致
    return files




def pdf_loader(filepath:str,password=None) -> list[Document]:
    return PyPDFLoader(filepath,password).load()



def txt_loader(filepath:str) -> list[Document]:        # 加载txt文件
    return TextLoader(filepath,encoding="utf-8").load()
