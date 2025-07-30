# SysGen

SysGen is a powerful CLI tool that creates high-quality synthetic datasets from documents using the Gemini API. It intelligently chunks documents, generates comprehensive questions, and produces detailed answers for machine learning training datasets.

## Features

- **Smart Document Chunking**: Automatically splits large documents into manageable chunks with overlap
- **Comprehensive Question Generation**: Extracts ALL possible questions from content using advanced AI prompting
- **High-Quality Answer Generation**: Creates detailed 4-5 sentence answers with supporting evidence
- **Multiple Output Formats**: Supports Alpaca, ChatML, and Conversation formats
- **Semantic Duplicate Detection**: Automatically removes duplicate questions using sentence embeddings
- **Token-Aware Processing**: Uses tiktoken for accurate token counting and chunking
- **Batch Processing**: Process multiple markdown/text files in a single run
- **Quality Validation**: Ensures answer length and content quality standards

## Installation

### Install from pip
```bash
pip install sysgen
```

### Set Up Environment Variables
Before running sysgen, set the API key in your terminal:
```bash
# Windows
set GEMINI_API_KEY=your_gemini_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_gemini_api_key_here
```

## Usage

### Basic Usage
```bash
sysgen --input-folder md --output dataset.json --format alpaca
```

### Advanced Usage
```bash
sysgen --input-folder documents --output training_data.json --format chatml --similarity-threshold 0.85
```

### Arguments

- `--input-folder`: Folder containing markdown/text files (default: `md`)
- `--output`: Output JSON file (default: `output.json`)
- `--format`: Output format - `alpaca`, `chatml`, or `conversation` (default: `alpaca`)
- `--similarity-threshold`: Similarity threshold for duplicate detection, 0.0-1.0 (default: `0.85`)

## Output Formats

### Alpaca Format
```json
{
  "instruction": "What is the main concept discussed in this section?",
  "input": "",
  "output": "The main concept discussed is the implementation of neural networks...",
  "source_document": "document.md"
}
```

### ChatML Format
```json
{
  "messages": [
    {"role": "user", "content": "What is the main concept discussed in this section?"},
    {"role": "assistant", "content": "The main concept discussed is the implementation of neural networks..."}
  ],
  "source_document": "document.md"
}
```

### Conversation Format
```json
{
  "conversations": [
    {"from": "human", "value": "What is the main concept discussed in this section?"},
    {"from": "gpt", "value": "The main concept discussed is the implementation of neural networks..."}
  ],
  "source_document": "document.md"
}
```

## How It Works

1. **Document Chunking**: Splits documents into 3000-token chunks with 200-token overlap
2. **Question Extraction**: Uses advanced AI prompting to extract ALL possible questions from each chunk
3. **Answer Generation**: Creates comprehensive 4-5 sentence answers with supporting evidence
4. **Quality Filtering**: Validates answer length (3-6 sentences) and content quality
5. **Duplicate Detection**: Uses sentence embeddings to identify semantically similar questions
6. **Format Conversion**: Converts to specified output format (Alpaca/ChatML/Conversation)
7. **Batch Processing**: Processes multiple files and combines results

## Advanced Features

### Smart Chunking
- **Token-Aware**: Uses tiktoken for accurate token counting
- **Sentence Preservation**: Keeps sentences intact during chunking
- **Overlap Management**: Maintains context between chunks with configurable overlap

### Comprehensive Question Generation
- **Multi-Level Questions**: Generates factual, conceptual, analytical, and application questions
- **Exhaustive Extraction**: Extracts ALL possible questions from content
- **Quality Standards**: Ensures questions are clear, specific, and answerable

### Semantic Duplicate Detection
- **Embedding-Based**: Uses sentence-transformers for semantic similarity
- **Configurable Threshold**: Adjust sensitivity with similarity_threshold parameter
- **Quality Preservation**: Keeps highest quality version from duplicate groups

## Dependencies

- `google-genai`: Gemini API client for question and answer generation
- `sentence-transformers`: Semantic similarity detection for duplicate removal
- `scikit-learn`: Cosine similarity calculations
- `tiktoken`: Token counting for document chunking
- `torch`: PyTorch backend for sentence transformers
- `transformers`: Hugging Face transformers library
- `numpy`: Numerical operations
- `scipy`: Scientific computing utilities

## Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

### How to Contribute

1. **Fork the Repository**: Start by forking the project on GitHub
2. **Clone the Repository**: Clone it to your local machine
3. **Create a Branch**: Create a new branch for your changes
4. **Make Changes**: Implement your improvements or bug fixes
5. **Test Your Changes**: Ensure the tool works correctly with your modifications
6. **Submit a Pull Request**: Open a PR describing your changes

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contact

- **Author**: [Adhishtanaka](https://github.com/Adhishtanaka)
- **Email**: kulasoooriyaa@gmail.com