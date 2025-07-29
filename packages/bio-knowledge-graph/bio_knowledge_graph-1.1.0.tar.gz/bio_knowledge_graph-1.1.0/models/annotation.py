"""
Annotation entity model for the BIO Knowledge Graph.
"""
import uuid
from typing import Dict, List, Any, Optional
from models.database import db

class AnnotationEntity:
    """Annotation entity model for BIO tagged entities."""
    
    def __init__(self, text: str, bio_label: str, position: int = 0, 
                 confidence: float = 1.0, entity_id: str = None):
        """Initialize an AnnotationEntity instance."""
        self.id = entity_id or str(uuid.uuid4())
        self.text = text
        self.bio_label = bio_label
        self.position = position
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert annotation entity to dictionary."""
        return {
            'id': self.id,
            'text': self.text,
            'bio_label': self.bio_label,
            'position': self.position,
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnnotationEntity':
        """Create AnnotationEntity instance from dictionary."""
        return cls(
            entity_id=data.get('id'),
            text=data['text'],
            bio_label=data['bio_label'],
            position=data.get('position', 0),
            confidence=data.get('confidence', 1.0)
        )
    
    def save(self) -> bool:
        """Save annotation entity to database."""
        query = """
        MERGE (a:AnnotationEntity {id: $id})
        SET a.text = $text,
            a.bio_label = $bio_label,
            a.position = $position,
            a.confidence = $confidence,
            a.updated_at = datetime()
        RETURN a
        """
        
        try:
            result = db.execute_write_query(query, self.to_dict())
            return len(result) > 0
        except Exception as e:
            print(f"Error saving annotation entity: {e}")
            return False
    
    @classmethod
    def find_by_id(cls, entity_id: str) -> Optional['AnnotationEntity']:
        """Find annotation entity by ID."""
        query = "MATCH (a:AnnotationEntity {id: $id}) RETURN a"
        
        try:
            result = db.execute_query(query, {'id': entity_id})
            if result:
                return cls.from_dict(result[0]['a'])
            return None
        except Exception as e:
            print(f"Error finding annotation entity by ID: {e}")
            return None
    
    @classmethod
    def find_by_bio_label(cls, bio_label: str, limit: int = 100) -> List['AnnotationEntity']:
        """Find annotation entities by BIO label."""
        query = """
        MATCH (a:AnnotationEntity {bio_label: $bio_label})
        RETURN a
        LIMIT $limit
        """
        
        try:
            result = db.execute_query(query, {
                'bio_label': bio_label,
                'limit': limit
            })
            return [cls.from_dict(record['a']) for record in result]
        except Exception as e:
            print(f"Error finding annotation entities by BIO label: {e}")
            return []
    
    @classmethod
    def get_all(cls, limit: int = 100) -> List['AnnotationEntity']:
        """Get all annotation entities."""
        query = "MATCH (a:AnnotationEntity) RETURN a LIMIT $limit"
        
        try:
            result = db.execute_query(query, {'limit': limit})
            return [cls.from_dict(record['a']) for record in result]
        except Exception as e:
            print(f"Error getting all annotation entities: {e}")
            return []
    
    def link_to_course(self, course_id: str, confidence: float = None) -> bool:
        """Link annotation entity to a course."""
        if confidence is None:
            confidence = self.confidence
            
        query = """
        MATCH (a:AnnotationEntity {id: $entity_id})
        MATCH (c:Course {id: $course_id})
        MERGE (a)-[r:ANNOTATED_AS]->(c)
        SET r.confidence = $confidence,
            r.created_at = datetime()
        RETURN r
        """
        
        try:
            result = db.execute_write_query(query, {
                'entity_id': self.id,
                'course_id': course_id,
                'confidence': confidence
            })
            return len(result) > 0
        except Exception as e:
            print(f"Error linking annotation entity to course: {e}")
            return False
    
    def get_linked_courses(self) -> List[Dict[str, Any]]:
        """Get courses linked to this annotation entity."""
        query = """
        MATCH (a:AnnotationEntity {id: $entity_id})-[r:ANNOTATED_AS]->(c:Course)
        RETURN c, r.confidence as confidence
        """
        
        try:
            result = db.execute_query(query, {'entity_id': self.id})
            return [{
                'course': result[0]['c'],
                'confidence': record['confidence']
            } for record in result]
        except Exception as e:
            print(f"Error getting linked courses: {e}")
            return []
    
    @classmethod
    def get_bio_label_stats(cls) -> Dict[str, int]:
        """Get statistics of BIO labels."""
        query = """
        MATCH (a:AnnotationEntity)
        RETURN a.bio_label as label, count(a) as count
        ORDER BY count DESC
        """
        
        try:
            result = db.execute_query(query)
            return {record['label']: record['count'] for record in result}
        except Exception as e:
            print(f"Error getting BIO label stats: {e}")
            return {}
    
    def delete(self) -> bool:
        """Delete annotation entity from database."""
        query = """
        MATCH (a:AnnotationEntity {id: $id})
        DETACH DELETE a
        """
        
        try:
            db.execute_write_query(query, {'id': self.id})
            return True
        except Exception as e:
            print(f"Error deleting annotation entity: {e}")
            return False

