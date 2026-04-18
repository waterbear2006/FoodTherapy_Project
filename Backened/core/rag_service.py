import logging
from pathlib import Path
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DB_DIR = BASE_DIR / "tcm_chroma_db"
MODEL_NAME = "BAAI/bge-small-zh-v1.5"

# Global instances (Singleton-like behavior when module is loaded)
embeddings = None
vectorstore = None

def _init_rag_system():
    """Initialize the embedding model and vector store."""
    global embeddings, vectorstore
    try:
        if embeddings is None:
            model_kwargs = {'device': 'cpu'}
            encode_kwargs = {'normalize_embeddings': True}
            embeddings = HuggingFaceBgeEmbeddings(
                model_name=MODEL_NAME,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
        
        if vectorstore is None:
            if not CHROMA_DB_DIR.exists():
                logger.warning(f"Chroma DB directory not found at {CHROMA_DB_DIR}. Ensure init_vector_db.py ran successfully.")
            else:
                vectorstore = Chroma(
                    persist_directory=str(CHROMA_DB_DIR),
                    embedding_function=embeddings
                )
                logger.info("RAG vector store initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")

# Initialize upon module load
_init_rag_system()

def retrieve_tcm_knowledge(query: str, top_k: int = 3, doc_type: str = None) -> str:
    """
    Retrieve Traditional Chinese Medicine knowledge from the local vector database.
    
    Args:
        query: The search query string (e.g. current season, symptoms, etc.).
        top_k: Number of reference documents to retrieve.
        doc_type: Optional filter ('recipe' or 'herb').
        
    Returns:
        A formatted string of relevant context with numbered references.
        Returns empty string if unavailable or on error.
    """
    if not vectorstore:
        logger.warning("RAG Vectorstore is not initialized, skipping knowledge retrieval.")
        return ""
        
    if not query.strip():
        return ""
        
    try:
        search_kwargs = {"k": top_k}
        if doc_type:
            # ChromaDB metadata filter format
            search_kwargs["filter"] = {"doc_type": doc_type}
            
        docs = vectorstore.similarity_search(query, **search_kwargs)
        
        if not docs:
            return ""
            
        formatted_results = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content.strip()
            formatted_results.append(f"[{i}] {content}")
            
        return "\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"Error during TCM knowledge retrieval step: {e}")
        return ""
