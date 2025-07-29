"""
Neo4j database connection and management.
"""
import logging
from typing import Dict, List, Any, Optional
from neo4j import GraphDatabase, Driver, Session
from config import Config

logger = logging.getLogger(__name__)

class Neo4jDatabase:
    """Neo4j database connection and query management."""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """Initialize Neo4j database connection."""
        self.uri = uri or Config.NEO4J_URI
        self.user = user or Config.NEO4J_USER
        self.password = password or Config.NEO4J_PASSWORD
        self.driver: Optional[Driver] = None
        
    def connect(self) -> bool:
        """Establish connection to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j database: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j database connection closed")
    
    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results."""
        if not self.driver:
            raise RuntimeError("Database connection not established")
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_write_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a write query (CREATE, UPDATE, DELETE)."""
        if not self.driver:
            raise RuntimeError("Database connection not established")
        
        try:
            with self.driver.session() as session:
                result = session.write_transaction(self._execute_query, query, parameters or {})
                return result
        except Exception as e:
            logger.error(f"Write query execution failed: {e}")
            raise
    
    @staticmethod
    def _execute_query(tx, query: str, parameters: Dict[str, Any]):
        """Execute query within a transaction."""
        result = tx.run(query, parameters)
        return [record.data() for record in result]
    
    def create_indexes(self):
        """Create necessary indexes for better performance."""
        indexes = [
            "CREATE INDEX course_name_idx IF NOT EXISTS FOR (c:Course) ON (c.name)",
            "CREATE INDEX course_bio_tag_idx IF NOT EXISTS FOR (c:Course) ON (c.bio_tag)",
            "CREATE INDEX annotation_bio_label_idx IF NOT EXISTS FOR (a:AnnotationEntity) ON (a.bio_label)",
            "CREATE INDEX document_id_idx IF NOT EXISTS FOR (d:Document) ON (d.id)",
            "CREATE INDEX user_id_idx IF NOT EXISTS FOR (u:User) ON (u.id)",
            "CREATE INDEX category_name_idx IF NOT EXISTS FOR (cc:CourseCategory) ON (cc.name)"
        ]
        
        for index_query in indexes:
            try:
                self.execute_write_query(index_query)
                logger.info(f"Index created: {index_query}")
            except Exception as e:
                logger.warning(f"Index creation failed or already exists: {e}")
    
    def clear_database(self):
        """Clear all nodes and relationships (use with caution!)."""
        query = "MATCH (n) DETACH DELETE n"
        self.execute_write_query(query)
        logger.info("Database cleared")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        queries = {
            'total_nodes': "MATCH (n) RETURN count(n) as count",
            'total_relationships': "MATCH ()-[r]->() RETURN count(r) as count",
            'course_count': "MATCH (c:Course) RETURN count(c) as count",
            'annotation_count': "MATCH (a:AnnotationEntity) RETURN count(a) as count",
            'document_count': "MATCH (d:Document) RETURN count(d) as count",
            'user_count': "MATCH (u:User) RETURN count(u) as count",
            'category_count': "MATCH (cc:CourseCategory) RETURN count(cc) as count"
        }
        
        stats = {}
        for key, query in queries.items():
            try:
                result = self.execute_query(query)
                stats[key] = result[0]['count'] if result else 0
            except Exception as e:
                logger.error(f"Failed to get {key}: {e}")
                stats[key] = 0
        
        return stats
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

# Global database instance
db = Neo4jDatabase()

