#!/bin/bash
# Proxmox Backup Checker Setup Script

set -e

echo "🚀 Setting up Proxmox Backup Checker..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p var log examples
mkdir -p ~/etc

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source .venv/bin/activate
pip install -r requirements.txt

# Copy example configuration if it doesn't exist
if [ ! -f "var/config.yaml" ]; then
    echo "⚙️ Creating example configuration..."
    cp var/example_config.yaml var/config.yaml
    echo "✏️  Please edit var/config.yaml with your backup directories"
fi

# Copy example environment files
echo "🔐 Setting up example credential files..."

if [ ! -f "~/etc/smtp.env" ]; then
    cp examples/grsrv03.env.example ~/etc/smtp.env.example
    echo "✏️  Example SMTP config created at ~/etc/smtp.env.example"
    echo "    Copy to ~/etc/smtp.env and configure with your SMTP settings"
fi

if [ ! -f "~/etc/pushover.env" ]; then
    cp examples/pushover.env.example ~/etc/pushover.env.example
    echo "✏️  Example Pushover config created at ~/etc/pushover.env.example"
    echo "    Copy to ~/etc/pushover.env and configure with your Pushover credentials"
fi

# Test configuration
echo "🧪 Testing configuration..."
source .venv/bin/activate

echo "Testing configuration file..."
if [ -f "var/config.yaml" ]; then
    if python3 -c "from python_utils import parse_config_file; parse_config_file('var/config.yaml')" 2>/dev/null; then
        echo "✅ Configuration file is valid"
    else
        echo "❌ Configuration file has errors - please check var/config.yaml"
    fi
else
    if python3 -c "from python_utils import parse_config_file; parse_config_file('var/example_config.yaml')" 2>/dev/null; then
        echo "✅ Example configuration file is valid"
    else
        echo "❌ Example configuration file has errors"
    fi
fi

echo "Testing python_utils import..."
if python3 -c "from python_utils import *" 2>/dev/null; then
    echo "✅ Python utilities loaded successfully"
else
    echo "❌ Error loading python utilities"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit var/config.yaml with your backup directories"
echo "2. Configure SMTP credentials in ~/etc/smtp.env"
echo "3. (Optional) Configure Pushover credentials in ~/etc/pushover.env"
echo "4. Test run: source .venv/bin/activate && python main.py"
echo "5. Add to cron: 0 6 * * * cd $(pwd) && $(pwd)/.venv/bin/python main.py"
echo ""
echo "For help, see: README.md"