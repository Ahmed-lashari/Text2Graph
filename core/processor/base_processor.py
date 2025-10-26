"""
Base processor and factory for file processing.
"""
from abc import ABC, abstractmethod
from typing import Tuple, Dict
import pandas as pd
from streamlit.runtime.uploaded_file_manager import UploadedFile
import re


class BaseProcessor(ABC):
    """Abstract base class for file processors."""
    
    def __init__(self, uploaded_file: UploadedFile):
        self.file = uploaded_file
        self.filename = uploaded_file.name
    
    @abstractmethod
    def process(self) -> Tuple[pd.DataFrame, Dict]:
        """Process file and return DataFrame and summary."""
        pass
    
    def get_graph_name(self) -> str:
        """Get intelligent graph name."""
        # Remove extension and clean filename
        name = self.filename.rsplit('.', 1)[0]
        clean_name = re.sub(r'[^a-zA-Z0-9_\s-]', '_', name)
        clean_name = re.sub(r'[_\s-]+', '_', clean_name)
        return clean_name or "Knowledge_Graph"
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict:
        """Generate summary statistics."""
        return {
            "rows": len(df),
            "columns": list(df.columns),
            "missing_values": int(df.isnull().sum().sum()),
            "file_type": self.filename.split('.')[-1].upper()
        }


class ProcessorFactory:
    """Factory for creating appropriate processors."""
    
    @staticmethod
    def get_processor(uploaded_file: UploadedFile) -> BaseProcessor:
        """Get appropriate processor based on file type."""
        from core.processor.text_processor import TextProcessor
        from core.processor.csv_processor import CSVProcessor
        from core.processor.json_processor import JSONProcessor
        
        filename = uploaded_file.name.lower()
        
        if filename.endswith('.txt'):
            return TextProcessor(uploaded_file)
        elif filename.endswith('.csv'):
            return CSVProcessor(uploaded_file)
        elif filename.endswith('.json'):
            return JSONProcessor(uploaded_file)
        else:
            raise ValueError(f"Unsupported file type: {filename}")