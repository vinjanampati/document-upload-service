# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Start Qdrant (if not already running)
```bash
cd ../hellofastapi  # Go to hellofastapi directory
docker compose up -d qdrant
cd ../document-upload-service  # Return to this directory
```

### Step 2: Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure API Keys
The `.env` file is already created with your OpenAI key. If you want to use other providers, edit `.env`:
```bash
nano .env  # or use your preferred editor
```

### Step 4: Start Backend
```bash
./start-backend.sh
# Or manually: uvicorn app.main:app --reload --port 8001
```

Backend will be available at: **http://localhost:8001**
API Documentation: **http://localhost:8001/docs**

### Step 5: Start Frontend
```bash
cd frontend
npm install
npm start
```

Frontend will open at: **http://localhost:3000**

## 📝 Quick Test

### Test 1: Upload via Web UI
1. Go to http://localhost:3000
2. Click "Choose File" and select a .txt or .pdf file
3. Leave default settings (Fixed chunking, OpenAI embeddings)
4. Click "Upload and Process"
5. View the results with chunk preview!

### Test 2: Upload via API
```bash
# Create a test file
echo "This is a test document. It has multiple sentences. Each sentence adds more context." > test.txt

# Upload with fixed chunking
curl -X POST "http://localhost:8001/api/upload" \
  -F "file=@test.txt" \
  -F 'config_json={"chunking_strategy":"fixed","chunk_size":100,"chunk_overlap":20,"embedding_provider":"openai","embedding_model":"text-embedding-3-small","embedding_dimension":1536}'
```

### Test 3: Check Collections
```bash
# List all collections
curl http://localhost:8001/api/collections

# Get collection info
curl http://localhost:8001/api/collections/documents
```

## 🎯 Try Different Chunking Strategies

### Fixed Chunking (Default)
- **Use for**: General purpose, predictable chunks
- **Settings**: chunk_size=512, chunk_overlap=50

### Semantic Chunking
- **Use for**: Maintaining topic coherence
- **Settings**: chunking_strategy="semantic", semantic_threshold=0.7

### Hierarchical Chunking
- **Use for**: Multi-level retrieval (parent + child chunks)
- **Settings**: chunking_strategy="hierarchical", parent_chunk_size=2048, child_chunk_size=512

## 🔧 Common Issues

**Backend won't start?**
- Make sure port 8001 is free: `lsof -i :8001`
- Check Qdrant is running: `docker ps | grep qdrant`

**Upload fails?**
- Verify OpenAI API key in `.env`
- Check file size (max 50MB)
- Ensure file format is supported (.txt, .md, .pdf, .docx, .html)

**Frontend can't connect?**
- Backend must be running on port 8001
- Check browser console for errors

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore API docs at http://localhost:8001/docs
- Try uploading documents for use with the RAG chatbot
- Experiment with different embedding models and chunking strategies

## 💡 Tips

- Use **Fixed chunking** for general documents
- Use **Semantic chunking** when topic coherence matters
- Use **Hierarchical chunking** for complex retrieval with broad+specific search
- OpenAI embeddings are fast and high-quality (recommended)
- FastEmbed works offline (no API key needed)
