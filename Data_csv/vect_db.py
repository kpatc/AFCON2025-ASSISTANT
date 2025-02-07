import json
from langchain_community.embeddings import OllamaEmbeddings
from langchain.docstore.document import Document
from langchain_chroma import Chroma
from typing import List
from uuid import uuid4

def load_json_data(file_path: str) -> List[Document]:
    """Load JSON data and convert to list of Document objects"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    documents = []
    for table_name, rows in data.items():
        for row in rows:
            content = json.dumps(row, ensure_ascii=False)
            documents.append(Document(page_content=content))
    
    return documents

def create_vector_db(documents: List[Document], persist_dir: str = './db_vect'):
    """Create a vector database from documents"""
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_store = Chroma(
        collection_name="afcon_data",
        embedding_function=embeddings,
        persist_directory=persist_dir
    )
    
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)
    
    print(f"Vector database created at {persist_dir}")

if __name__ == "__main__":
    json_file_path = './Data_csv/sqlToJson.json'
    documents = load_json_data(json_file_path)
    create_vector_db(documents)