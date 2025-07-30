def generate_response(intent, entities):
    if intent == "info_query":
        response = f"[Info] {'; '.join(e[0] for e in entities)}"
    elif intent == "location_query":
        response = f"[Location] {'; '.join(e[0] for e in entities)}"
    elif intent == "data_request":
        response = f"[Data Access] {'; '.join(e[0] for e in entities)}"
    elif intent == "download":
        response = f"[Download Link] {'; '.join(e[0] for e in entities)}"
    else:
        response = "Sorry, I didn't understand your request."
    return {"answer": response, "entities": entities}
