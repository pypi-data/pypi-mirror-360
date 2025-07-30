# intent_classifier/intent_router.py

def classify_intent(user_query: str) -> str:
    query = user_query.lower()

    # Rule-based intent detection
    if any(keyword in query for keyword in ["what is", "define", "meaning", "explain", "used for"]):
        return "info_query"
    
    elif any(keyword in query for keyword in ["download", "get file", "fetch report", "save document"]):
        return "download"

    elif any(keyword in query for keyword in [
        "data", "satellite", "imagery", "weather", "rainfall", "temperature", 
        "precipitation", "humidity", "access data", "retrieve data", "ocean data", "monsoon data"
    ]):
        return "data_request"
    
    elif any(keyword in query for keyword in ["where is", "location of", "region", "area", "map"]):
        return "location_query"

    else:
        return "fallback"
