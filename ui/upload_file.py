import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile 


def detect_file() -> UploadedFile | None:
    st.title("🧩 Text2Graph File Uploader")
    st.write("Upload your data file to begin analysis and visualization.")

    # --- Info message about supported types ---
    with st.expander("ℹ️ Accepted File Types"):
        st.info("You can upload **.csv**, **.json**, or **.txt** files only.")
    

    # --- File uploader ---
    uploaded_file: UploadedFile | None = st.file_uploader(
        "Drag & drop your file here or browse",
        type= ["csv", "json", "txt"], 
        accept_multiple_files=False,
        help="Only .csv, .json, .txt files are supported."
    )
    
    if uploaded_file is None:
        return

    # --- Conditional logic ---
    
    filename: str = uploaded_file.name
    if filename.endswith((".csv", ".json", ".txt")):
        # Valid file
        st.markdown(
            f"""
            <div style='
                background-color:#00BFA6;
                color:white;
                margin:10px 16px;
                padding:10px 16px;
                border-radius:8px;
                display:inline-block;
                font-weight:600;
                margin-top:10px;
            '>
                ✅ Uploaded file: {filename}
            </div>
            """,
            unsafe_allow_html=True)
      
        # Placeholder for your next processing steps
        st.success("File accepted! Ready for text or graph processing.")
        return uploaded_file
    else:
        # Invalid file (shouldn't trigger normally due to `type` param)
        st.error("❌ Unsupported file type! Please upload .csv, .json, .txt files.")
        return None
    

    st.write("---")