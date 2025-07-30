# intent_classifier/intent_predictor.py

import re

INTENTS = {
    "weather": ["rainfall", "temperature", "forecast", "monsoon", "humidity", "climate", "weather"],
    "download": ["download", "get", "access", "data", "retrieve", "obtain"],
    "info_query": ["tell me", "about", "information", "describe", "what is", "who is", "name of", "full name", "details of"],
    "location_query": ["where", "located", "location", "region", "place", "area"],
    "data_request": ["graph", "chart", "plot", "visualize", "trend", "analysis"],
    "factual_name": ["name of", "full name", "who is", "chairman", "director", "chief"],
}

def predict_intent(query):
    query_lower = query.lower().strip()

    # Rule-based intent detection using keyword match
    for intent, keywords in INTENTS.items():
        if any(kw in query_lower for kw in keywords):
            return intent

    # Fallback if nothing matches
    return "fallback"
