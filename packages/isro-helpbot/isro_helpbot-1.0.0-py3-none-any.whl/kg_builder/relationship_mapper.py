

import spacy
import networkx as nx

nlp = spacy.load("en_core_web_sm")

def extract_entity_pairs(text):
    doc = nlp(text)
    entity_pairs = []

    for sent in doc.sents:
        subject = ""
        object_ = ""
        relation = ""

        for token in sent:
            # Extract subject
            if "subj" in token.dep_:
                subject = token.text

            # Extract object
            if "obj" in token.dep_:
                object_ = token.text

            # Get relation
            if token.dep_ == "ROOT":
                relation = token.lemma_

        if subject and object_ and relation:
            entity_pairs.append((subject, relation, object_))

    return entity_pairs

def build_knowledge_graph(entity_pairs):
    G = nx.DiGraph()
    for subj, rel, obj in entity_pairs:
        G.add_node(subj)
        G.add_node(obj)
        G.add_edge(subj, obj, label=rel)
    return G
import pickle
import os

GRAPH_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "graph", "knowledge_graph.pkl")

def query_knowledge_graph(user_query):
    if not os.path.exists(GRAPH_PATH):
        return ["Knowledge Graph not found."]
    
    with open(GRAPH_PATH, "rb") as f:
        G = pickle.load(f)

    results = []
    for node in G.nodes:
        if user_query.lower() in node.lower():
            neighbors = list(G.neighbors(node))
            for n in neighbors:
                edge_label = G.edges[node, n].get("label", "")
                results.append(f"{node} —[{edge_label}]→ {n}")
    
    return results if results else ["No relevant info found in Knowledge Graph."]
