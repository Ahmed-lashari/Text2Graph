import re
import pandas as pd
from streamlit.runtime.uploaded_file_manager import UploadedFile

def get_app_name(df: pd.DataFrame, uploaded_file: UploadedFile) -> str:
    """
    Intelligently determine the best root name for the graph.
    
    Priority:
    1. For text data: Use most frequent entity or file name
    2. For structured data: Use name/title/id column if exists
    3. Fallback: Use filename without extension
    """
    
    # Check if this is text relationship data
    if 'source' in df.columns and 'target' in df.columns:
        # For text data, find the most central/frequent entity
        entities = pd.concat([df['source'], df['target']]).value_counts()
        if not entities.empty:
            most_common_entity = entities.index[0]
            return f"{most_common_entity}_Graph"
    
    # For structured data, look for common identifier columns
    name_columns = ['name', 'title', 'app_name', 'project', 'id', 'application']
    
    for col in name_columns:
        if col in df.columns:
            first_value = df[col].iloc[0]
            if pd.notna(first_value) and str(first_value).strip():
                return str(first_value)
    
    # Fallback: Use filename without extension
    filename_without_ext = uploaded_file.name.rsplit('.', 1)[0]
    # Clean the filename (replace special chars with underscores)
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', filename_without_ext)
    
    return clean_name