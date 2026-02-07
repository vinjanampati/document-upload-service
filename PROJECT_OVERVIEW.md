# Document Upload Service

**Standalone service for uploading and processing documents into a vector database with configurable chunking and embedding strategies.**

## 📁 Project Location

This is a **separate project** from the main `hellofastapi` conversational chatbot. It provides document ingestion capabilities that can be used independently or alongside the chatbot.

```
/Users/vin/Documents/code/ai/
├── hellofastapi/              # Main conversational RAG chatbot
│   ├── app/
│   ├── docker-compose.yml     # Qdrant + Redis containers
│   └── ...
│
└── document-upload-service/   # THIS PROJECT (Document upload & processing)
    ├── app/                   # Backend (FastAPI)
    │   ├── chunking/          # Chunking strategies
    │   ├── services/          # Embedding & vector store
    │   └── routers/           # API endpoints
    ├── frontend/              # Frontend (React)
    └── uploads/               # Temporary file storage
```

## 🔗 Relationship with hellofastapi

- **Shared Infrastructure**: Uses the same Qdrant instance from `hellofastapi` (port 6333)
- **Independent**: Runs on different ports (Backend: 8002, Frontend: 3002)
- **Complementary**: Documents uploaded here are available to the chatbot for RAG retrieval

## 🚀 Quick Start

### Prerequisites
1. **Start Qdrant** from hellofastapi:
   ```bash
   cd /Users/vin/Documents/code/ai/hellofastapi
   docker compose up -d qdrant
   ```

### Run the Service

**Backend** (in one terminal):
```bash
cd /Users/vin/Documents/code/ai/document-upload-service
./start-backend.sh
```
- API: http://localhost:8002
- Docs: http://localhost:8002/docs

**Frontend** (in another terminal):
```bash
cd /Users/vin/Documents/code/ai/document-upload-service/frontend
npm start
```
- UI: http://localhost:3002

## 📋 Features

### Chunking Strategies
- **Fixed**: Fixed-size chunks with overlap (fast, predictable)
- **Semantic**: Similarity-based sentence grouping (coherent topics)
- **Hierarchical**: Parent + child chunks (multi-level retrieval)

### Embedding Providers
- **OpenAI**: text-embedding-3-small/large
- **Cohere**: embed-english/multilingual-v3.0
- **Google**: models/embedding-001
- **FastEmbed**: Local embeddings (no API key)

### File Formats
- `.txt`, `.md`, `.pdf`, `.docx`, `.html`

## 🔌 Ports Summary

| Service | Port | URL |
|---------|------|-----|
| Qdrant (shared) | 6333 | http://localhost:6333 |
| Redis (shared) | 6379 | http://localhost:6379 |
| Redis Insight | 8001 | http://localhost:8001 |
| **Upload Backend** | **8002** | **http://localhost:8002** |
| **Upload Frontend** | **3002** | **http://localhost:3002** |
| Chatbot Backend | 8000 | http://localhost:8000 |
| Chatbot Frontend | 3001 | http://localhost:3001 |

## 📚 Documentation

- [Quick Start Guide](QUICKSTART.md) - Get started in 5 minutes
- [Full README](README.md) - Complete documentation
- [API Documentation](http://localhost:8002/docs) - Interactive API docs (when running)

## 🎯 Use Cases

1. **Bulk Document Ingestion**: Upload multiple documents to vector store
2. **Custom Chunking**: Experiment with different chunking strategies
3. **Multi-Provider Embeddings**: Test different embedding models
4. **RAG Chatbot Preparation**: Prepare documents for the hellofastapi chatbot
5. **Standalone Search**: Use as independent document search service

## 🤝 Integration Workflow

```
1. Upload documents here → 2. Stored in Qdrant → 3. Available to chatbot
   (document-upload-service)                         (hellofastapi)
```

## 💡 Tips

- Use **Fixed chunking** for general documents
- Use **Semantic chunking** when topic coherence matters
- Use **Hierarchical chunking** for complex retrieval systems
- OpenAI embeddings are recommended for quality
- FastEmbed works offline (no API key required)
