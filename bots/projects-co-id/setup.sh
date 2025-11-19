#!/bin/bash
# Setup script for Projects.co.id scraper

echo "🚀 Setting up Projects.co.id Scraper..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browser
echo ""
echo "🌐 Installing Playwright Chromium browser..."
playwright install chromium

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure .env file is configured with credentials"
echo "2. Run: python scraper.py --pages 5"
echo "3. Check output in: data/scraped/projects-co-id/"

