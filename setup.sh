#!/bin/bash

# GraphRAG Generator Setup Script

echo "🚀 Setting up GraphRAG Generator..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker from https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv graphrag-env

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source graphrag-env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing Python packages..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file..."
    cp .env.example .env
    echo "✏️  Please edit .env file and add your API keys."
fi

# Check if Memgraph is running
echo "🔍 Checking if Memgraph is running..."
if ! docker ps | grep -q memgraph; then
    echo "🐳 Starting Memgraph with Docker..."
    docker run -d --name memgraph -p 7687:7687 -p 7444:7444 -p 3000:3000 memgraph/memgraph-platform
    echo "⏳ Waiting for Memgraph to start..."
    sleep 10
else
    echo "✅ Memgraph is already running."
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Activate virtual environment: source graphrag-env/bin/activate"
echo "3. Start Jupyter Lab: jupyter lab"
echo "4. Open graphrag_tutorial.ipynb"
echo ""
echo "Or run the Python script directly:"
echo "python graphrag_script.py"
