# AIPrishtina VectorDB Examples

This directory contains example scripts demonstrating various features and use cases of the AIPrishtina VectorDB library.

## Basic Examples

- `basic_text_search.py`: Simple text search using different embedding models
- `basic_image_search.py`: Image similarity search with CLIP embeddings
- `basic_audio_search.py`: Audio file search using audio embeddings
- `basic_video_search.py`: Video search with frame extraction and embeddings

## Advanced Examples

- `advanced_hybrid_search.py`: Combining text and image search
- `advanced_streaming.py`: Streaming data processing and indexing
- `advanced_caching.py`: Implementing caching for better performance
- `advanced_metrics.py`: Collecting and analyzing search metrics

## API Examples

- `api_text_search.py`: Using the text search API
- `api_image_search.py`: Using the image search API
- `api_hybrid_search.py`: Using the hybrid search API
- `api_streaming.py`: Using the streaming API

## Configuration Examples

- `config_basic.py`: Basic configuration setup
- `config_advanced.py`: Advanced configuration options
- `config_custom.py`: Custom configuration examples

## Docker Examples

- `docker_basic.py`: Basic Docker setup
- `docker_advanced.py`: Advanced Docker configuration
- `docker_compose.py`: Docker Compose setup

## Running the Examples

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run any example script:
```bash
python examples/basic_text_search.py
```

## Configuration

The examples use configuration files located in the `examples/config` directory:
- `config.ini`: Basic configuration
- `config.yaml`: Advanced configuration
- `config.json`: Custom configuration

## Notes

- All examples include logging to help understand the process
- Examples use sample data that is generated automatically
- Each example demonstrates different features and use cases
- Examples can be modified to suit specific needs

## Contributing

Feel free to contribute more examples or improve existing ones. Please follow the same structure and include proper documentation.

## Directory Structure
```
examples/
├── recommendation_system/  # Recommendation system example
│   ├── main.py            # Main implementation
│   ├── data/              # Sample data directory
│   ├── logs/              # Log files
│   └── README.md          # Example documentation
└── README.md              # This file
```

## Running Examples
Each example can be run independently. Navigate to the example directory and run:
```bash
python main.py
```

## Features
- Content-based recommendation system
- User preference modeling
- Similarity-based recommendations
- Hybrid recommendation approaches
- Comprehensive logging
- Error handling and validation

## Requirements
- Python 3.8+
- AIPrishtina VectorDB
- ChromaDB
- Additional dependencies as specified in each example

## Logging
All examples use the AIPrishtinaLogger for consistent logging across the application. Log files are stored in the `logs` directory of each example.

## Data Management
- Sample data is generated automatically when running the examples
- Data is stored in JSON format in the `data` directory
- Vector embeddings are managed by ChromaDB

## Error Handling
The examples include comprehensive error handling for:
- Database operations
- Data validation
- User input processing
- File operations 