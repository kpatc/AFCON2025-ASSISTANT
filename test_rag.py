from rag.hybrid_rag import HybridRAG

def main():
    rag = HybridRAG()
    
    while True:
        question = input("Ask about AFCON 2025 (or 'quit' to exit): ")
        if question.lower() == 'quit':
            break
            
        result = rag.get_combined_answer(question)
        print("\nAnswer:", result['answer'])
        print("\nThinking process:")
        for step in result['thinking_process']:
            print(step)

if __name__ == "__main__":
    main()