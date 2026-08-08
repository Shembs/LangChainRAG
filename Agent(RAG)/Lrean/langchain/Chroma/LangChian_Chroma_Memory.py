from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import CSVLoader
from langchain_community.embeddings import DashScopeEmbeddings

vector_store = Chroma(
    collection_name="test",
    embedding_function=DashScopeEmbeddings(),
    persist_directory="../data/chroma_db",
)

loader = CSVLoader(
    file_path="../data/info.csv",
    encoding="utf-8",
    metadata_columns=["source"],
)

documents = loader.load()

# 向量存储的新增
vector_store.add_documents(
    documents=documents,
    ids=["id" + str(i) for i in range(1, len(documents) + 1)]
)
# 删除
vector_store.delete(["id1", "id2"])

# 查询
results = vector_store.similarity_search(
    "股票代码是多少",
    1
)

print(results)