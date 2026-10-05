from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore"


def create_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2",
    )


def create_vector_store() -> Chroma:
    embeddings = create_embeddings()

    return Chroma(
        collection_name="portfolio",
        embedding_function=embeddings,
        persist_directory=str(VECTORSTORE_DIR),
    )


