# Offline Document Analysis Engine

An end-to-end, completely offline document processing pipeline designed to extract structured, hierarchical outlines from dense, unstructured PDFs. Built to handle complex multi-column layouts without relying on external APIs or cloud OCR services.

## Key Features

- **PDF Structure Extraction:** Uses PyMuPDF to extract text, bounding-box coordinates, and font metadata from PDF documents.
- **Multi-Column Layout Parsing:** Applies spatial sorting based on text-block coordinates to reconstruct reading order across column-based layouts.
- **Semantic Classification:** Uses a locally cached Sentence-Transformer model combined with font-based heuristics to classify document elements into H1, H2, H3, and Body roles.
- **Hierarchical JSON Output:** Converts classified document elements into a nested JSON outline representing document structure.
- **Containerized Execution:** Provides a Docker environment with the Sentence-Transformer model cached during image creation for network-independent inference at runtime.

## Architecture & Workflow
1. **Geometry & Layout Extraction:** Uses `PyMuPDF (fitz)` to extract text blocks along with precise spatial coordinates `(x0, y0, x1, y1)` and font metadata.
2. **Multi-Column Sorting:** Implements a two-pass spatial sorting algorithm that groups text blocks into vertical columns and sorts them by reading order, preventing cross-column text merging.
3. **Semantic Hierarchy Classification:** Uses a lightweight, locally cached `Sentence-Transformer` model (`all-MiniLM-L6-v2`) combined with font-size heuristic weighting to classify text spans into structural document roles (`Title`, `H1`, `H2`, `H3`, `Body`).
4. **JSON Outline Generation:** Assembles the classified nodes into a nested JSON tree structure representing the document's true table of contents and reading flow.

## Project Structure
```text
├── Dockerfile              # Offline container environment with cached models
├── requirements.txt        # Lightweight Python dependencies
├── pipeline.py             # Core layout parsing and semantic extraction engine
└── README.md               # Documentation
