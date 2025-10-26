"""
Entity extraction using spaCy.
"""
import spacy
from typing import List, Dict, Set
from config.config import NLP_CONFIG
from utils.logger import setup_logger

logger = setup_logger(__name__)


class EntityExtractor:
    """Extract named entities from text using spaCy."""
    
    def __init__(self):
        """Initialize spaCy model."""
        try:
            self.nlp = spacy.load(NLP_CONFIG["spacy_model"])
        except OSError:
            logger.error(f"spaCy model '{NLP_CONFIG['spacy_model']}' not found")
            raise RuntimeError(
                f"Please install spaCy model: python -m spacy download {NLP_CONFIG['spacy_model']}"
            )
    
    def extract_from_text(self, text: str) -> List[Dict[str, str]]:
        """
        Extract entities from text.
        
        Returns:
            List of dicts with 'text', 'label', 'start', 'end'
        """
        doc = self.nlp(text)
        
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        return entities
    
    def extract_from_sentences(self, sentences: List[str]) -> Dict[str, str]:
        """
        Extract unique entities from multiple sentences.
        
        Returns:
            Dict mapping entity text to entity type
        """
        entities = {}
        
        for sentence in sentences:
            doc = self.nlp(sentence)
            for ent in doc.ents:
                if ent.text not in entities:
                    entities[ent.text] = ent.label_
        
        return entities
    
    def get_entities_in_sentence(self, sentence: str) -> List[tuple]:
        """
        Get entities in a single sentence.
        
        Returns:
            List of (entity_text, entity_label) tuples
        """
        doc = self.nlp(sentence)
        return [(ent.text, ent.label_) for ent in doc.ents]