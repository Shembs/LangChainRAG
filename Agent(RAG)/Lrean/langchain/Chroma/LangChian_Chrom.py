import os
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import CSVLoader
from langchain_openai import OpenAIEmbeddings


def main():
    # 使用 OpenAIEmbeddings 来调用 DeepSeek 的嵌入模型
    embedding = OpenAIEmbeddings(
        base_url="https://api.deepseek.com/v1",
        model="deepseek-embedding",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )

    vector_store = InMemoryVectorStore(
        embedding=embedding
    )

    loader = CSVLoader(

        file_path="../data/info.csv",
        encoding="utf-8",
        metadata_columns=["source"],
    )


    documents = loader.load()
    if len(documents) > 1:
        print(documents[1])
    else:
        print(f"文档数量不足，当前只有 {len(documents)} 条")

        # 向量存储的新增
    vector_store.add_documents(
        documents=documents,
        ids=[f"doc_{i}" for i in range(len(documents))]
    )

    # 删除
    vector_store.delete(["id1", "id2"])

    # 查询
    results = vector_store.similarity_search(
        query="股票代码是多少",
        k=1,
    )
    print(results)


if __name__ == "__main__":
    main()