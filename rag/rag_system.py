from rag.agents_to_interact_with_csv_files import AfconAgents
from typing import Dict
import sqlite3
import pandas as pd

class AfconRAG:
    def __init__(self):
        self.agents = AfconAgents()
        self.conversation_history = ""
        
    def get_db_schema(self) -> str:
        """Get database schema"""
        conn = sqlite3.connect('../afcon2025.db')
        cursor = conn.cursor()
        schema = []
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for table in cursor.fetchall():
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [f"{col[1]} ({col[2]})" for col in cursor.fetchall()]
            schema.append(f"Table: {table_name}\nColumns: {', '.join(columns)}")
            
        conn.close()
        return "\n\n".join(schema)

    def process_query(self, question: str) -> Dict:
        """Process user query through the RAG pipeline"""
        sql_result = {'thinking': []}
        data = None
        # Classify question
        classification = self.agents.classifier_agent(
            question, self.conversation_history
        )
        
        if classification['type'] == 'database':
            # Generate and execute SQL
            schema = self.get_db_schema()
            sql_result = self.agents.sql_agent(
                question, schema, self.conversation_history
            )   
            
            # Execute query if valid
            if sql_result['query'] != 'INVALID':
                conn = sqlite3.connect('../afcon2025.db')
                try:
                    # Clean query before execution
                    clean_query = sql_result['query'].strip()
                    data = pd.read_sql_query(clean_query, conn)
                except Exception as e:
                    print(f"SQL Error: {e}")
                    data = None
                finally:
                    conn.close()
            else:
                data = None

        else:
            data = None
            
        # Generate natural language response
        answer = self.agents.answer_agent(
            question, data, self.conversation_history
        )
        
        # Update conversation history
        self.conversation_history += f"\nQ: {question}\nA: {answer['answer']}\n"
        
        return {
            'answer': answer['answer'],
            'thinking_process': (
                classification['thinking'] + 
                sql_result.get('thinking', []) +
                answer['thinking']
            )
        }