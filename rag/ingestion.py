from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.vector_store import create_vector_store

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_documents():
    print(DATA_DIR)
    documents = []
    for path in DATA_DIR.rglob("*"):
        print(path)
        if path.suffix.lower() not in {".md", ".json"}:
            continue
        documents.append(
            Document(
                page_content=path.read_text(encoding="utf-8"),
                metadata={"source": str(path)},
            )
        )

    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )

    return splitter.split_documents(documents)


def ingest_documents():
    documents = load_documents()

    if not documents:
        print("No documents found.")
        return

    chunks = split_documents(documents)

    vector_store = create_vector_store()
    vector_store.add_documents(chunks)

    print(f"Loaded {len(documents)} documents.")
    print(f"Created {len(chunks)} chunks.")


if __name__ == "__main__":
    ingest_documents()

