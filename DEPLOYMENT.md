# OpenAI Branch Deployment Guide

## Overview
The `openai` branch uses OpenAI API instead of local Llama models for generating responses.

## Changes from Main Branch

### Files Modified:
1. **config.py** - Uses OPENAI_API_KEY instead of MODEL_PATH
2. **chatbot.py** - Imports `OpenAIModel` instead of `LlamaModel`
3. **requirements.txt** - Uses `openai>=1.0.0` instead of `llama-cpp-python`
4. **README.md** - Updated setup instructions for OpenAI
5. **.env.example** - New OpenAI configuration template

### Files Added:
1. **openai_model.py** - OpenAI API wrapper

## Setup Instructions

### 1. Install Dependencies
```bash
pip install openai pymysql flask flask-cors python-dotenv chromadb sentence-transformers
```

### 2. Configure .env File
Your .env is already configured with:
- Database: cs_wiki_poc on AWS RDS
- OpenAI API Key: Configured
- Model: gpt-3.5-turbo
- Ports: 5000 (API), 8080 (Web)

### 3. Start Services
```bash
./start.sh
```

### 4. Access the Chatbot
- Web UI: http://localhost:8080
- API: http://localhost:5000

## Testing
```bash
# Test OpenAI connection
python3 -c "from openai_model import OpenAIModel; m = OpenAIModel(); m.load_model(); print(m.generate_response('Test'))"
```

## Branch Information
- Branch: openai
- Repository: https://github.com/chchingyesstyle/cs_wiki_chatbot
- View branch: https://github.com/chchingyesstyle/cs_wiki_chatbot/tree/openai

## Advantages of OpenAI Branch
✅ No need to download large model files (GBs)
✅ Faster responses with GPT-3.5-turbo
✅ Better language understanding with GPT-4
✅ No GPU/CPU requirements for model inference
✅ Scalable without hardware constraints

## Cost Considerations
- GPT-3.5-turbo: ~$0.0005 per 1K tokens (cheap)
- GPT-4: ~$0.03 per 1K tokens (more expensive but better quality)
- Monitor usage at: https://platform.openai.com/usage
