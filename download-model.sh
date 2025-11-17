#!/bin/bash
# Download recommended LLM model for cs_wiki_chatbot

set -e

echo "========================================"
echo "Model Download Script"
echo "========================================"
echo ""

# Create models directory
mkdir -p models
cd models

# Check if model already exists
if [ -f "llama-2-7b-chat.Q4_K_M.gguf" ]; then
    echo "✓ Model already exists: llama-2-7b-chat.Q4_K_M.gguf"
    ls -lh llama-2-7b-chat.Q4_K_M.gguf
    echo ""
    echo "To re-download, delete the file first:"
    echo "  rm models/llama-2-7b-chat.Q4_K_M.gguf"
    exit 0
fi

echo "Recommended model: Llama-2-7B-Chat Q4_K_M"
echo "Size: ~4.1GB"
echo "Requirements: 8GB+ RAM"
echo ""

# Check available disk space
available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$available_space" -lt 10 ]; then
    echo "⚠️  Warning: Low disk space (${available_space}GB available)"
    echo "   At least 10GB recommended"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Downloading Llama-2-7B-Chat Q4_K_M..."
echo "This will take 5-15 minutes depending on your connection."
echo ""

# Download with wget (shows progress)
if command -v wget &> /dev/null; then
    wget -c https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf
elif command -v curl &> /dev/null; then
    curl -L -C - https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf -o llama-2-7b-chat.Q4_K_M.gguf
else
    echo "❌ Error: Neither wget nor curl found"
    echo "   Install wget: sudo yum install wget"
    exit 1
fi

echo ""
echo "========================================"
echo "✓ Download complete!"
echo "========================================"
echo ""
ls -lh llama-2-7b-chat.Q4_K_M.gguf
echo ""
echo "Model saved to: ./models/llama-2-7b-chat.Q4_K_M.gguf"
echo ""
echo "Next steps:"
echo "1. Configure .env file: cp .env.example .env"
echo "2. Build Docker images: ./docker-build.sh"
echo "3. Start services: ./docker-start.sh"
echo ""
