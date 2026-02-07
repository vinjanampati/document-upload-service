# Document Upload Service

A complete solution for uploading documents to a vector store with configurable chunking strategies and embedding options.

## Features

### Chunking Strategies
1. **Fixed Chunking**: Split text into fixed-size chunks with configurable overlap
2. **Semantic Chunking**: Split text based on semantic similarity between sentences
3. **Hierarchical Chunking**: Create both parent (large) and child (small) chunks for multi-level retrieval

### Embedding Providers
- **OpenAI**: text-embedding-3-small, text-embedding-3-large
- **Cohere**: embed-english-v3.0, embed-multilingual-v3.0
- **Google**: models/embedding-001
- **FastEmbed**: Local embeddings (BAAI/bge-small-en-v1.5, etc.)

### Supported File Formats
- Plain text (.txt)
- Markdown (.md)
- PDF (.pdf)
- Word documents (.docx)
- HTML (.html)

## Architecture

```
document-upload-service/
├── app/
│   ├── chunking/          # Chunking strategies
│   │   ├── base.py        # Base chunker class
│   │   ├── fixed.py       # Fixed-size chunking
│   │   ├── semantic.py    # Semantic chunking
│   │   └── hierarchical.py # Hierarchical chunking
│   ├── services/          # Business logic
│   │   ├── embedding.py   # Embedding generation
│   │   ├── vectorstore.py # Qdrant integration
│   │   └── document.py    # Document processing
│   ├── routers/           # API endpoints
│   │   └── upload.py      # Upload routes
│   ├── config.py          # Configuration
│   ├── models.py          # Pydantic models
│   └── main.py            # FastAPI app
├── frontend/              # React frontend
│   └── src/
│       ├── components/
│       └── services/
└── uploads/               # Temporary file storage
```

## Setup

### Prerequisites
- Python 3.10+
- Node.js 16+
- Docker (for Qdrant)
- API keys for embedding providers (OpenAI, Cohere, etc.)

### Backend Setup

1. **Start Qdrant** (shares Qdrant instance with hellofastapi chatbot):
   ```bash
   cd ../hellofastapi  # Go to hellofastapi directory
   docker compose up -d qdrant
   cd ../document-upload-service  # Return to this directory
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Start backend**:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

   Backend will run on: http://localhost:8001
   API docs: http://localhost:8001/docs

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Default API URL is http://localhost:8001/api
   ```

3. **Start frontend**:
   ```bash
   npm start
   ```

   Frontend will run on: http://localhost:3000

## Usage

### Via Web UI

1. Open http://localhost:3000
2. Select a file to upload
3. Configure chunking strategy:
   - **Fixed**: Set chunk size and overlap
   - **Semantic**: Set similarity threshold
   - **Hierarchical**: Set parent and child chunk sizes
4. Configure embedding:
   - Choose provider (OpenAI, Cohere, Google, FastEmbed)
   - Specify model name
   - Set embedding dimension
5. Optionally specify a custom collection name
6. Click "Upload and Process"
7. View results including chunk preview

### Via API

#### Upload a document

```bash
curl -X POST "http://localhost:8001/api/upload" \
  -F "file=@document.pdf" \
  -F 'config_json={
    "chunking_strategy": "fixed",
    "chunk_size": 512,
    "chunk_overlap": 50,
    "embedding_provider": "openai",
    "embedding_model": "text-embedding-3-small",
    "embedding_dimension": 1536,
    "collection_name": "my_documents"
  }'
```

#### List collections

```bash
curl "http://localhost:8001/api/collections"
```

#### Get collection info

```bash
curl "http://localhost:8001/api/collections/my_documents"
```

#### Delete collection

```bash
curl -X DELETE "http://localhost:8001/api/collections/my_documents"
```

## Configuration Options

### UploadConfig

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `chunking_strategy` | enum | fixed, semantic, hierarchical | fixed |
| `chunk_size` | int | Chunk size in characters (100-4000) | 512 |
| `chunk_overlap` | int | Overlap between chunks (0-500) | 50 |
| `embedding_provider` | str | openai, cohere, google, fastembed | openai |
| `embedding_model` | str | Specific model name | text-embedding-3-small |
| `embedding_dimension` | int | Vector dimension | 1536 |
| `collection_name` | str | Qdrant collection name | documents |
| `parent_chunk_size` | int | Parent size for hierarchical | 2048 |
| `child_chunk_size` | int | Child size for hierarchical | 512 |
| `semantic_threshold` | float | Similarity threshold (0-1) | 0.7 |

## Chunking Strategies Explained

### Fixed Chunking
- Splits text into chunks of approximately equal size
- Configurable overlap to maintain context
- Fast and predictable
- Good for: General purpose, consistent chunk sizes

### Semantic Chunking
- Splits text at natural sentence boundaries
- Groups sentences based on semantic similarity
- Requires embedding model for similarity calculation
- Good for: Maintaining semantic coherence, topic-based retrieval

### Hierarchical Chunking
- Creates both parent (large) and child (small) chunks
- Child chunks reference their parent
- Enables multi-level retrieval strategies
- Good for: Complex retrieval systems, broad+specific search

## Embedding Models

### OpenAI
- `text-embedding-3-small` (1536 dim) - Fast, cost-effective
- `text-embedding-3-large` (3072 dim) - Higher quality
- `text-embedding-ada-002` (1536 dim) - Legacy model

### Cohere
- `embed-english-v3.0` - English-optimized
- `embed-multilingual-v3.0` - Multilingual support

### Google
- `models/embedding-001` (768 dim) - General purpose

### FastEmbed (Local)
- `BAAI/bge-small-en-v1.5` (384 dim) - Fast, no API needed
- `BAAI/bge-base-en-v1.5` (768 dim) - Balanced
- `sentence-transformers/all-MiniLM-L6-v2` (384 dim) - Lightweight

## Integration with RAG Chatbot

This service uploads documents to the same Qdrant instance used by the main RAG chatbot. Documents uploaded here will be available for retrieval in the chatbot.

### Workflow
1. Upload documents via this service
2. Documents are chunked and embedded
3. Chunks stored in Qdrant
4. RAG chatbot retrieves relevant chunks during conversations

## Troubleshooting

### Backend won't start
- Check Qdrant is running: `docker ps | grep qdrant`
- Verify API keys in `.env`
- Check port 8001 is not in use

### Frontend can't connect
- Verify backend is running on port 8001
- Check CORS settings in `app/main.py`
- Verify `.env` has correct API_URL

### Upload fails
- Check file size (default max: 50MB)
- Verify file format is supported
- Check embedding provider API key is valid
- Ensure Qdrant is accessible

### Semantic chunking not working
- Requires embedding model to calculate similarity
- Falls back to sentence-based chunking if embedding fails
- Check embedding provider credentials

## API Documentation

Full interactive API documentation available at: http://localhost:8001/docs

## License

MIT
