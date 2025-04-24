import json
import google.generativeai as genai
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

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
    """Process JSON data into a format suitable for vectorization"""
    processed_text = []

    def extract_data(data, parent_key=''):
        """Helper function to recursively extract key-value pairs from the JSON structure"""
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{parent_key}_{key}" if parent_key else key
                extract_data(value, new_key)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                extract_data(item, f"{parent_key}_{index}")
        else:
            # Add leaf node to the text
            processed_text.append(f"{parent_key}: {data}")
    
    # Start processing the JSON data
    extract_data(json_data)
    return "\n".join(processed_text)

def load_json_files():
    """Load and process all JSON files from the data directory"""
    documents = []
    
    # Get all JSON files in the data directory
    json_files = [f for f in os.listdir(DATA_DIRECTORY) if f.endswith('.json')]
    
    for json_file in json_files:
        file_path = os.path.join(DATA_DIRECTORY, json_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Process the JSON data into a more searchable format
                text = process_json_data(data, json_file)
                # Create a document with metadata
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "source": json_file,
                        "type": json_file.replace('.json', '')
                    }
                ))
        except Exception as e:
            print(f"Error loading {json_file}: {str(e)}")
    
    return documents

def create_vector_store(embedding):
    """Create a new vector store from documents"""
    documents = load_json_files()
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,  # Increased overlap for better context
        separator="\n"
    )
    
    # Split documents into chunks
    docs = []
    for doc in documents:
        splits = text_splitter.split_text(doc.page_content)
        for split in splits:
            docs.append(Document(
                page_content=split,
                metadata=doc.metadata
            ))

    # Create and persist the vector store
    return Chroma.from_documents(
        documents=docs,
        embedding=embedding,
        persist_directory=PERSIST_DIRECTORY
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
                # Remove existing store
                import shutil
                shutil.rmtree(PERSIST_DIRECTORY, ignore_errors=True)
                os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
                vectorstore = create_vector_store(embedding)
        else:
            print("Creating new vector store...")
            os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
            vectorstore = create_vector_store(embedding)
        
        vectorstore.persist()  # Persist immediately after creation
        
        retriever = vectorstore.as_retriever(
            search_kwargs={
                "k": 5  # Retrieve top 5 most relevant chunks
            }
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",  # Using "stuff" method for better context handling
            retriever=retriever,
            return_source_documents=False  # Disable source tracking to fix the output format
        )

        return qa_chain
    except Exception as e:
        print(f"Error initializing RAG system: {e}")
        raise
