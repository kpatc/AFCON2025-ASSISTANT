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
        conn = sqlite3.connect('./afcon2025.db')
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
        try:
            classification = self.agents.classifier_agent(question, self.format_history())
            sql_result = {'thinking': []}
            data = None
            
            if classification['type'] == 'database':
                schema = self.get_db_schema()
                sql_result = self.agents.sql_agent(question, schema, self.format_history())
                
                if sql_result['query'] != 'INVALID':
                    try:
                        conn = sqlite3.connect('./afcon2025.db')
                        data = pd.read_sql_query(sql_result['query'].strip(), conn)
                        conn.close()
                    except Exception as e:
                        sql_result['thinking'].append(f"❌ Database error: {str(e)}")
                        data = None
            
            answer = self.agents.answer_agent(question, data, self.format_history())
            self.conversation_history.append({'question': question, 'answer': answer['answer']})
            
            return {
                'answer': answer['answer'],
                'thinking_process': classification['thinking'] + sql_result['thinking'] + answer['thinking']
            }
        except Exception as e:
            return {
                'answer': f"Error: {str(e)}",
                'thinking_process': ["❌ Error processing query"]
            }