from langchain_core.documents import Document
from utils.logger_handler import logger
from langchain_chroma import Chroma
from utils.config_handler import chroma_conf
from model.factory import embedding_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.path_tool import get_abs_path
from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex
import os


class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            persist_directory=chroma_conf["persist_directory"],
            embedding_function=embedding_model,
        )

        # 修正1: spliter → splitter（拼写错误）
        # 修正2: length_limit → length_function（RecursiveCharacterTextSplitter 的正确参数名是 length_function，
        #         传入 len 用于计算文本长度；length_limit 是无效参数，会导致 TypeError）
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})

    def load_document(self):
        """
        加载文档
        """

        def check_md5_hex(md5_for_check: str):
            # 修正3: 使用 with 语句创建空文件（原代码 open().close() 无法保证异常时关闭句柄）
            if not os.path.exists(get_abs_path(chroma_conf["md5_hex_store"])):
                with open(get_abs_path(chroma_conf["md5_hex_store"]), "w", encoding="utf-8") as _:
                    pass  # 仅创建空文件，不做写入
                return False
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "r", encoding="utf-8") as f:
                # 修正4: 直接迭代文件对象 f，而非 f.readlines()，
                #        避免将整个文件一次性读入内存，处理大文件时更高效
                for line in f:
                    line = line.strip()
                    if line == md5_for_check:
                        return True
                return False

        def save_md5_hex(md5_for_check: str):
            # 修正5: 原代码以读模式 "r" 打开文件却尝试 f.write()，
            #        会抛出 io.UnsupportedOperation 异常。改为追加模式 "a"，
            #        并在写入后添加换行符，保证每条 md5 记录独占一行
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")

        def get_file_documents(read_file: str):
            if read_file.endswith("txt"):
                return txt_loader(read_file)
            if read_file.endswith("pdf"):
                return pdf_loader(read_file)
            return []

        allowed_file_paths: list[str] = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"]),
        )

        for path in allowed_file_paths:
            # 计算文件的md5值
            md5_hex = get_file_md5_hex(path)

            if check_md5_hex(md5_hex):
                logger.info(f"[文件加载]文件{path}已加载,跳过")
                continue

            try:
                documents: list[Document] = get_file_documents(path)

                if not documents:
                    logger.warning(f"[文件加载]文件{path}加载失败,跳过")
                    continue

                split_documents: list[Document] = self.splitter.split_documents(documents)

                if not split_documents:
                    logger.warning(f"[文件加载]文件{path}分片失败,跳过")
                    continue

                self.vector_store.add_documents(split_documents)

                save_md5_hex(md5_hex)

                logger.info(f"[文件加载]文件{path}加载成功")

            except Exception as e:
                logger.error(f"[文件加载]文件{path}加载失败: {e}", exc_info=True)
                continue


if __name__ == '__main__':
    vs = VectorStoreService()
    vs.load_document()

    retriever = vs.get_retriever()

    res = retriever.invoke("迷路")

    for r in res:
        print(r.page_content)
        print("="*50)
