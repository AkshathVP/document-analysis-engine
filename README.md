# Automated Document Analysis System

An end-to-end document processing pipeline for extracting document structure and generating hierarchical JSON outlines, with Docker support for network-independent inference.

## Key Features

- **PDF Structure Extraction:** Uses PyMuPDF to extract text, bounding-box coordinates, and font metadata from PDF documents.
- **Multi-Column Layout Parsing:** Applies spatial sorting based on text-block coordinates to reconstruct reading order across column-based layouts.
- **Semantic Classification:** Uses a locally cached Sentence-Transformer model combined with font-based heuristics to classify document elements into H1, H2, H3, and Body roles.
- **Hierarchical JSON Output:** Converts classified document elements into a nested JSON outline representing document structure.
- **Containerized Execution:** Provides a Docker environment with the Sentence-Transformer model cached during image creation for network-independent inference at runtime.

## Docker Usage

Build the Docker image:

```bash
docker build -t document-analysis-engine .

## Architecture & Workflow

1. **Geometry & Layout Extraction:** Uses `PyMuPDF (fitz)` to extract text blocks along with spatial coordinates `(x0, y0, x1, y1)` and font metadata.
2. **Multi-Column Sorting:** Groups text blocks into visual columns using bounding-box coordinates, then sorts columns left-to-right and text blocks top-to-bottom to reconstruct reading order.
3. **Structural Role Classification:** Uses a lightweight, locally cached `Sentence-Transformer` model (`all-MiniLM-L6-v2`) combined with font-size heuristics to classify text spans into structural document roles (`H1`, `H2`, `H3`, `Body`).
4. **JSON Outline Generation:** Assembles the classified nodes into a nested JSON tree representing the document's inferred structural hierarchy and reading flow.

## Project Structure
├── Dockerfile              # Container environment with cached Sentence-Transformer model
├── .dockerignore           # Excludes unnecessary files from Docker build context
├── requirements.txt        # Python dependencies
├── pipeline.py             # Core layout parsing and semantic extraction engine
└── README.md               # Project documentation
