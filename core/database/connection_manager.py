"""
Neo4j connection manager with session state integration.
"""
import streamlit as st
from neo4j import GraphDatabase, Driver
from typing import Optional
from config.config import NEO4J_CONFIG
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Neo4jConnectionManager:
    """Manages Neo4j driver lifecycle using Streamlit session state."""
    
    def __init__(self):
        """Initialize connection manager."""
        if 'neo4j_driver' not in st.session_state:
            self.connect()
    
    def connect(self) -> Driver:
        """Establish Neo4j connection."""
        try:
            uri = NEO4J_CONFIG["NEO4J_URI"]
            user = NEO4J_CONFIG["NEO4J_USERNAME"]
            password = NEO4J_CONFIG["NEO4J_PASSWORD"]

            logger.info(f"Connecting to Neo4j at: {uri}")
            logger.info(f"Using username: {user}")

            if not password:
                raise ValueError("Neo4j password is empty. Check your .env file.")

            driver: Driver = GraphDatabase.driver(
                uri,
                auth=(user, password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_timeout=30
            )

            # Test connection
            logger.info("Testing connection...")
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()

            st.session_state.neo4j_driver = driver
            logger.info("✅ Neo4j connection established successfully")

            return driver

        except ValueError as ve:
            logger.error(f"Configuration error: {ve}")
            st.error(f"⚠️ Configuration Error: {ve}")
            raise
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Failed to connect to Neo4j: {error_msg}", exc_info=True)
            
            # Provide helpful error messages
            if "authentication" in error_msg.lower():
                st.error("🔒 Authentication failed. Check your username and password.")
            elif "connection refused" in error_msg.lower():
                st.error("🔌 Connection refused. Is Neo4j running?")
            elif "serviceunavailable" in error_msg.lower():
                st.error("⚠️ Neo4j service unavailable. Check if the database is running.")
            else:
                st.error(f"❌ Connection Error: {error_msg}")
            
            raise ConnectionError(f"Neo4j connection failed: {error_msg}")
        
    def get_driver(self) -> Driver:
        """Get existing driver from session state."""
        if 'neo4j_driver' not in st.session_state:
            return self.connect()
        return st.session_state.neo4j_driver
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        if 'neo4j_driver' not in st.session_state:
            return False
        
        try:
            driver = st.session_state.neo4j_driver
            with driver.session() as session:
                session.run("RETURN 1")
            return True
        except:
            return False
    
    def reconnect(self):
        """Reconnect to Neo4j."""
        self.close()
        driver:Driver = self.connect()
        return driver
    
    def close(self):
        """Close Neo4j connection."""
        if 'neo4j_driver' in st.session_state:
            try:
                st.session_state.neo4j_driver.close()
                del st.session_state.neo4j_driver
                logger.info("Neo4j connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")