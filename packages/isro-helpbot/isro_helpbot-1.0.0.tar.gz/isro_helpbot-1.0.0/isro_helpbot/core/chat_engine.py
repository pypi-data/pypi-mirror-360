# core/chat_engine.py

from api.query_handler import answer_query
from kg_builder.build_kg import build_knowledge_graph_from_files
import os

def process_user_query(query: str, chat_history: list):
    response = answer_query(query, chat_history)
    return response["llm_response"]

def update_knowledge_graph(files, data_dir: str):
    os.makedirs(data_dir, exist_ok=True)
    for file in files:
        with open(os.path.join(data_dir, file.filename), "wb") as f:
            f.write(file.file.read())
    build_knowledge_graph_from_files()
