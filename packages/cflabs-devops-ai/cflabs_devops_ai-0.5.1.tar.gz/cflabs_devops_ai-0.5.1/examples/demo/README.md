# Project Summarizer

A comprehensive document summarization and analysis tool that processes various file formats and provides intelligent summaries.

## Features

- **Doument Summary**: Process PDF, DOCX, PPTX, and text files and produce summary
- **Numerical Analysis**: Extract and analyze table data from documents

## Project Structure

```
project_summarizer/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── src/
│   ├── api/              # API endpoints
│   ├── base_classes/     # Base classes for data and vector operations
│   ├── config.py         # Configuration settings
│   ├── core/            # Core functionality
│   │   ├── data_layer/  # Document ingestion and processing
│   │   ├── document_summary/  # Summarization logic
│   │   ├── numerical_summary/ # Table data analysis
│   │   └── services/    # External service integrations
│   ├── database.py      # Database configuration
│   ├── models/          # Data models
│   ├── repositories/    # Data access layer
│   └── utils/          # Utility functions
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables in `.env` file
5. Run the application:
   ```bash
   python main.py
   ```

## Environment Variables

Create a `.env` file with the following variables:
```
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=your_index_name
```

## Usage

The application provides APIs for:
- Document ingestion and processing
- Document summarization
- Numerical data analysis
- Vector search and retrieval

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add your license information here] 