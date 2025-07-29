# Caching Example

This example demonstrates different caching strategies using AIPrishtina VectorDB.

## Features
- Implementing different caching strategies
- Caching embeddings and search results
- Cache invalidation and management
- Performance monitoring

## Directory Structure
```
caching/
├── data/           # Sample data files
├── logs/           # Log files
└── main.py         # Main example code
```

## Usage
1. Run the example:
```bash
python main.py
```

2. Check the logs in `logs/caching.log` for detailed execution information.

## Caching Strategies
- File-based caching for embeddings
- Redis-based caching for search results
- In-memory LRU caching for frequently accessed data 