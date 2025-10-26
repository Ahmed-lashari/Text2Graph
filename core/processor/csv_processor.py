"""
CSV file processor.
"""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Tuple, Dict

from core.processor.base_processor import BaseProcessor
from utils.logger import setup_logger

logger = setup_logger(__name__)


class CSVProcessor(BaseProcessor):
    """Processor for CSV files."""
    
    def process(self) -> Tuple[pd.DataFrame, Dict]:
        """Process CSV file."""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("📄 Reading CSV file...")
            progress_bar.progress(20)
            
            # Read CSV with error handling
            try:
                df = pd.read_csv(self.file, encoding='utf-8')
            except UnicodeDecodeError:
                # Try different encoding if UTF-8 fails
                self.file.seek(0)
                df = pd.read_csv(self.file, encoding='latin-1')
            
            progress_bar.progress(60)
            
            # Clean data
            status_text.text("🧹 Cleaning data...")
            df = self._clean_dataframe(df)
            progress_bar.progress(80)
            
            # Generate summary
            summary = self._generate_summary(df)
            progress_bar.progress(100)
            
            status_text.text("✅ CSV processing complete!")
            progress_bar.empty()
            status_text.empty()
            
            return df, summary
            
        except Exception as e:
            logger.error(f"Error processing CSV: {e}", exc_info=True)
            progress_bar.empty()
            status_text.empty()
            raise ValueError(f"Failed to process CSV: {e}")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame for Neo4j compatibility."""
        # Replace various null representations with None
        df = df.replace({
            np.nan: None,
            'nan': None,
            'NaN': None,
            'null': None,
            'NULL': None,
            '': None
        })
        
        # Clean column names - safely handle all column types
        df.columns = [str(col).strip().replace(' ', '_') for col in df.columns]
        
        # Clean values in each column
        for col in df.columns:
            # Only process object (string) columns
            if df[col].dtype == 'object':
                df[col] = self._safe_strip_strings(df[col])
        
        return df
    
    def _safe_strip_strings(self, series: pd.Series) -> pd.Series:
        """Safely strip strings from a pandas Series."""
        def strip_if_string(val):
            if val is None or pd.isna(val):
                return None
            if isinstance(val, str):
                stripped = val.strip()
                # Return None for empty strings
                return stripped if stripped else None
            return val
        
        return series.apply(strip_if_string)
    
    def get_graph_name(self) -> str:
        """Get graph name from CSV data if possible."""
        return super().get_graph_name()