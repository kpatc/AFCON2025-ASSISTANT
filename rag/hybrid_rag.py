from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from typing import Dict, List
from langchain_core.prompts import ChatPromptTemplate
import google.generativeai as genai
import os
from dotenv import load_dotenv
from rag.rag_system import AfconRAG

class HybridRAG:
    VECTOR_PROMPT = """
    Based on previous conversation:
    {history}
    
    And this context:
    {context}
    
    Answer this question: {question}
    
    Instructions:
    - Provide detailed answers
    - Don't justify your answers
    - Don't reference the context
    - Build on previous conversation
    """
    
    COMBINED_PROMPT = """
    Previous conversation:
    {history}
    
    Database information:
    {sql_answer}
    
    Document information:
    {vector_answer}
    
    Question: {question}
    
    Instructions:
    - Provide detailed answers
    - Don't justify your answers
    - Don't reference the context
    - Build on previous conversation
    """
    
    def __init__(
        self,
        vector_store_path: str = "./db_vect",
        collection_name: str = "Afcon_2025"
    ):  
        load_dotenv()
        #initialize sql rag
        self.sql_rag = AfconRAG()
        
        # Initialize embeddings for querying
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        
        # Initialize vector store with embeddings
        self.vector_store = Chroma(
            persist_directory=vector_store_path,
            collection_name=collection_name,
            embedding_function=self.embeddings
        )
        
        # Initialize conversation history
        self.conversation_history = []
        self.max_history = 5

        # Initialize prompt templates
        self.vector_prompt = ChatPromptTemplate.from_template(self.VECTOR_PROMPT)
        self.combined_prompt = ChatPromptTemplate.from_template(self.COMBINED_PROMPT)
        # Initialize LLM
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.llm = genai.GenerativeModel("gemini-pro")
    
    def format_history(self) -> str:
        """Format conversation history"""
        if not self.conversation_history:
            return "No previous conversation."
        
        formatted = []
        for exchange in self.conversation_history[-self.max_history:]:
            formatted.extend([
                f"User: {exchange['question']}",
                f"Assistant: {exchange['answer']}"
            ])
        return "\n".join(formatted)
    
    def get_vector_answer(self, query: str) -> str:
        docs = self.vector_store.similarity_search(
            query=query,
            k=3
        )
        context = [doc.page_content for doc in docs]
        prompt = self.vector_prompt.format(
            context=context,
            question=query,
            history=self.format_history()
        )
        response = self.llm.generate_content(prompt)
        return response.text
    
    def get_combined_answer(self, query: str) -> Dict:
        sql_result = self.sql_rag.process_query(query)
        vector_answer = self.get_vector_answer(query)
        history = self.format_history()
        
        prompt = self.combined_prompt.format(
            sql_answer=sql_result['answer'],
            vector_answer=vector_answer,
            question=query,
            history=history
        )
        
        final_response = self.llm.generate_content(prompt)
        
        # Update conversation history
        self.conversation_history.append({
            'question': query,
            'answer': final_response.text
        })
        
        return {
            'answer': final_response.text,
            'thinking_process': sql_result.get('thinking_process', []) + [
                "📚 Retrieved vector store information",
                "🧠 Considered conversation history",
                "✨ Generated combined response"
            ]
        }