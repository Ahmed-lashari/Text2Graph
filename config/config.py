"""
Central configuration for Text2Graph application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
NLTK_DATA_DIR = DATA_DIR / "nltk_data"
SAMPLES_DIR = DATA_DIR / "samples"

# Create directories if they don't exist
for dir_path in [DATA_DIR, UPLOADS_DIR, NLTK_DATA_DIR, SAMPLES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Neo4j Configuration
NEO4J_CONFIG = {
    "NEO4J_URI": os.getenv("NEO4J_URI").replace("neo4j+s://", "neo4j+ssc://"),
    "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME"),
    "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
    # "NEO4J_DATABASE": os.getenv("NEO4J_DATABASE", "neo4j"),
}

# NLP Configuration
NLP_CONFIG = {
    "spacy_model": "en_core_web_sm",
    "spacy_model_path": PROJECT_ROOT / "config" / "models" / "en_core_web_sm",
    "nltk_data_path": str(NLTK_DATA_DIR),
    "required_nltk_packages": ["punkt_tab"],  # ONLY punkt_tab is needed
}

# File Processing Configuration
FILE_CONFIG = {
    "allowed_extensions": [".txt", ".csv", ".json"],
    "max_file_size_mb": 250,
    "encoding": "utf-8",
}

# UI Configuration
UI_CONFIG = {
    "page_title": "Text2Graph",
    "page_icon": "🧠",
    "layout": "wide",
    # "graph_height": "600px",
    # "graph_width": "100%",
}

# Logging Configuration
LOG_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": PROJECT_ROOT / "app.log",
}