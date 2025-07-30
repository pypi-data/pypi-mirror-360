# kg_builder/build_kg.py

import sys
import os
import pickle
import re

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kg_builder.text_preprocessor import preprocess_text
from kg_builder.entity_extractor import extract_entities
from kg_builder.relationship_mapper import extract_entity_pairs, build_knowledge_graph
from kg_builder.docx_pdf_parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_excel
)
from kg_builder.geospatial_extractor import extract_geospatial_entities
from isro_helpbot.config import DATA_DIR, GRAPH_DIR, KG_FILE
  # <--- Import paths from config

# --- Geospatial Triple Generator ---
def generate_geospatial_triples(text, geo_entities):
    triples = []
    satellites = ["INSAT-3D", "INSAT-3DR", "SCATSAT-1", "Megha-Tropiques"]
    relations = ["cover", "monitor", "observe", "track", "support", "scan", "map"]
    sentences = re.split(r'(?<=[.!?]) +', text)
    for sentence in sentences:
        for sat in satellites:
            if sat.lower() in sentence.lower():
                for geo in geo_entities:
                    if geo.lower() in sentence.lower():
                        found_relation = next((rel for rel in relations if rel in sentence.lower()), "relates_to")
                        triples.append((sat, found_relation, geo))
    return triples


def build_knowledge_graph_from_files():
    os.makedirs(GRAPH_DIR, exist_ok=True)
    all_pairs = []

    for filename in os.listdir(DATA_DIR):
        ext = filename.lower().split(".")[-1]
        path = os.path.join(DATA_DIR, filename)

        if ext == "txt":
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        elif ext == "pdf":
            text = extract_text_from_pdf(path)
        elif ext == "docx":
            text = extract_text_from_docx(path)
        elif ext == "xlsx":
            text = extract_text_from_excel(path)
        else:
            print(f"[!] Skipping unsupported file format: {filename}")
            continue

        if not text.strip():
            print(f"[!] Skipping empty or unreadable file: {filename}")
            continue

        cleaned_text = preprocess_text(text)
        pairs = extract_entity_pairs(cleaned_text)
        all_pairs.extend(pairs)

        geo_entities = extract_geospatial_entities(cleaned_text)
        geo_triples = generate_geospatial_triples(cleaned_text, geo_entities)
        all_pairs.extend(geo_triples)

        if geo_triples:
            print(f"  → [Geo] {len(geo_triples)} geo triples")

        if geo_entities:
            print(f" {filename}: Geospatial Entities Found → {geo_entities}")
            for location in geo_entities:
                all_pairs.append(("This Document", "mentions_location", location))

        print(f"[+] {filename}: {len(pairs)} entity pairs")

    G = build_knowledge_graph(all_pairs)

    with open(KG_FILE, "wb") as f:
        pickle.dump(G, f)

    print(f"[✓] Knowledge Graph saved to {KG_FILE}")


if __name__ == "__main__":
    build_knowledge_graph_from_files()
