"""
Graph service - orchestrates all graph operations.
"""
import streamlit as st
from typing import Dict, Any
from streamlit.runtime.uploaded_file_manager import UploadedFile

from core.database.connection_manager import Neo4jConnectionManager
from core.processor.base_processor import ProcessorFactory
from services.graph_builder import GraphBuilder
from utils.logger import setup_logger
from utils.validators import validate_file

logger = setup_logger(__name__)


class GraphService:
    """Service for managing graph operations."""
    
    def __init__(self):
        """Initialize graph service with Neo4j connection."""
        self.connection_manager = Neo4jConnectionManager()
        self.driver = self.connection_manager.get_driver()
        self.graph_builder = GraphBuilder(self.driver)
    
    def show_connection_status(self):
        """Display connection status in sidebar with bottom developer credit."""
        with st.sidebar:
            st.markdown("### 🔗 Connection Status")
            if self.connection_manager.is_connected():
                st.success("Neo4j: Connected ✓")
                if st.button("🔄 Reconnect"):
                    self.connection_manager.reconnect()
                    st.rerun()
            else:
                st.error("Neo4j: Disconnected ✗")
                if st.button("🔌 Connect"):
                    self.connection_manager.connect()
                    st.rerun()

            # Flexible spacer
            st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)

            # Bottom developer credit
            st.markdown(
            """
            <div style="position:fixed; bottom:10px; width:230px; font-size:0.85em;">
                <strong>M.A. Lashari</strong><br>
                🎓 AI UnderGrad<br>
                📍 Pakistan<br>
                Exploring diverse tech stacks<br>
                <a href='YOUR_LINKEDIN_URL' target='_blank'>
                    <img src='https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white' />
                </a>
                <a href='YOUR_GITHUB_URL' target='_blank'>
                    <img src='https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white' />
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )


    
    def process_and_create_graph(
        self,
        uploaded_file: UploadedFile,
        clear_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Process file and create graph.
        
        Returns:
            Dict with success status, message, dataframe, summary, and graph_name
        """
        try:
            # Validate file
            validation = validate_file(uploaded_file)
            if not validation["valid"]:
                return {
                    "success": False,
                    "message": validation["error"]
                }
            
            # Get appropriate processor
            processor = ProcessorFactory.get_processor(uploaded_file)
            
            # Process file
            with st.spinner("Processing file..."):
                df, summary = processor.process()
            
            # Clear database if requested
            if clear_existing:
                with st.spinner("Clearing existing data..."):
                    self.graph_builder.clear_database()
            
            # Determine graph name
            graph_name = processor.get_graph_name()
            
            # Create graph
            with st.spinner(f"Creating graph: {graph_name}..."):
                status_text = st.empty()
                status_text.text("🗑️ Clearing previous graph...")
                self.graph_builder.create_app_graph(graph_name, df)
            
            return {
                "success": True,
                "message": f"Graph '{graph_name}' created successfully!",
                "dataframe": df,
                "summary": summary,
                "graph_name": graph_name
            }
            
        except Exception as e:
            logger.error(f"Error in process_and_create_graph: {e}", exc_info=True)
            return {
                "success": False,
                "message": str(e)
            }
    
    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, 'connection_manager'):
            self.connection_manager.close()
            
    def get_graph_stats(self) -> dict:
     """Get statistics about the graph."""
     with self.driver.session() as session:
        # Count nodes
        node_count :int= session.run("MATCH (n) RETURN count(n) as count").single()["count"]
        
        # Count relationships
        rel_count :int= session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
        
        # Count node types
        node_types :int= session.run("MATCH (n) RETURN count(DISTINCT labels(n)) as count").single()["count"]

        return {
            "nodes": node_count,
            "relationships": rel_count,
            "node_types": node_types
        }