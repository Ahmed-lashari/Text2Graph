"""
Enhanced graph builder with beautiful visualization support.
"""
from neo4j import Driver, Session
import pandas as pd
from pyvis.network import Network
from typing import Dict, List
import random


class GraphBuilder:
    """Build and visualize knowledge graphs in Neo4j."""
    
    def __init__(self, driver: Driver):
        self.driver = driver
        
        # Color scheme for different node types
        self.node_colors = {
            'Person': '#FF6B6B',           # Red
            'Organization': '#4ECDC4',     # Teal
            'Location': '#45B7D1',         # Blue
            'Date': '#FFA07A',             # Light Salmon
            'Product': '#98D8C8',          # Mint
            'Event': '#F7DC6F',            # Yellow
            'Entity': '#95A5A6',           # Gray
            'App': '#9B59B6',              # Purple
        }
        
        # Relationship color scheme
        self.relationship_colors = {
            'OWNS': '#E74C3C',
            'FOUNDED': '#8E44AD',
            'WORKS_AT': '#3498DB',
            'MANAGES': '#E67E22',
            'REPORTS_TO': '#16A085',
            'COLLABORATES_WITH': '#27AE60',
            'HIRED': '#2ECC71',
            'LOCATED_IN': '#3498DB',
        }
    
    def clear_database(self):
        """Delete all nodes and relationships from the database."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def create_app_graph(self, app_name: str, df: pd.DataFrame):
        """Create a knowledge graph from the DataFrame."""
        self.clear_database()
        
        with self.driver.session() as session:
            # Check if this is text data (has relationship columns)
            if self._is_text_data(df):
                self._create_text_graph(session, df)
            else:
                # Original logic for CSV/JSON
                self._create_structured_graph(session, app_name, df)
    
    def _is_text_data(self, df: pd.DataFrame) -> bool:
        """Check if DataFrame is from text processing."""
        required_cols = {'source', 'target', 'relationship'}
        return required_cols.issubset(set(df.columns))
    
    def _create_text_graph(self, session: Session, df: pd.DataFrame):
        """Create beautiful graph from text entity relationships."""
        created_nodes = set()
        
        for idx, row in df.iterrows():
            source = row.get('source')
            target = row.get('target')
            rel_type = row.get('relationship', 'RELATED_TO')
            
            if pd.isna(source) or pd.isna(target):
                continue
            
            # Clean relationship type
            rel_type = self._clean_relationship_type(rel_type)
            
            # Get entity types
            source_type = self._clean_node_label(row.get('source_type', 'Entity'))
            target_type = self._clean_node_label(row.get('target_type', 'Entity'))
            
            # Create nodes if they don't exist
            if source not in created_nodes:
                self._create_node(session, source, source_type)
                created_nodes.add(source)
            
            if target not in created_nodes:
                self._create_node(session, target, target_type)
                created_nodes.add(target)
            
            # Create relationship
            self._create_relationship(
                session,
                source, target,
                rel_type,
                row.get('sentence', ''),
                row.get('confidence', 'medium')
            )
    
    def _create_node(self, session: Session, name: str, node_type: str):
        """Create a node with proper label and properties."""
        query = f"""
            MERGE (n:{node_type} {{name: $name}})
            SET n.type = $node_type,
                n.created = timestamp()
        """
        
        try:
            session.run(query, name=str(name), node_type=node_type)
        except Exception as e:
            # Fallback to Entity if label is invalid
            query_fallback = """
                MERGE (n:Entity {name: $name})
                SET n.type = $node_type,
                    n.created = timestamp()
            """
            session.run(query_fallback, name=str(name), node_type=node_type)
    
    def _create_relationship(
        self,
        session: Session,
        source: str,
        target: str,
        rel_type: str,
        sentence: str = '',
        confidence: str = 'medium'
    ):
        """Create a relationship between two nodes."""
        query = f"""
            MATCH (a {{name: $source}})
            MATCH (b {{name: $target}})
            MERGE (a)-[r:{rel_type}]->(b)
            SET r.sentence = $sentence,
                r.confidence = $confidence,
                r.created = timestamp()
        """
        
        try:
            session.run(
                query,
                source=str(source),
                target=str(target),
                sentence=str(sentence),
                confidence=confidence
            )
        except Exception as e:
            # Fallback to generic RELATED_TO
            query_fallback = """
                MATCH (a {name: $source})
                MATCH (b {name: $target})
                MERGE (a)-[r:RELATED_TO]->(b)
                SET r.sentence = $sentence,
                    r.original_type = $rel_type,
                    r.confidence = $confidence
            """
            session.run(
                query_fallback,
                source=str(source),
                target=str(target),
                sentence=str(sentence),
                rel_type=rel_type,
                confidence=confidence
            )
    
    def _create_structured_graph(self, session: Session, app_name: str, df: pd.DataFrame):
        """Create graph for structured CSV/JSON data."""
        # Create root app node
        session.run("MERGE (a:App {name: $app_name})", app_name=app_name)
        
        # Process each row
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            
            for key, value in row_dict.items():
                if value is None or pd.isna(value):
                    continue
                
                if isinstance(value, list):
                    for v in value:
                        self._create_app_relation(session, app_name, key, v)
                else:
                    self._create_app_relation(session, app_name, key, value)
    
    def _create_app_relation(self, session: Session, app_name: str, key: str, value):
        """Create relationship from app node to data entity."""
        rel_type = f"HAS_{self._clean_relationship_type(key)}"
        
        query = f"""
            MATCH (a:App {{name: $app_name}})
            MERGE (b:DataEntity {{name: $value, property: $key}})
            MERGE (a)-[r:{rel_type}]->(b)
        """
        
        try:
            session.run(query, app_name=app_name, value=str(value), key=key)
        except Exception as e:
            # Fallback with generic relationship
            query_fallback = """
                MATCH (a:App {name: $app_name})
                MERGE (b:DataEntity {name: $value, property: $key})
                MERGE (a)-[r:HAS_PROPERTY]->(b)
                SET r.property_name = $key
            """
            session.run(query_fallback, app_name=app_name, value=str(value), key=key)
    
    def add_to_pyvis(self, net: Network):
        """Load nodes/edges from Neo4j and create beautiful visualization."""
        with self.driver.session() as session:
            # Fetch nodes with their types
            node_result = session.run("""
                MATCH (n)
                RETURN DISTINCT n.name AS name, 
                       labels(n)[0] AS type,
                       n.type AS stored_type
            """)
            
            # Add nodes with colors based on type
            for record in node_result:
                name = record["name"]
                node_type = record["stored_type"] or record["type"] or "Entity"
                color = self.node_colors.get(node_type, '#95A5A6')
                
                net.add_node(
                    name,
                    label=name,
                    title=f"{node_type}: {name}",
                    color=color,
                    size=25,
                    font={'size': 14, 'face': 'Arial'}
                )
            
            # Fetch relationships
            edge_result = session.run("""
                MATCH (n)-[r]->(m)
                RETURN n.name AS from,
                       m.name AS to,
                       type(r) AS rel,
                       r.confidence AS confidence
            """)
            
            # Add edges with labels and colors
            for record in edge_result:
                from_node = record["from"]
                to_node = record["to"]
                rel_type = record["rel"]
                confidence = record.get("confidence", "medium")
                
                # Get relationship color
                color = self.relationship_colors.get(rel_type, '#7F8C8D')
                
                # Edge width based on confidence
                width_map = {'high': 3, 'medium': 2, 'low': 1}
                width = width_map.get(confidence, 2)
                
                net.add_edge(
                    from_node,
                    to_node,
                    title=rel_type,
                    label=rel_type,
                    color=color,
                    width=width,
                    arrows='to',
                    font={'size': 10, 'align': 'middle'}
                )
    
    def get_graph_stats(self) -> Dict:
        """Get statistics about the graph."""
        with self.driver.session() as session:
            # Count nodes
            node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
            
            # Count relationships
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
            
            # Count node types
            node_types_result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] AS type, count(*) AS count
                ORDER BY count DESC
            """)
            
            node_types = {record["type"]: record["count"] for record in node_types_result}
            
            # Count relationship types
            rel_types_result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) AS type, count(*) AS count
                ORDER BY count DESC
                LIMIT 10
            """)
            
            rel_types = {record["type"]: record["count"] for record in rel_types_result}
            
            return {
                "nodes": node_count,
                "relationships": rel_count,
                "node_types": len(node_types),
                "node_type_distribution": node_types,
                "top_relationships": rel_types
            }
    
    @staticmethod
    def _clean_relationship_type(rel_type: str) -> str:
        """Clean relationship type for Neo4j."""
        return str(rel_type).upper().replace(" ", "_").replace("-", "_").replace(".", "_")
    
    @staticmethod
    def _clean_node_label(label: str) -> str:
        """Clean node label for Neo4j."""
        if not label or label == 'nan':
            return 'Entity'
        return str(label).replace(" ", "").replace("-", "")