import spacy
from kg_builder.text_preprocessor import preprocess_text

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Custom ISRO-related keywords for rule-based matching
ISRO_ENTITIES = [
    "insat", "insat-3d", "megha-tropiques", "scatsat",
    "ocean report", "rainfall data", "cyclone imagery",
    "weather data", "satellite imagery", "mars mission",
    "moon mission", "gaganyaan", "earth observation",
    "launch vehicle", "pslv", "gslv", "data archive"
]

def extract_entities(text):
    # Step 1: Clean and normalize the input
    text = preprocess_text(text).lower()

    # Step 2: Apply spaCy NER
    doc = nlp(text)
    entities = [(ent.text.strip().lower(), ent.label_) for ent in doc.ents]

    # Step 3: Add rule-based entities if matched
    for keyword in ISRO_ENTITIES:
        if keyword in text:
            if keyword not in [e[0] for e in entities]:  # avoid duplicates
                entities.append((keyword, "ISRO_ENTITY"))

    return entities
