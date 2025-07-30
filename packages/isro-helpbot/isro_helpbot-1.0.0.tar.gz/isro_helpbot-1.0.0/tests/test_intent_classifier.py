# tests/test_intent_classifier.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from intent_classifier.intent_router import classify_intent

test_queries = {
    "What is INSAT-3D used for?": "info_query",
    "Download the latest monsoon report": "download",
    "Where is SCATSAT located?": "location_query",
    "I want satellite data for Bay of Bengal": "data_request",
    "Just checking something": "fallback"
}

def run_tests():
    print("\nRunning Intent Classification Tests:\n")
    for query, expected_intent in test_queries.items():
        predicted_intent = classify_intent(query)
        result = "✓" if predicted_intent == expected_intent else "✗"
        print(f"{result}  Query: {query}\n    → Expected: {expected_intent}, Got: {predicted_intent}\n")

if __name__ == "__main__":
    run_tests()
