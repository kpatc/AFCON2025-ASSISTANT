from typing import Dict, Optional
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import google.generativeai as genai
import os
from dotenv import load_dotenv

class AfconAgents:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Configure Google API
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
        genai.configure(api_key=api_key)
        self.model = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=api_key
        )
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        
    def sql_agent(self, question: str, schema: str, history: str = "") -> Dict:
        """SQL query generation and execution agent"""
        thinking_process = ["🤔 Understanding question and context..."]
        
        prompt = f"""You are a SQL expert. Given the database schema:

        {schema}

        Generate a SQL query for: {question}

        Instructions:
        1. First, identify which table(s) are relevant to the question
        2. Use exact column names as shown in schema
        3. Return only the raw SQL query without formatting
        4. Use UPPER() for case-insensitive text matching
        5. For questions about:
        - Pharmacies: use pharmacies table
        - Hotels: use hotels table
        - Matches: use match_schedule table
        - Restaurants: use restaurants table
        - Hospitals: use repartition_des_hopitaux_par_region_et_province_2022
        - Medicaments: use ref_des_medicaments_cnops_2014
        6. Return 'INVALID' if no relevant table exists
        
        Example formats:
        - Pharmacies: SELECT Pharmacie_Name, address FROM pharmacies WHERE UPPER(city) = 'SALE'
        - Hotels: SELECT Hotel_Name, Address FROM hotels WHERE UPPER(City) = 'CASABLANCA'
        - Matches: SELECT * FROM match_schedule WHERE UPPER(City) = 'CASABLANCA'
        """
        
        response = self.model.invoke([HumanMessage(content=prompt)])
        sql_query = response.content.strip().replace('```sql', '').replace('```', '').strip()
        
        thinking_process.append(f"🔍 Detected relevant tables from schema")
        thinking_process.append(f"📝 Generated query: {sql_query}")
        
        return {
            'query': sql_query,
            'thinking': thinking_process
        }
 
    def answer_agent(self, question: str, data: Optional[pd.DataFrame] = None, 
                    history: str = "") -> Dict:
        """Natural language response generation agent"""
        system_prompt = """You are an AFCON 2025 expert. Provide natural, 
        conversational responses. Be informative but concise."""
        
        context = f"""
        Question: {question}
        Data: {data.to_string() if data is not None else 'No data'}
        History: {history}
        """
        
        response = self.model.invoke([
            HumanMessage(content=system_prompt),
            HumanMessage(content=context)
        ])
        
        return {
            'answer': response.content,
            'thinking': ["✅ Generated response"]
        }

    def classifier_agent(self, question: str, history: str = "") -> Dict:
        """Question classification agent"""
        system_prompt = """Classify if the question needs database access.
        Return only 'database' or 'general'."""
        
        context = f"Question: {question}\nHistory: {history}"
        response = self.model.invoke([
            HumanMessage(content=system_prompt),
            HumanMessage(content=context)
        ])
        
        return {
            'type': 'database' if 'database' in response.content.lower() else 'general',
            'thinking': ["🤔 Classified question type"]
        }