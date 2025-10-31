"""
File uploader UI component.
"""
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from config.config import FILE_CONFIG

def render_file_uploader() -> UploadedFile | None:
    """
    Render file upload component.
    
    Returns:
        UploadedFile or None
    """
    st.title("🧩 Text2Graph File Uploader")
    st.write("Upload your data file to begin analysis and visualization.")

    # Info about supported types
    with st.expander("ℹ️ Accepted File Types"):
        st.info(f"You can upload **{', '.join(FILE_CONFIG['allowed_extensions'])}** files only.")
        st.write(f"**Maximum file size:** {FILE_CONFIG['max_file_size_mb']}MB")

    # File uploader
    uploaded_file: UploadedFile | None = st.file_uploader(
        "Drag & drop your file here or browse",
        type=[ext.replace('.', '') for ext in FILE_CONFIG['allowed_extensions']],
        accept_multiple_files=False,
        help=f"Only {', '.join(FILE_CONFIG['allowed_extensions'])} files are supported."
    )
    
    if uploaded_file is None:
        return None

    # Display success message
    filename: str = uploaded_file.name
    st.markdown(
        f"""
        <div style='
            background-color:#00BFA6;
            color:white;
            margin:10px 0px;
            padding:10px 16px;
            border-radius:8px;
            display:inline-block;
            font-weight:600;
        '>
            ✅ Uploaded file: {filename}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Show file info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
    with col2:
        st.metric("File Type", filename.split('.')[-1].upper())
    with col3:
        st.metric("Status", "✓ Ready")

    return uploaded_file