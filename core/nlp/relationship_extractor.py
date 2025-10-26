"""
Relationship extraction using dependency parsing.
"""
import re
from typing_extensions import Doc
import spacy
from typing import List, Dict
from config.config import NLP_CONFIG
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RelationshipExtractor:
    """Extract relationships between entities using spaCy."""
    def __init__(self):
        """Initialize spaCy model."""
        try:
            self.nlp = spacy.load(NLP_CONFIG["spacy_model"])
        except OSError:
            logger.error(f"spaCy model '{NLP_CONFIG['spacy_model']}' not found")
            raise RuntimeError(
                f"Please install spaCy model: python -m spacy download {NLP_CONFIG['spacy_model']}"
            )
    
    
    def extract_from_sentences(
        self,
        sentences: List[str],
        known_entities: Dict[str, str] = None
    ) -> List[Dict]:
        """
        Extract relationships from sentences.
        
        Args:
            sentences: List of sentences to process
            known_entities: Dict of entity_text -> entity_type
        
        Returns:
            List of relationship dicts with source, target, relationship, etc.
        """
        relationships = []

        
        for sentence in sentences:
            doc :Doc= self.nlp(sentence)
            
            # Method 1: Entity-aware pattern matching (BEST for accuracy)
            pattern_rels = self._extract_entity_patterns(sentence, known_entities)
            relationships.extend(pattern_rels)

            # Method 2: Dependency parsing with verb mapping
            verb_rels = self._extract_verb_relationships(doc, known_entities)
            relationships.extend(verb_rels)

            # Method 3: Prepositional relationships
            prep_rels = self._extract_prep_relationships(doc,sentence, known_entities)
            relationships.extend(prep_rels)
        
        return relationships
    
    
    # ---- ENTITY PATTERN EXTRACTION METHODS ----
    def _extract_entity_patterns(self, sentence: str, all_entities: dict) -> list:
        """Extract patterns using actual entity names (handles multi-word entities)."""
        relationships = []
        
        # Create entity list sorted by length (longest first to avoid partial matches)
        entity_names = sorted(all_entities.keys(), key=len, reverse=True)
        
        # Escape special regex characters in entity names
        def escape_entity(name):
            return re.escape(name)
        
        # Build patterns dynamically with actual entity names
        for source_entity in entity_names:
            for target_entity in entity_names:
                if source_entity == target_entity:
                    continue
                
                source_escaped = escape_entity(source_entity)
                target_escaped = escape_entity(target_entity)
                
                # Define relationship patterns
                patterns = [
                    # Ownership and founding
                    (rf'{source_escaped}\s+owns?\s+{target_escaped}', 'OWNS'),
                    (rf'{source_escaped}\s+(?:founded|established|created)\s+{target_escaped}', 'FOUNDED'),
                    
                    # Employment
                    (rf'{source_escaped}\s+works?\s+(?:at|for)\s+{target_escaped}', 'WORKS_AT'),
                    (rf'{source_escaped}\s+(?:is|was)\s+(?:a|an|the)?\s*(?:employee|engineer|developer|manager|director|ceo|cto|founder)\s+(?:at|of)\s+{target_escaped}', 'WORKS_AT'),
                    
                    # Management
                    (rf'{source_escaped}\s+(?:manages?|leads?|heads?|runs?|oversees?)\s+(?:the\s+)?{target_escaped}', 'MANAGES'),
                    (rf'{source_escaped}\s+(?:is|was)\s+(?:a|an|the)?\s*(?:manager|director|head|leader)\s+of\s+{target_escaped}', 'MANAGES'),
                    
                    # Reporting
                    (rf'{source_escaped}\s+reports?\s+to\s+{target_escaped}', 'REPORTS_TO'),
                    
                    # Collaboration
                    (rf'{source_escaped}\s+(?:collaborates?|works?|partners?)\s+with\s+{target_escaped}', 'COLLABORATES_WITH'),
                    (rf'{source_escaped}\s+(?:coordinates?|cooperates?)\s+with\s+{target_escaped}', 'COORDINATES_WITH'),
                    
                    # Products/Services
                    (rf'{source_escaped}\s+(?:has|produces?|manufactures?|makes?|develops?|offers?|provides?)\s+{target_escaped}', 'PRODUCES'),
                    (rf'{source_escaped}\s+(?:sells?|markets?)\s+{target_escaped}', 'SELLS'),
                    
                    # Location
                    (rf'{source_escaped}\s+(?:is\s+)?(?:located|based|headquartered)\s+(?:in|at)\s+{target_escaped}', 'LOCATED_IN'),
                    (rf'{source_escaped}\s+(?:has\s+)?(?:offices?|branches?)\s+(?:in|at)\s+{target_escaped}', 'HAS_OFFICE_IN'),
                    
                    # Employment history
                    (rf'{source_escaped}\s+(?:hired|employed|recruited)\s+{target_escaped}', 'HIRED'),
                    (rf'{source_escaped}\s+(?:interned?|worked)\s+(?:at|for|under)\s+{target_escaped}', 'INTERNED_AT'),
                    
                    # Relationships
                    (rf'{source_escaped}\s+(?:is|are)\s+(?:friends?|colleagues?)\s+(?:with|of)\s+{target_escaped}', 'FRIEND_WITH'),
                    
                    # Events
                    (rf'{source_escaped}\s+(?:attended|participated in|joined)\s+{target_escaped}', 'ATTENDED'),
                    (rf'{source_escaped}\s+(?:worked on|participated in)\s+(?:a\s+)?(?:project|initiative)\s+(?:with\s+)?{target_escaped}', 'WORKED_WITH'),
                ]
                
                for pattern, rel_type in patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        relationships.append({
                            "source": source_entity,
                            "relationship": rel_type,
                            "target": target_entity,
                            "sentence": sentence,
                            "source_type": all_entities.get(source_entity, "Entity"),
                            "target_type": all_entities.get(target_entity, "Entity")
                        })
        
        return relationships
    
    # ---- VERB RELATION EXTRACTION METHODS ----
    def _extract_verb_relationships(self, doc:Doc, sentence: str) -> List[Dict]:
        """Extract relationships based on verb dependencies."""
        relationships = []
        
        for token in doc:
            if token.pos_ == "VERB":
                # Find subject
                subjects = [child for child in token.children 
                           if child.dep_ in ("nsubj", "nsubjpass")]
                
                # Find objects
                objects = [child for child in token.children 
                          if child.dep_ in ("dobj", "pobj", "attr")]
                
                # Create relationships
                for subj in subjects:
                    for obj in objects:
                        subj_text = self._get_noun_phrase(subj)
                        obj_text = self._get_noun_phrase(obj)
                        
                        relationships.append({
                            "source": subj_text,
                            "relationship": token.lemma_.upper().replace(" ", "_"),
                            "target": obj_text,
                            "sentence": sentence,
                            "source_type": self._get_entity_type(subj),
                            "target_type": self._get_entity_type(obj)
                        })
        
        return relationships
    
    
    def _get_noun_phrase(self, token) -> str:
        """Extract full noun phrase from token."""
        for chunk in token.doc.noun_chunks:
            if token in chunk:
                return chunk.text
        return token.text
    
    
    def _get_entity_type(self, token) -> str:
        """Get entity type if token is part of an entity."""
        for ent in token.doc.ents:
            if token in ent:
                return ent.label_
        return "Entity"


    def _extract_prep_relationships(self, doc:Doc, sentence: str, all_entities: dict) -> list:
        """Extract prepositional relationships."""
        relationships = []
        
        for token in doc:
            if token.dep_ == "prep":
                # Get the object of the preposition
                pobj = None
                for child in token.children:
                    if child.dep_ == "pobj":
                        pobj = child
                        break
                
                if pobj:
                    head_text = self._get_noun_phrase(token.head)
                    obj_text = self._get_noun_phrase(pobj)
                    
                    # Only proceed if both are known entities
                    if head_text not in all_entities or obj_text not in all_entities:
                        continue
                    
                    if head_text.lower() == obj_text.lower():
                        continue
                    
                    rel_name = self._map_preposition_to_relationship(token.text, token.head.pos_)
                    
                    relationships.append({
                        "source": head_text,
                        "relationship": rel_name,
                        "target": obj_text,
                        "sentence": sentence,
                        "source_type": all_entities.get(head_text, "Entity"),
                        "target_type": all_entities.get(obj_text, "Entity")
                    })
        
        return relationships
    
    
    def _map_preposition_to_relationship(self, prep: str, head_pos: str) -> str:
        """Map prepositions to meaningful relationship names based on context."""
        prep = prep.lower()
        
        # Context-aware mapping
        if head_pos == "VERB":
            prep_mapping = {
                "at": "WORKS_AT",
                "for": "WORKS_FOR",
                "with": "COLLABORATES_WITH",
                "under": "REPORTS_TO",
                "to": "REPORTS_TO",
            }
        else:  # NOUN
            prep_mapping = {
                "at": "LOCATED_AT",
                "in": "LOCATED_IN",
                "of": "PART_OF",
                "with": "ASSOCIATED_WITH",
                "from": "FROM",
            }
        
        return prep_mapping.get(prep, f"RELATED_VIA_{prep.upper()}")
