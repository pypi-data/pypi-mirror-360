# config.py

import os
# config.py

DATA_DIR = "data/clean_text"
GRAPH_DIR = "data/graph"
KG_FILE = f"{GRAPH_DIR}/knowledge_graph.pkl"

# Centralized paths for all modules

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Input text/PDF/Docx/Xlsx files
DATA_DIR = os.path.join(BASE_DIR, "data", "clean_text")

# Graph files
GRAPH_DIR = os.path.join(BASE_DIR, "data", "graph")
KG_FILE = os.path.join(GRAPH_DIR, "knowledge_graph.pkl")

# Evaluation output
EVAL_RESULTS_DIR = os.path.join(BASE_DIR, "evaluation", "results")
