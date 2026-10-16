import os
import json
import argparse
import time
from typing import List, Dict, Any
import fitz  # PyMuPDF
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class MultiColumnLayoutParser:
    """
    Parses complex multi-column document layouts by analyzing bounding box coordinates
    and sorting text blocks into human-natural reading order.
    """
    def __init__(self, column_threshold: float = 50.0):
        self.column_threshold = column_threshold

    def parse_page(self, page: fitz.Page) -> List[Dict[str, Any]]:
        blocks = page.get_text("dict")["blocks"]
        text_blocks = []

        for b in blocks:
            if b.get("type") == 0:  # Type 0 is text block
                for line in b["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text:
                            continue
                        # Bounding box: (x0, y0, x1, y1)
                        bbox = span["bbox"]
                        font_size = span["size"]
                        font_flags = span["flags"]
                        
                        text_blocks.append({
                            "text": text,
                            "bbox": bbox,
                            "font_size": round(font_size, 1),
                            "is_bold": bool(font_flags & 2**4),
                            "x0": bbox[0],
                            "y0": bbox[1],
                            "x1": bbox[2],
                            "y1": bbox[3]
                        })

        return self._sort_reading_order(text_blocks)

    def _sort_reading_order(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not blocks:
            return []

        # Sort roughly from top to bottom first
        blocks.sort(key=lambda b: b["y0"])

        # Group blocks into visual horizontal bands/columns to prevent multi-column interleaving
        columns = []
        for block in blocks:
            placed = False
            for col in columns:
                # If block falls within the horizontal boundaries of an existing column
                col_x0 = min(b["x0"] for b in col)
                col_x1 = max(b["x1"] for b in col)
                if not (block["x1"] < col_x0 - self.column_threshold or block["x0"] > col_x1 + self.column_threshold):
                    col.append(block)
                    placed = True
                    break
            if not placed:
                columns.append([block])

        # Sort columns left-to-right, and internal blocks top-to-bottom
        columns.sort(key=lambda col: min(b["x0"] for b in col))
        sorted_blocks = []
        for col in columns:
            col.sort(key=lambda b: (b["y0"], b["x0"]))
            sorted_blocks.extend(col)

        return sorted_blocks


class SemanticOutlineExtractor:
    """
    Uses local offline Sentence-Transformers combined with font heuristics
    to classify document elements into hierarchical outline trees (H1, H2, H3, Body).
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Loads model completely offline from local cache if available
        self.model = SentenceTransformer(model_name)
        
        # Anchor definitions for semantic role classification
        self.role_anchors = {
            "H1": "Major section title, executive summary, introduction, conclusion, primary chapter heading",
            "H2": "Subsection heading, methodology details, architectural breakdown, regional analysis",
            "H3": "Minor sub-heading, specific item list header, technical note header",
            "Body": "Detailed descriptive paragraph, extensive explanation, standard document body text"
        }
        self.anchor_embeddings = self.model.encode(list(self.role_anchors.values()))
        self.roles = list(self.role_anchors.keys())

    def classify_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not blocks:
            return []

        texts = [b["text"] for b in blocks]
        embeddings = self.model.encode(texts, show_progress_bar=False)
        
        # Calculate cosine similarity against structural anchor definitions
        sim_matrix = cosine_similarity(embeddings, self.anchor_embeddings)

        # Dynamic font size statistics for heuristic weighting
        font_sizes = [b["font_size"] for b in blocks]
        max_size = max(font_sizes) if font_sizes else 12.0
        avg_size = np.mean(font_sizes) if font_sizes else 12.0

        classified = []
        for idx, block in enumerate(blocks):
            sim_scores = sim_matrix[idx]
            best_role_idx = np.argmax(sim_scores)
            semantic_role = self.roles[best_role_idx]

            # Heuristic override: adjust semantic classification using layout metadata
            size = block["font_size"]
            if size >= max_size * 0.9 and len(block["text"].split()) < 10:
                final_role = "H1"
            elif size > avg_size * 1.15 and len(block["text"].split()) < 15:
                final_role = "H2" if semantic_role == "Body" else semantic_role
            elif size <= avg_size and not block["is_bold"]:
                final_role = "Body"
            else:
                final_role = semantic_role

            block["role"] = final_role
            classified.append(block)

        return classified

    def build_hierarchy(self, classified_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        outline = {"title": "Document Outline", "structure": []}
        
        current_h1 = None
        current_h2 = None

        for block in classified_blocks:
            role = block["role"]
            text = block["text"]

            if role == "H1":
                current_h1 = {"level": "H1", "title": text, "subsections": []}
                outline["structure"].append(current_h1)
                current_h2 = None
            elif role == "H2":
                node = {"level": "H2", "title": text, "subsections": []}
                if current_h1:
                    current_h1["subsections"].append(node)
                else:
                    outline["structure"].append(node)
                current_h2 = node
            elif role == "H3":
                node = {"level": "H3", "title": text}
                if current_h2:
                    current_h2["subsections"].append(node)
                elif current_h1:
                    current_h1["subsections"].append(node)
                else:
                    outline["structure"].append(node)
            # Body text is omitted because the output represents the document's structural outline.
            
        return outline


def run_pipeline(pdf_path: str, output_json: str):
    print(f"[*] Initializing Offline Document Analysis Engine...")
    start_time = time.time()
    
    if not os.path.exists(pdf_path):
        print(f"[!] Error: Input file '{pdf_path}' not found.")
        return
    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)
        print(f"[*] Loaded document with {total_pages} pages. Running multi-column layout parser...")

        layout_parser = MultiColumnLayoutParser()
        extractor = SemanticOutlineExtractor()

        all_blocks = []
        for page_num in range(total_pages):
            page = doc[page_num]
            sorted_blocks = layout_parser.parse_page(page)
            all_blocks.extend(sorted_blocks)

               print(f"[*] Extracted {len(all_blocks)} structural blocks. Performing semantic outline extraction...")
        classified_blocks = extractor.classify_blocks(all_blocks)
        hierarchical_outline = extractor.build_hierarchy(classified_blocks)
    elapsed_time = time.time() - start_time
    throughput = total_pages / elapsed_time if elapsed_time > 0 else 0

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(hierarchical_outline, f, indent=4)

    print(f"[*] Pipeline Execution Complete!")
    print(f"    - Processing Time: {elapsed_time:.2f} seconds")
    print(f"    - Inference Throughput: {throughput:.2f} pages/sec")
    print(f"    - Structural Outline saved to: {output_json}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Offline Document Analysis Engine")
    parser.add_argument("--input", type=str, default="sample.pdf", help="Path to input PDF document")
    parser.add_argument("--output", type=str, default="outline.json", help="Path to output JSON outline")
    args = parser.parse_args()

    run_pipeline(args.input, args.output)
