"""
Main Streamlit application entry point.
Minimal code - delegates to services and UI components.
"""
import streamlit as st
from config.config import UI_CONFIG
st.set_page_config(**UI_CONFIG)
from services.graph_service import GraphService
from ui.components.file_uploader import render_file_uploader
from ui.components.graph_visualizer import render_graph_visualization
from utils.logger import setup_logger

# Setup
logger = setup_logger(__name__)


def main():
    """Main application flow."""
    st.title("🧠 Text2Graph - Knowledge Graph Generator")
    
    # Initialize graph service (handles Neo4j connection)
    graph_service = GraphService()
    
    # Show connection status
    graph_service.show_connection_status()
    
    # File upload section
    uploaded_file = render_file_uploader()
    
    if uploaded_file is None:
        st.info("👆 Upload a file to begin")
        return
    
    # Processing section
    st.markdown("### 🧠 Ready to Process Your Data")
    st.markdown(f"**Uploaded File:** {uploaded_file.name}")
    
    # Options
    # col1, col2 = st.columns([3, 1])
    # with col2:
    #     clear_db = st.checkbox("Clear old data", value=True)
    
    # Process button
    if st.button("🚀 Start Processing", type="primary"):
        try:
            # Process and create graph
            result = graph_service.process_and_create_graph(
                uploaded_file=uploaded_file,
                # clear_existing=clear_db
            )
            
            if result["success"]:
                # Show summary
                st.success(f"✅ {result['message']}")
                st.write("**Summary:**", result["summary"])
                st.dataframe(result["dataframe"].head())
                
                # Visualize graph
                render_graph_visualization(
                    graph_service=graph_service,
                    graph_name=result["graph_name"]
                )
            else:
                st.error(f"❌ {result['message']}")
                
        except Exception as e:
            logger.error(f"Error in main flow: {e}", exc_info=True)
            st.error(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    main()