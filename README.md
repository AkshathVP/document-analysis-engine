# Automated Document Analysis System

An end-to-end Python pipeline that extracts document structure from PDF files and generates hierarchical JSON outlines. The system combines PDF geometry, font metadata, Sentence-Transformer embeddings, and layout heuristics.

## Key Features

- **PDF Structure Extraction:** Extracts text, bounding boxes, font sizes, and formatting metadata using PyMuPDF.
- **Multi-Column Parsing:** Uses spatial coordinates to reconstruct an approximate reading order across columns.
- **Structural Classification:** Uses `all-MiniLM-L6-v2` Sentence-Transformer embeddings with font and layout heuristics to classify text as `H1`, `H2`, `H3`, or `Body`.
- **Hierarchical JSON:** Converts detected document structure into a nested JSON outline.
- **Docker Support:** Provides a reproducible environment with the Sentence-Transformer model cached during image creation.

## Architecture

```text
PDF
 │
 ▼
PyMuPDF Extraction
 │
 ├── Text
 ├── Bounding Boxes
 ├── Font Size
 └── Font Style
 │
 ▼
Multi-Column Layout Ordering
 │
 ▼
Sentence-Transformer Embeddings
 │
 ▼
Cosine Similarity + Layout Heuristics
 │
 ▼
H1 / H2 / H3 / Body
 │
 ▼
Hierarchical JSON
```

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core pipeline |
| PyMuPDF | PDF extraction |
| Sentence-Transformers | Semantic representation |
| all-MiniLM-L6-v2 | Structural role inference |
| scikit-learn | Cosine similarity |
| NumPy | Numerical processing |
| Docker | Containerized execution |

## Project Structure

```text
document-analysis-engine/
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── pipeline.py
└── README.md
```

## Local Usage

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run

```bash
python pipeline.py --input path/to/input.pdf --output outline.json
```

The resulting hierarchical structure is saved as a JSON file.

## Docker Usage

### Build

```bash
docker build -t document-analysis-engine .
```

### Run

Place your PDF inside `input_docs/`, then run:

```bash
docker run --rm \
  -v "$(pwd)/input_docs:/app/input_docs" \
  -v "$(pwd)/output:/app/output" \
  document-analysis-engine \
  python pipeline.py \
  --input /app/input_docs/sample.pdf \
  --output /app/output/outline.json
```

The generated JSON will be available in the local `output/` directory.



The system uses a combination of:

- Bounding-box based layout analysis
- Font-size and formatting heuristics
- Sentence-Transformer embeddings
- Cosine similarity against predefined structural role descriptions

The classifier is not trained on a labelled document dataset. Complex layouts may require additional layout rules, and scanned PDFs may require OCR before processing.



