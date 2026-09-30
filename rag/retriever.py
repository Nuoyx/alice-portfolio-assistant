from langchain_core.documents import Document

from rag.vector_store import create_vector_store


def retrieve_documents(query: str, k: int = 4) -> list[Document]:
    vector_store = create_vector_store()

    return vector_store.similarity_search(
        query,
        k=k,
    )

if __name__ == "__main__":
    documents = retrieve_documents(
        "What technologies does my Food To Eat project use?"
    )

    for document in documents:
        print("=" * 80)
        print(document.page_content)
        print(document.metadata)

