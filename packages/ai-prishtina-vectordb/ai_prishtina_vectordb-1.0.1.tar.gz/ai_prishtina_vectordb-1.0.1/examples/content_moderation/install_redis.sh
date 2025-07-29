#!/bin/bash

# Install the redis Python package
pip install --upgrade redis

# Optionally install Redis server if on macOS and Homebrew is available
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &> /dev/null; then
        echo "Installing Redis server with Homebrew..."
        brew install redis
        echo "To start Redis server: brew services start redis"
    else
        echo "Homebrew not found. Please install Redis server manually if needed."
    fi
else
    echo "If you need the Redis server, please install it using your system's package manager."
fi

echo "Redis Python package installation complete." 