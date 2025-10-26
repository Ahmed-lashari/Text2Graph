"""
Text file processor with advanced NLP capabilities.
"""
import streamlit as st
import pandas as pd
from typing import Tuple, Dict
import re

from core.processor.base_processor import BaseProcessor
from core.nlp.entity_extractor import EntityExtractor
from core.nlp.relationship_extractor import RelationshipExtractor
from utils.text_utils import clean_text, tokenize_sentences
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TextProcessor(BaseProcessor):
    """Processor for text files with advanced relationship extraction."""
    
    def __init__(self, uploaded_file):
        super().__init__(uploaded_file)
        self.entity_extractor = EntityExtractor()
        self.relationship_extractor = RelationshipExtractor()
    
    def process(self) -> Tuple[pd.DataFrame, Dict]:
        """Process text file and extract entities/relationships."""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Read file
            status_text.text("📄 Reading text file...")
            text = self.file.read().decode("utf-8")
            progress_bar.progress(15)
            
            # Clean text
            status_text.text("🧹 Cleaning text...")
            text = clean_text(text)
            progress_bar.progress(25)
            
            # Tokenize sentences
            status_text.text("✂️ Tokenizing sentences...")
            sentences = tokenize_sentences(text)
            progress_bar.progress(35)
            
            # Extract entities first
            status_text.text("🔍 Extracting entities...")
            entities = self.entity_extractor.extract_from_sentences(sentences)
            progress_bar.progress(50)
            
            logger.info(f"Found {len(entities)} unique entities")
            
            # Extract relationships using multiple methods
            status_text.text("🔗 Extracting relationships...")
            relationships = []
            
            # Method 1: Entity-aware pattern matching (most accurate)
            for sent in sentences:
                pattern_rels = self._extract_entity_patterns(sent, entities)
                relationships.extend(pattern_rels)
            
            progress_bar.progress(65)
            
            # Method 2: Advanced dependency parsing
            dep_rels = self.relationship_extractor.extract_from_sentences(
                sentences, entities
            )
            relationships.extend(dep_rels)
            
            progress_bar.progress(80)
            
            # Build DataFrame
            df = pd.DataFrame(relationships)
            
            # Clean and deduplicate
            if not df.empty:
                df = self._clean_relationships(df)
                df = self._prioritize_relationships(df)
                df = self._enhance_entity_types(df, entities)
            
            progress_bar.progress(95)
            
            # Generate summary
            summary = self._generate_summary(df)
            summary["entities_found"] = len(entities)
            summary["relationships_found"] = len(df)
            summary["entity_types"] = self._count_entity_types(entities)
            
            status_text.text("✅ Processing complete!")
            progress_bar.progress(100)
            
            progress_bar.empty()
            status_text.empty()
            
            logger.info(f"Extracted {len(df)} relationships from {len(sentences)} sentences")
            
            return df, summary
            
        except Exception as e:
            logger.error(f"Error processing text: {e}", exc_info=True)
            progress_bar.empty()
            status_text.empty()
            raise
    
    def _extract_entity_patterns(self, sentence: str, entities: Dict[str, str]) -> list:
        """Extract patterns using actual entity names."""
        relationships = []
        
        # Sort entities by length (longest first) to avoid partial matches
        entity_names = sorted(entities.keys(), key=len, reverse=True)
        
        for source_entity in entity_names:
            for target_entity in entity_names:
                if source_entity == target_entity:
                    continue
                
                # Escape special regex characters
                source_escaped = re.escape(source_entity)
                target_escaped = re.escape(target_entity)
                
                # Comprehensive relationship patterns
                patterns = [
                    # Ownership & Founding
                    (rf'{source_escaped}\s+owns?\s+{target_escaped}', 'OWNS'),
                    (rf'{source_escaped}\s+(?:founded|established|created|started)\s+{target_escaped}', 'FOUNDED'),
                    
                    # Employment & Work
                    (rf'{source_escaped}\s+works?\s+(?:at|for|with)\s+{target_escaped}', 'WORKS_AT'),
                    (rf'{source_escaped}\s+(?:is|was)\s+(?:a|an|the)?\s*(?:employee|engineer|developer|analyst|consultant|specialist)\s+(?:at|of|for)\s+{target_escaped}', 'WORKS_AT'),
                    
                    # Management & Leadership
                    (rf'{source_escaped}\s+(?:manages?|leads?|heads?|runs?|oversees?|supervises?|directs?)\s+(?:the\s+)?{target_escaped}', 'MANAGES'),
                    (rf'{source_escaped}\s+(?:is|was)\s+(?:a|an|the)?\s*(?:manager|director|head|leader|supervisor|chief)\s+(?:of|at)\s+{target_escaped}', 'MANAGES'),
                    
                    # Reporting Structure
                    (rf'{source_escaped}\s+reports?\s+to\s+{target_escaped}', 'REPORTS_TO'),
                    (rf'{source_escaped}\s+works?\s+under\s+{target_escaped}', 'REPORTS_TO'),
                    
                    # Collaboration
                    (rf'{source_escaped}\s+(?:collaborates?|works?|partners?|cooperates?)\s+with\s+{target_escaped}', 'COLLABORATES_WITH'),
                    (rf'{source_escaped}\s+(?:and\s+)?{target_escaped}\s+(?:collaborate|work together|partner)', 'COLLABORATES_WITH'),
                    
                    # Team Coordination
                    (rf'{source_escaped}\s+(?:coordinates?|cooperates?)\s+with\s+(?:the\s+)?{target_escaped}', 'COORDINATES_WITH'),
                    (rf'(?:the\s+)?{source_escaped}\s+(?:often\s+)?coordinates?\s+with\s+(?:the\s+)?{target_escaped}', 'COORDINATES_WITH'),
                    
                    # Products & Services
                    (rf'{source_escaped}\s+(?:produces?|manufactures?|makes?|develops?|creates?)\s+{target_escaped}', 'PRODUCES'),
                    (rf'{source_escaped}\s+(?:has|offers?|provides?)\s+{target_escaped}', 'OFFERS'),
                    (rf'{source_escaped}\s+(?:sells?|markets?)\s+{target_escaped}', 'SELLS'),
                    
                    # Location
                    (rf'{source_escaped}\s+(?:is\s+)?(?:located|based|headquartered|situated)\s+(?:in|at)\s+{target_escaped}', 'LOCATED_IN'),
                    (rf'{source_escaped}\s+(?:has\s+)?(?:offices?|branches?|facilities?|locations?)\s+(?:in|at)\s+{target_escaped}', 'HAS_OFFICE_IN'),
                    
                    # Hiring & Employment
                    (rf'{source_escaped}\s+(?:hired|employed|recruited|brought on)\s+{target_escaped}', 'HIRED'),
                    (rf'{source_escaped}\s+recently\s+hired\s+{target_escaped}', 'HIRED'),
                    
                    # Internships & Training
                    (rf'{source_escaped}\s+(?:previously\s+)?(?:interned?|worked)\s+(?:at|for|under|with)\s+{target_escaped}', 'INTERNED_AT'),
                    (rf'{source_escaped}\s+(?:interned?|worked)\s+under\s+{target_escaped}', 'INTERNED_UNDER'),
                    
                    # Professional Relationships
                    (rf'{source_escaped}\s+(?:previously\s+)?worked\s+(?:with|alongside)\s+{target_escaped}', 'WORKED_WITH'),
                    (rf'{source_escaped}\s+(?:and\s+)?{target_escaped}\s+worked\s+(?:together\s+)?on\s+(?:a\s+)?(?:joint\s+)?project', 'WORKED_WITH'),
                    
                    # Events & Activities
                    (rf'{source_escaped}\s+(?:and\s+)?{target_escaped}\s+attended\s+(?:the\s+)?same\s+(?:workshop|conference|event|meeting)', 'ATTENDED_WITH'),
                    (rf'{source_escaped}\s+attended\s+{target_escaped}', 'ATTENDED'),
                    
                    # Membership
                    (rf'{source_escaped}\s+(?:is|was)\s+(?:a\s+)?(?:member|part)\s+of\s+{target_escaped}', 'MEMBER_OF'),
                    (rf'{source_escaped}\s+(?:joins?|joined)\s+{target_escaped}', 'JOINED'),
                ]
                
                for pattern, rel_type in patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        relationships.append({
                            "source": source_entity,
                            "relationship": rel_type,
                            "target": target_entity,
                            "sentence": sentence,
                            "source_type": entities.get(source_entity, "Entity"),
                            "target_type": entities.get(target_entity, "Entity"),
                            "confidence": "high"  # Pattern-based extraction is high confidence
                        })
        
        return relationships
    
    def _clean_relationships(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate relationships."""
        if df.empty:
            return df
        
        # Remove null relationships
        df = df[df['relationship'].notna() & (df['relationship'] != '')]
        
        # Remove self-referencing relationships
        df = df[df['source'].str.lower() != df['target'].str.lower()]
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['source', 'relationship', 'target'])
        
        # Normalize relationship names
        df['relationship'] = df['relationship'].str.upper().str.replace(' ', '_')
        
        return df
    
    def _prioritize_relationships(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove generic relationships if more specific ones exist."""
        if df.empty:
            return df
        
        # Define relationship hierarchy (generic to specific)
        generic_rels = {
            'CO_OCCURS': 1,
            'RELATED_TO': 2,
            'ASSOCIATED_WITH': 3,
            'CONNECTED_TO': 4,
            'HAS': 5,
            'OFFERS': 6,
        }
        
        # Group by source-target pairs
        result_rows = []
        for (source, target), group in df.groupby(['source', 'target']):
            # Sort by specificity (non-generic first)
            group['priority'] = group['relationship'].map(
                lambda x: generic_rels.get(x, 100)  # High priority for specific rels
            )
            
            # Take the most specific relationship
            best_rel = group.nlargest(1, 'priority')
            
            # Only keep if not too generic
            if best_rel.iloc[0]['priority'] > 1:
                result_rows.append(best_rel.iloc[0])
        
        if result_rows:
            result_df = pd.DataFrame(result_rows).drop('priority', axis=1)
            return result_df.reset_index(drop=True)
        
        return df
    
    def _enhance_entity_types(self, df: pd.DataFrame, entities: Dict[str, str]) -> pd.DataFrame:
        """Ensure all entities have proper types."""
        if df.empty:
            return df
        
        # Map entity types to more readable names
        type_mapping = {
            'PERSON': 'Person',
            'ORG': 'Organization',
            'GPE': 'Location',
            'LOC': 'Location',
            'DATE': 'Date',
            'TIME': 'Time',
            'MONEY': 'Money',
            'PRODUCT': 'Product',
            'EVENT': 'Event',
            'WORK_OF_ART': 'WorkOfArt',
            'FAC': 'Facility',
            'NORP': 'Group',
        }
        
        df['source_type'] = df['source_type'].map(
            lambda x: type_mapping.get(x, x if x else 'Entity')
        )
        df['target_type'] = df['target_type'].map(
            lambda x: type_mapping.get(x, x if x else 'Entity')
        )
        
        return df
    
    def _count_entity_types(self, entities: Dict[str, str]) -> Dict[str, int]:
        """Count entities by type."""
        type_counts = {}
        for entity_type in entities.values():
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        return type_counts
    
    def get_graph_name(self) -> str:
        """Get intelligent graph name from content."""
        return super().get_graph_name()