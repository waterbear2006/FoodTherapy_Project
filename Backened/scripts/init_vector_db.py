import os
import json
import shutil
from pathlib import Path
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DB_DIR = BASE_DIR / "tcm_chroma_db"

SHICAI_FILE = DATA_DIR / "shicai_rag.jsonl"
CAIPU_FILE = DATA_DIR / "caipu_rag.jsonl"

# Embedding model settings
MODEL_NAME = "BAAI/bge-small-zh-v1.5"

def load_documents_from_jsonl(file_path: Path):
    documents = []
    if not file_path.exists():
        print(f"Warning: {file_path} not found.")
        return documents
        
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            doc = Document(
                page_content=data.get("page_content", ""),
                metadata=data.get("metadata", {})
            )
            documents.append(doc)
    return documents

def init_vector_db():
    print(f"Initializing embedding model '{MODEL_NAME}' ...")
    model_kwargs = {'device': 'cpu'}  
    encode_kwargs = {'normalize_embeddings': True}
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    
    # Check and clear existing Chroma DB to prevent duplication
    if CHROMA_DB_DIR.exists():
        print(f"Clearing existing vector database at: {CHROMA_DB_DIR}")
        shutil.rmtree(CHROMA_DB_DIR)
        
    CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load documents
    print("Loading documents from JSONL files...")
    shicai_docs = load_documents_from_jsonl(SHICAI_FILE)
    print(f"  Loaded {len(shicai_docs)} shicai (ingredient) documents.")
    
    caipu_docs = load_documents_from_jsonl(CAIPU_FILE)
    print(f"  Loaded {len(caipu_docs)} caipu (recipe) documents.")
    
    all_docs = shicai_docs + caipu_docs
    
    if not all_docs:
        print("No documents to load. Exiting.")
        return
        
    print(f"Total documents to ingest: {len(all_docs)}")
    print("Ingesting into ChromaDB... (This may take a few moments)")
    
    # Create and persist vector store
    vectorstore = Chroma.from_documents(
        documents=all_docs,
        embedding=embeddings,
        persist_directory=str(CHROMA_DB_DIR)
    )
    vectorstore.persist()
    print("✅ Vector database successfully built and persisted at:", CHROMA_DB_DIR)

if __name__ == "__main__":
    init_vector_db()
