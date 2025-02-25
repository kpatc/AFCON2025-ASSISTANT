# AFCON 2025 Information Retrieval System

## Overview

Welcome to the AFCON 2025 Information Retrieval System! This project is designed to provide detailed information about the AFCON 2025 event using a combination of SQL database queries and vector-based document retrieval. The system leverages advanced language models to generate natural language responses based on both structured and unstructured data.

## Features

- **SQL Database Extraction**: Extract data from SQLite database tables and save it to JSON files.
- **Vector-Based Document Retrieval**: Use Chroma for similarity search on document embeddings.
- **Combined Responses**: Merge information from both sources to provide comprehensive answers.
- **Conversation Memory**: Maintain context across multiple queries for more accurate responses.

## Setup

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/afcon2025-info-retrieval.git
    cd afcon2025-info-retrieval
    ```

2. **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    Create a [.env](http://_vscodecontentref_/1) file in the root directory with the following content:
    ```plaintext
    GOOGLE_API_KEY=your_google_api_key
    ```

5. **Prepare the database**:
    Ensure your SQLite database (`afcon2025.db`) is in the root directory.

## Usage

### Extract Data from SQLite to JSON

1. **Run the extraction script**:
    ```bash
    python CreateDBS/sql_to_json.py
    ```
    This will extract data from all tables in the SQLite database and save it to [sqlToJson.json](http://_vscodecontentref_/2).

### Process JSON Files into Vector Database

1. **Run the processing script**:
    ```bash
    python CreateDBS/createdbvectfromJson.py
    ```
    This will process the JSON files and add them to the vector database.

### Interact with the System

1. **Run the main script**:
    ```bash
    python test_rag.py
    ```

2. **Ask questions about AFCON 2025**:
    - Example queries:
        - "Give me some hostels in Rabat"
        - "Show me the match schedule for Casablanca"
        - "List pharmacies in Sale"

## Example Queries

- "Give me some hostels in Rabat"
- "Show me the match schedule for Casablanca"
- "List pharmacies in Sale"

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
