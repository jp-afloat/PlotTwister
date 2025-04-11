from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Document
from llama_index.core.query_engine import RetrieverQueryEngine

def build_index_from_docs(docs: list[dict]) -> RetrieverQueryEngine:
    documents = [Document(text=str(doc)) for doc in docs]
    index = VectorStoreIndex.from_documents(documents)
    return index.as_query_engine()
