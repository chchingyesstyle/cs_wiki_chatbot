# MediaWiki Chatbot PoC

A proof-of-concept chatbot that uses your MediaWiki 1.43 database with a local Llama model (via llama-cpp-python) to answer questions about your wiki content.

## Architecture

- **Database**: MariaDB (MediaWiki 1.43)
- **LLM**: Local Llama model (GGUF format via llama-cpp-python)
- **Backend**: Python + Flask
- **Frontend**: Simple HTML/JS interface

## Features

✅ Query MediaWiki database for relevant content  
✅ Use LLM to generate natural language answers  
✅ RESTful API with Flask  
✅ Web UI and CLI interface  
✅ Source attribution (shows which wiki pages were used)

## Installation

### 1. Install Dependencies

```bash
# Install Python packages
python3 -m pip install -r requirements.txt
```

### 2. Download a Llama Model

Download a quantized GGUF model (4-bit recommended for CPU):

```bash
# Create models directory
mkdir -p models

# Example: Download Llama 2 7B Chat (Q4_K_M quantization)
# You can use wget, curl, or download manually from Hugging Face
# Popular options:
# - TheBloke/Llama-2-7B-Chat-GGUF
# - TheBloke/Mistral-7B-Instruct-v0.2-GGUF
# - TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF (faster, smaller)

# Example using wget:
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf -O models/llama-2-7b-chat.Q4_K_M.gguf
```

### 3. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your settings
nano .env
```

Update these values in `.env`:
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Your MariaDB credentials
- `MODEL_PATH` - Path to your GGUF model file

## Usage

### Option 1: Web Interface (Recommended)

```bash
# Start the Flask server
python3 app.py
```

Then open `index.html` in your browser or serve it:
```bash
# Serve the HTML file
python3 -m http.server 8080
# Visit: http://localhost:8080
```

### Option 2: CLI Interface

```bash
# Make executable
chmod +x cli.py

# Run
python3 cli.py
```

### Option 3: API Only

```bash
# Start server
python3 app.py

# Test with curl
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main page about?"}'
```

## API Endpoints

### POST /api/chat
Chat with the bot
```json
{
  "question": "Your question here"
}
```

Response:
```json
{
  "question": "Your question",
  "answer": "Bot's answer",
  "sources": ["Page1", "Page2"],
  "context_used": true
}
```

### GET /api/search?q=query&limit=10
Search wiki pages

### GET /api/pages?limit=50
List all wiki pages

### GET /health
Health check

## Project Structure

```
chatbot/
├── app.py              # Flask API server
├── chatbot.py          # Main chatbot logic
├── config.py           # Configuration
├── db_connector.py     # MediaWiki DB connector
├── llm_model.py        # Llama model wrapper
├── cli.py              # Command-line interface
├── index.html          # Web interface
├── requirements.txt    # Python dependencies
├── .env               # Your configuration (create from .env.example)
└── .env.example       # Example configuration
```

## How It Works

1. **User asks a question** → Sent to Flask API
2. **Database search** → Searches MediaWiki DB for relevant pages
3. **Context building** → Cleans and formats wiki content
4. **Prompt creation** → Builds prompt with context + question
5. **LLM generation** → Local Llama model generates answer
6. **Response** → Returns answer with source attribution

## Troubleshooting

### Model loading issues
- Ensure the model file exists at the path specified in `.env`
- Check you have enough RAM (4GB+ for Q4 models)
- Try a smaller model like TinyLlama-1.1B

### Database connection issues
- Verify MariaDB is running
- Check credentials in `.env`
- Test connection: `mysql -h localhost -u wikiuser -p wikidb`

### Slow responses
- Use a smaller/faster model
- Increase `MODEL_N_THREADS` in `.env`
- Reduce `MAX_CONTEXT_PAGES` to use less context

### pip installation issues
```bash
# Try with pip module
python3 -m pip install --user -r requirements.txt

# Or install system packages (if available)
sudo yum install python3-pymysql python3-flask
pip install llama-cpp-python
```

## Vector Search (Enhanced Feature)

The chatbot now supports **semantic/vector search** using ChromaDB and sentence-transformers for better context retrieval.

### Setup Vector Search

1. **Index your wiki pages** (one-time setup):
```bash
python3 index_wiki.py
```

This will:
- Download the sentence-transformers model (all-MiniLM-L6-v2)
- Index all wiki pages into ChromaDB
- Store embeddings in `./chroma_db/` directory

2. **Enable in `.env`**:
```bash
USE_VECTOR_SEARCH=True
VECTOR_DB_PATH=./chroma_db
VECTOR_TOP_K=3
```

3. **Restart the chatbot**:
```bash
./restart.sh
```

### How it Works

- **With Vector Search**: Uses semantic similarity to find relevant pages (better understanding of context)
- **Without Vector Search**: Falls back to keyword-based search
- Automatic fallback if vector DB is empty or unavailable

### Re-indexing

Run `index_wiki.py` again whenever wiki content changes significantly.

## Next Steps

- ✅ **Vector search**: Semantic embeddings for better context retrieval
- **Chat history**: Implement conversation memory
- **Streaming**: Stream responses for better UX
- **Caching**: Cache frequent queries
- **Fine-tuning**: Fine-tune model on your wiki content

## License

MIT
