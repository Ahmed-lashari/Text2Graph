"""
JSON file processor.
"""
import streamlit as st
import pandas as pd
import json
from typing import Tuple, Dict

from core.processor.base_processor import BaseProcessor
from utils.logger import setup_logger

logger = setup_logger(__name__)


class JSONProcessor(BaseProcessor):
    """Processor for JSON files."""
    
    def process(self) -> Tuple[pd.DataFrame, Dict]:
        """Process JSON file."""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("📄 Reading JSON file...")
            progress_bar.progress(20)
            
            # Try reading as JSON
            try:
                df = pd.read_json(self.file)
                progress_bar.progress(50)
            except ValueError:
                # If that fails, try loading and normalizing
                self.file.seek(0)
                data = json.load(self.file)
                progress_bar.progress(40)
                
                if isinstance(data, list):
                    df = pd.json_normalize(data)
                elif isinstance(data, dict):
                    df = pd.json_normalize(data, sep='_')
                else:
                    raise ValueError("Unsupported JSON structure")
                
                progress_bar.progress(60)
            
            # Clean data
            status_text.text("🧹 Cleaning data...")
            df = self._clean_dataframe(df)
            progress_bar.progress(80)
            
            # Generate summary
            summary = self._generate_summary(df)
            progress_bar.progress(100)
            
            status_text.text("✅ JSON processing complete!")
            progress_bar.empty()
            status_text.empty()
            
            return df, summary
            
        except Exception as e:
            logger.error(f"Error processing JSON: {e}", exc_info=True)
            progress_bar.empty()
            status_text.empty()
            raise ValueError(f"Failed to process JSON: {e}")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame for Neo4j compatibility."""
        import numpy as np
        
        # Replace NaN with None
        df = df.replace({np.nan: None})
        
        # Clean column names
        df.columns = df.columns.str.strip().str.replace('.', '_')
        
        return df