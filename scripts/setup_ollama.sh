#!/bin/bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &

# Wait for service to start
sleep 15

# Pull the required model
ollama pull llama3.2:3b

# Keep connection alive for debugging if needed
echo "Ollama setup complete"
