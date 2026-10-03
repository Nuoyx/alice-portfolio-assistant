from langchain_core.tools import tool
from langchain_core.documents import Document
from rag.retriever import retrieve_documents


@tool
def search_portfolio_knowledge_tool(query: str, k: int = 4) -> list[Document]:
    """Retrieve semantically relevant passages from the portfolio's local knowledge base."""
    try:
        return retrieve_documents(query, k)
    except RuntimeError as err:
        return [Document(
            page_content="error: " + str(err)
        )]






