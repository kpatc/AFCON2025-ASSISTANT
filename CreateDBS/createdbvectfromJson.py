import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Optional
from uuid import uuid4
from langchain_community.embeddings import OllamaEmbeddings
from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma
import logging
import glob
import shutil
from pathlib import Path
# load json files
def load_data(json_file_path: str): 
    combined_data = []
    # Get all JSON files in directory
    json_files = glob.glob(os.path.join(json_file_path, "*.json"))
    for file_path in json_files:
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                combined_data.extend(data)  
        else:
            print(f"Le fichier {file_path} n'existe pas.")
    return combined_data

#chunking function to split text into chunks
def chunking(data):
    # Split
    documents = [entry["title"]+" "+entry["text"] for entry in data]
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500, chunk_overlap=50
    )
    # Divide text in chunks
    all_splits = []
    for text in documents:
        splits = text_splitter.split_text(text) 
        all_splits.extend(splits) 
    print("Nombre total de chunks générés :", len(all_splits))
    return all_splits

def init_embeddings(model_name: str = "nomic-embed-text") -> OllamaEmbeddings:
    """Initialize embedding model"""
    try:
        return OllamaEmbeddings(model=model_name)
    except Exception as e:
        logging.error(f"Error initializing embeddings: {e}")
        raise

def setup_vector_store(
    collection_name: str,
    embedding_model: OllamaEmbeddings,
    persist_dir: str = "./db_vect"
) -> Chroma:
    """Setup Chroma vector store"""
    return Chroma(
        collection_name=collection_name,
        embedding_function=embedding_model,
        persist_directory=persist_dir
    )

def process_documents(
    path_to_json_files: str = "../data_js",
    collection_name: str = "Afcon_2025",
    persist_dir: str = "../db_vect",
    model_name: str = "nomic-embed-text"
) -> Optional[Chroma]:
    """Process JSON files into vector database"""
    try:
        if os.path.exists(persist_dir):
            logging.info(f"Removing existing vector store at {persist_dir}")
            shutil.rmtree(persist_dir)
        
        # Create fresh directory
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        # Load data
        data = load_data(path_to_json_files)
        
        # Create chunks
        chunks = chunking(data)
        
        # Initialize embeddings
        embeddings = init_embeddings(model_name)
        
        # Setup vector store
        vector_store = setup_vector_store(
            collection_name,
            embeddings,
            persist_dir
        )
        
        # Create documents
        documents = [Document(page_content=chunk) for chunk in chunks]
        uuids = [str(uuid4()) for _ in range(len(documents))]
        
        # Add to vector store
        vector_store.add_documents(documents=documents, ids=uuids)
        
        return vector_store
        
    except Exception as e:
        logging.error(f"Error processing documents: {e}")
        return None
    
# Usage example
if __name__ == "__main__":
    store = process_documents()
    if store:
        print("Documents processed successfully")
