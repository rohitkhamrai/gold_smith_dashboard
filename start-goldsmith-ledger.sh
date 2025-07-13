#!/bin/bash

# Goldsmith Ledger Launcher for Mac/Linux
echo "========================================"
echo "    🏆 Goldsmith Ledger Launcher"
echo "========================================"
echo

# Check if the HTML file exists
if [ ! -f "goldsmith-ledger-offline.html" ]; then
    echo "❌ Error: goldsmith-ledger-offline.html not found!"
    echo "Please ensure the HTML file is in the same folder as this launcher."
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

echo "🔍 Looking for web browser..."

# Get the full path of the HTML file
HTML_FILE="file://$(pwd)/goldsmith-ledger-offline.html"

# Try different browsers based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "🍎 macOS detected"
    
    if command -v /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome &> /dev/null; then
        echo "✅ Opening with Google Chrome..."
        open -a "Google Chrome" --args --app="$HTML_FILE"
    elif command -v safari &> /dev/null; then
        echo "✅ Opening with Safari..."
        open -a Safari "$HTML_FILE"
    else
        echo "✅ Opening with default browser..."
        open "$HTML_FILE"
    fi
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "🐧 Linux detected"
    
    if command -v google-chrome &> /dev/null; then
        echo "✅ Opening with Google Chrome..."
        google-chrome --app="$HTML_FILE" &
    elif command -v chromium-browser &> /dev/null; then
        echo "✅ Opening with Chromium..."
        chromium-browser --app="$HTML_FILE" &
    elif command -v firefox &> /dev/null; then
        echo "✅ Opening with Firefox..."
        firefox "$HTML_FILE" &
    else
        echo "✅ Opening with default browser..."
        xdg-open "$HTML_FILE" &
    fi
else
    echo "✅ Opening with default browser..."
    xdg-open "$HTML_FILE" &
fi

echo
echo "🚀 Goldsmith Ledger is starting..."
echo "💡 Tip: Bookmark this page for easy access next time!"
echo
echo "Press Enter to close this window..."
read