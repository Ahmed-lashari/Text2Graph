"""
Graph visualization component using PyVis.
"""
from neo4j import Driver
import streamlit as st
from pyvis.network import Network
from pathlib import Path
# from config.config import UI_CONFIG
from services.graph_service import GraphService
from utils.logger import setup_logger


logger = setup_logger(__name__)


def render_graph_visualization(graph_service:GraphService,graph_name: str):
    """
    Render graph visualization.
    
    Args:
        graph_service: GraphService instance
        graph_name: Name of the graph to visualize
    """
    st.markdown("---")
    st.markdown(f"### 🎨 Graph Visualization: {graph_name}")
    
    try:
        with st.spinner("Generating graph visualization..."):
            # Create PyVis network
            net = Network(
                # height=UI_CONFIG["graph_height"],
                # width=UI_CONFIG["graph_width"],
                notebook=True,
                bgcolor="#ffffff",
                font_color="#000000"
            )
            
            # Configure physics
            net.set_options("""
            {
                "physics": {
                    "enabled": true,
                    "barnesHut": {
                        "gravitationalConstant": -8000,
                        "centralGravity": 0.3,
                        "springLength": 95,
                        "springConstant": 0.04
                    }
                },
                "nodes": {
                    "borderWidth": 2,
                    "borderWidthSelected": 4,
                    "font": {
                        "size": 14,
                        "face": "arial"
                    }
                },
                "edges": {
                    "color": {
                        "inherit": true
                    },
                    "smooth": {
                        "type": "continuous"
                    }
                }
            }
            """)
            
            # Add graph data
            
            graph_service.graph_builder.add_to_pyvis(net)
            
            # Save and display
            html_file = "graph.html"
            net.show(html_file)
            
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            st.components.v1.html(html_content, height=600, scrolling=True)
            
            # Display statistics
            _display_graph_stats(graph_service)
            
    except Exception as e:
        logger.error(f"Error visualizing graph: {e}", exc_info=True)
        st.error(f"❌ Error visualizing graph: {e}")


def _display_graph_stats(graph_service: GraphService):
    """Display graph statistics."""
    try:
        stats = graph_service.get_graph_stats()
        
        st.markdown("#### 📊 Graph Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Nodes", stats.get("nodes", 0))
        with col2:
            st.metric("Total Relationships", stats.get("relationships", 0))
        with col3:
            st.metric("Node Types", stats.get("node_types", 0))
            
    except Exception as e:
        logger.warning(f"Could not fetch graph stats: {e}")