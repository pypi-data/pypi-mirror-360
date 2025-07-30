# kg_builder/geospatial_extractor.py
import spacy

# Load the spaCy English model (should already be downloaded via requirements.txt)
nlp = spacy.load("en_core_web_sm")

def extract_geospatial_entities(text):
    """
    Extract geospatial entities like countries, cities, oceans, coordinates, etc.
    """
    doc = nlp(text)
    locations = []

    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:  # GPE = Geo-political entity, LOC = non-GPE location
            locations.append(ent.text)

    return list(set(locations))  # Remove duplicates
