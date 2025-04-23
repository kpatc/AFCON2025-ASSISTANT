import json
import google.generativeai as genai
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents import Document
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=GOOGLE_API_KEY)

# Define constants
PERSIST_DIRECTORY = os.path.join("database", "vector_store")
DATA_DIRECTORY = os.path.join("database", "data_processed")

def process_json_data(json_data, source):
    """Process JSON data into a format suitable for vectorization with enhanced metadata"""
    processed_docs = []
    
    if isinstance(json_data, dict):
        # Metadata enrichment based on source file
        base_metadata = {
            'source': source,
            'type': source.split('_')[0] if '_' in source else 'general',
            'last_updated': datetime.now().isoformat()
        }
        
        # Add specific metadata based on content type
        if 'afcon2025' in source:
            base_metadata['category'] = 'tournament'
            base_metadata['priority'] = 1
        elif any(x in source for x in ['hotel', 'restaurant']):
            base_metadata['category'] = 'accommodation_food'
            base_metadata['priority'] = 2
        elif any(x in source for x in ['hospital', 'pharmacies']):
            base_metadata['category'] = 'health'
            base_metadata['priority'] = 2
        
        # Process each section of the data
        for key, value in json_data.items():
            if key != 'metadata':
                section_text = f"{key}: {json.dumps(value, indent=2, ensure_ascii=False)}"
                doc = Document(
                    page_content=section_text,
                    metadata={**base_metadata, 'section': key}
                )
                processed_docs.append(doc)
    
    return processed_docs

def load_json_files():
    """Load and process all JSON files with enhanced metadata"""
    documents = []
    
    try:
        for filename in os.listdir(DATA_DIRECTORY):
            if filename.endswith('.json'):
                file_path = os.path.join(DATA_DIRECTORY, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    source_name = filename.replace('.json', '')
                    docs = process_json_data(data, source_name)
                    documents.extend(docs)
        return documents
    except Exception as e:
        print(f"Error loading JSON files: {e}")
        return []

def create_vector_store(embedding):
    """Create a new vector store from documents with optimized chunking"""
    documents = load_json_files()
    
    # Optimized text splitter configuration
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separator="\n"
    )
    
    # Split documents into chunks while preserving metadata
    chunks = []
    for doc in documents:
        splits = text_splitter.split_text(doc.page_content)
        for i, split in enumerate(splits):
            chunks.append(Document(
                page_content=split,
                metadata={
                    **doc.metadata,
                    'chunk_index': i,
                    'total_chunks': len(splits)
                }
            ))
    
    # Create and persist the vector store with metadata filtering capability
    return Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=PERSIST_DIRECTORY,
        collection_metadata={"hnsw:space": "cosine"}  # Optimizing for semantic search
    )

def init_rag(llm):
    """Initialize the RAG system with the provided LLM"""
    # Use Google's embeddings
    embedding = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GOOGLE_API_KEY
    )
    
    try:
        # Check if vector store exists
        if os.path.exists(PERSIST_DIRECTORY):
            try:
                print("Loading existing vector store...")
                vectorstore = Chroma(
                    persist_directory=PERSIST_DIRECTORY,
                    embedding_function=embedding
                )
                # Test the connection
                vectorstore.get()
            except Exception as e:
                print(f"Error loading existing vector store: {e}")
                print("Recreating vector store...")
                import shutil
                shutil.rmtree(PERSIST_DIRECTORY, ignore_errors=True)
                os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
                vectorstore = create_vector_store(embedding)
        else:
            print("Creating new vector store...")
            os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
            vectorstore = create_vector_store(embedding)
        
        vectorstore.persist()  # Persist immediately after creation
        
        # Configure retriever with metadata-aware search
        retriever = vectorstore.as_retriever(
            search_type="mmr",  # Using Maximum Marginal Relevance for diversity
            search_kwargs={
                "k": 5,  # Retrieve top 5 most relevant chunks
                "lambda_mult": 0.7,  # Balance between relevance and diversity
                "fetch_k": 20  # Fetch more candidates for MMR to choose from
            }
        )

        # Initialize QA chain with metadata handling
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,  # Enable source tracking
            verbose=True
        )

        return qa_chain
    except Exception as e:
        print(f"Error initializing RAG system: {e}")
        raise