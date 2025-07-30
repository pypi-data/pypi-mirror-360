# api/query_handler.py

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from intent_classifier.intent_predictor import predict_intent
from kg_builder.relationship_mapper import query_knowledge_graph

import openai
import dotenv
import time

# ---- Load API Key ----
dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---- LLM Fallback ----
def query_llm(prompt, history=None):
    try:
        messages = [{"role": "system", "content": "You are a helpful assistant for answering ISRO-related queries."}]
        
        # Add past messages as chat history context
        if history:
            for user_msg, bot_msg in history[-5:]:  # keep last 5 messages for context
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": bot_msg})
        
        # Add current user message
        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.3,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[LLM Error] {e}"


def answer_query(user_query, history=None):
    print(f"[*] Received query: {user_query}")

    intent = predict_intent(user_query)
    print(f"[+] Predicted Intent: {intent}")

    kg_results = query_knowledge_graph(user_query)

    if kg_results and kg_results[0] != "No relevant info found in Knowledge Graph.":
        llm_response = "\n".join(kg_results[:3])
    else:
        llm_response = query_llm(user_query, history)

    return {
        "intent": intent,
        "llm_response": llm_response,
        "kg_response": kg_results
    }

