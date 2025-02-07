import sqlite3
import pandas as pd

def inspect_database(db_path='./afcon2025.db'):
    """List all tables and their schemas in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Available tables:")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        print(f"\n📋 Table: {table_name}")
        print("Columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
        # Show sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
        sample = cursor.fetchone()
        if sample:
            print(f"Sample row: {sample}")
    
    conn.close()

if __name__ == "__main__":
    inspect_database()