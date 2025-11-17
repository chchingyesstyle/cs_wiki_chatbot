# MediaWiki Chatbot PoC (OpenAI Version)

A proof-of-concept chatbot that uses your MediaWiki 1.43 database with OpenAI API to answer questions about your wiki content.

## Architecture

- **Database**: MariaDB (MediaWiki 1.43)
- **Vector Database**: ChromaDB with sentence-transformers (semantic search)
- **LLM**: OpenAI API (GPT-3.5-turbo or GPT-4)
- **Backend**: Python + Flask
- **Frontend**: Simple HTML/JS interface
- **RAG (Retrieval-Augmented Generation)**: 3-stage pipeline for accurate, source-backed answers
  - **Retrieval**: Hybrid vector + keyword search for relevant wiki pages
  - **Augmentation**: Context-enriched prompts with source references
  - **Generation**: OpenAI generates answers strictly from provided context

## Features

✅ Query MediaWiki database for relevant content  
✅ Semantic search with vector embeddings (ChromaDB)  
✅ Use OpenAI API to generate natural language answers  
✅ RESTful API with Flask  
✅ Web UI and CLI interface  
✅ **Clickable source links**: Direct links to wiki pages for referenced sources  
✅ Source attribution (shows which wiki pages were used)  
✅ Automatic filtering of expired/outdated pages  
✅ Customer service agent persona (admits when it doesn't know)  
✅ **RAG-powered Q&A**: Retrieval-Augmented Generation for accurate, context-based answers

## Installation

### 1. Install Dependencies

```bash
# Install Python packages
python3 -m pip install -r requirements.txt
```

### 2. Get OpenAI API Key

Sign up for OpenAI API access at https://platform.openai.com/ and get your API key.

### 3. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your settings
nano .env
```

Update these values in `.env`:
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Your MariaDB credentials
- `OPENAI_API_KEY` - Your OpenAI API key
- `OPENAI_MODEL` - Model to use (e.g., gpt-3.5-turbo, gpt-4)
- `WIKI_BASE_URL` - Your MediaWiki base URL (e.g., http://172.17.7.95/cswikiuat/index.php)

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
  "sources": [
    {"title": "Page1", "url": "http://wiki/index.php?title=Page1"},
    {"title": "Page2", "url": "http://wiki/index.php?title=Page2"}
  ],
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
├── openai_model.py     # OpenAI API wrapper
├── cli.py              # Command-line interface
├── index.html          # Web interface
├── requirements.txt    # Python dependencies
├── .env               # Your configuration (create from .env.example)
└── .env.example       # Example configuration
```

## How It Works

### RAG (Retrieval-Augmented Generation) Architecture

1. **Retrieval** → Searches for relevant wiki pages
   - Vector search (semantic similarity) if enabled
   - Falls back to keyword search
   - Returns top 3 most relevant pages

2. **Augmentation** → Builds context-enriched prompt
   - Combines retrieved documents with user question
   - Formats context with clear source references
   - Adds customer service agent instructions

3. **Generation** → LLM generates answer
   - Uses local Llama model
   - Answers based ONLY on provided context
   - Sources displayed as clickable links below the answer
   - Says "I don't know" when context lacks information

### Customer Service Agent Persona

The chatbot acts as a customer service agent that:
- ✅ Answers based ONLY on the provided wiki context
- ✅ Displays clickable source links to referenced wiki pages
- ✅ Says "I don't know based on the available information" when context is insufficient
- ✅ Never makes up information outside the provided context

## Configuration

All ports and settings are configured via `.env` file - **no hardcoded values**:

- `FLASK_PORT` - API server port (default: 5000)
- `WEB_SERVER_PORT` - Web UI server port (default: 8080)
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Database settings
- `OPENAI_API_KEY` - Your OpenAI API key
- `OPENAI_MODEL` - OpenAI model to use (default: gpt-3.5-turbo)
- `OPENAI_MAX_TOKENS` - Max tokens per response (default: 512)
- `OPENAI_TEMPERATURE` - Temperature for response generation (default: 0.7)
- `WIKI_BASE_URL` - Your MediaWiki base URL
- `USE_VECTOR_SEARCH` - Enable/disable vector search (True/False)
- `VECTOR_DB_PATH` - Vector database storage path

Shell scripts (`start.sh`, `stop.sh`, `status.sh`) automatically read ports from `.env`.

## Troubleshooting

### OpenAI API issues
- Ensure `OPENAI_API_KEY` is set correctly in `.env`
- Check your API quota at https://platform.openai.com/usage
- Verify the model name (gpt-3.5-turbo, gpt-4, etc.)

### Database connection issues
- Verify MariaDB is running
- Check credentials in `.env`
- Test connection: `mysql -h localhost -u wikiuser -p wikidb`

### Rate limiting
- OpenAI API has rate limits based on your plan
- Consider using gpt-3.5-turbo for faster/cheaper responses
- Implement caching for frequently asked questions

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

## Quick Start Scripts

Use the provided convenience scripts to manage the chatbot:

```bash
./start.sh    # Start the chatbot and web server
./stop.sh     # Stop all services
./restart.sh  # Restart all services
./status.sh   # Check service status
```

## Next Steps

- ✅ **Vector search**: Semantic embeddings for better context retrieval
- ✅ **Clickable source links**: Direct navigation to wiki pages
- **Chat history**: Implement conversation memory
- **Streaming**: Stream responses for better UX
- **Caching**: Cache frequent queries
- **Fine-tuning**: Fine-tune model on your wiki content

## License

MIT
