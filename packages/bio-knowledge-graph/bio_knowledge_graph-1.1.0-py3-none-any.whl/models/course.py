"""
Course model for the BIO Knowledge Graph.
"""
import uuid
from typing import Dict, List, Any, Optional
from models.database import db

class Course:
    """Course entity model."""
    
    def __init__(self, name: str, bio_tag: str, description: str = "", 
                 skills: List[str] = None, difficulty_level: int = 1, 
                 course_id: str = None):
        """Initialize a Course instance."""
        self.id = course_id or str(uuid.uuid4())
        self.name = name
        self.bio_tag = bio_tag
        self.description = description
        self.skills = skills or []
        self.difficulty_level = difficulty_level
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert course to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'bio_tag': self.bio_tag,
            'description': self.description,
            'skills': self.skills,
            'difficulty_level': self.difficulty_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Course':
        """Create Course instance from dictionary."""
        return cls(
            course_id=data.get('id'),
            name=data['name'],
            bio_tag=data['bio_tag'],
            description=data.get('description', ''),
            skills=data.get('skills', []),
            difficulty_level=data.get('difficulty_level', 1)
        )
    
    def save(self) -> bool:
        """Save course to database."""
        query = """
        MERGE (c:Course {id: $id})
        SET c.name = $name,
            c.bio_tag = $bio_tag,
            c.description = $description,
            c.skills = $skills,
            c.difficulty_level = $difficulty_level,
            c.updated_at = datetime()
        RETURN c
        """
        
        try:
            result = db.execute_write_query(query, self.to_dict())
            return len(result) > 0
        except Exception as e:
            print(f"Error saving course: {e}")
            return False
    
    @classmethod
    def find_by_id(cls, course_id: str) -> Optional['Course']:
        """Find course by ID."""
        query = "MATCH (c:Course {id: $id}) RETURN c"
        
        try:
            result = db.execute_query(query, {'id': course_id})
            if result:
                return cls.from_dict(result[0]['c'])
            return None
        except Exception as e:
            print(f"Error finding course by ID: {e}")
            return None
    
    @classmethod
    def find_by_name(cls, name: str) -> Optional['Course']:
        """Find course by name."""
        query = "MATCH (c:Course {name: $name}) RETURN c"
        
        try:
            result = db.execute_query(query, {'name': name})
            if result:
                return cls.from_dict(result[0]['c'])
            return None
        except Exception as e:
            print(f"Error finding course by name: {e}")
            return None
    
    @classmethod
    def find_by_bio_tag(cls, bio_tag: str) -> Optional['Course']:
        """Find course by BIO tag."""
        query = "MATCH (c:Course {bio_tag: $bio_tag}) RETURN c"
        
        try:
            result = db.execute_query(query, {'bio_tag': bio_tag})
            if result:
                return cls.from_dict(result[0]['c'])
            return None
        except Exception as e:
            print(f"Error finding course by BIO tag: {e}")
            return None
    
    @classmethod
    def get_all(cls, limit: int = 100) -> List['Course']:
        """Get all courses."""
        query = "MATCH (c:Course) RETURN c LIMIT $limit"
        
        try:
            result = db.execute_query(query, {'limit': limit})
            return [cls.from_dict(record['c']) for record in result]
        except Exception as e:
            print(f"Error getting all courses: {e}")
            return []
    
    @classmethod
    def search(cls, search_term: str, limit: int = 20) -> List['Course']:
        """Search courses by name or description."""
        query = """
        MATCH (c:Course)
        WHERE toLower(c.name) CONTAINS toLower($search_term)
           OR toLower(c.description) CONTAINS toLower($search_term)
        RETURN c
        LIMIT $limit
        """
        
        try:
            result = db.execute_query(query, {
                'search_term': search_term,
                'limit': limit
            })
            return [cls.from_dict(record['c']) for record in result]
        except Exception as e:
            print(f"Error searching courses: {e}")
            return []
    
    def add_to_category(self, category_name: str, weight: float = 1.0) -> bool:
        """Add course to a category."""
        query = """
        MATCH (c:Course {id: $course_id})
        MERGE (cat:CourseCategory {name: $category_name})
        MERGE (c)-[r:BELONGS_TO]->(cat)
        SET r.weight = $weight
        RETURN r
        """
        
        try:
            result = db.execute_write_query(query, {
                'course_id': self.id,
                'category_name': category_name,
                'weight': weight
            })
            return len(result) > 0
        except Exception as e:
            print(f"Error adding course to category: {e}")
            return False
    
    def get_similar_courses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get similar courses based on category and skills."""
        query = """
        MATCH (c:Course {id: $course_id})-[:BELONGS_TO]->(cat:CourseCategory)<-[:BELONGS_TO]-(similar:Course)
        WHERE c <> similar
        WITH similar, count(cat) as shared_categories
        RETURN similar, shared_categories
        ORDER BY shared_categories DESC
        LIMIT $limit
        """
        
        try:
            result = db.execute_query(query, {
                'course_id': self.id,
                'limit': limit
            })
            return [{
                'course': Course.from_dict(record['similar']),
                'similarity_score': record['shared_categories']
            } for record in result]
        except Exception as e:
            print(f"Error getting similar courses: {e}")
            return []
    
    def delete(self) -> bool:
        """Delete course from database."""
        query = """
        MATCH (c:Course {id: $id})
        DETACH DELETE c
        """
        
        try:
            db.execute_write_query(query, {'id': self.id})
            return True
        except Exception as e:
            print(f"Error deleting course: {e}")
            return False

class CourseCategory:
    """Course category model."""
    
    def __init__(self, name: str, description: str = "", level: int = 1, 
                 category_id: str = None):
        """Initialize a CourseCategory instance."""
        self.id = category_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.level = level
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert category to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'level': self.level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CourseCategory':
        """Create CourseCategory instance from dictionary."""
        return cls(
            category_id=data.get('id'),
            name=data['name'],
            description=data.get('description', ''),
            level=data.get('level', 1)
        )
    
    def save(self) -> bool:
        """Save category to database."""
        query = """
        MERGE (cat:CourseCategory {id: $id})
        SET cat.name = $name,
            cat.description = $description,
            cat.level = $level,
            cat.updated_at = datetime()
        RETURN cat
        """
        
        try:
            result = db.execute_write_query(query, self.to_dict())
            return len(result) > 0
        except Exception as e:
            print(f"Error saving category: {e}")
            return False
    
    @classmethod
    def get_all(cls) -> List['CourseCategory']:
        """Get all categories."""
        query = "MATCH (cat:CourseCategory) RETURN cat"
        
        try:
            result = db.execute_query(query)
            return [cls.from_dict(record['cat']) for record in result]
        except Exception as e:
            print(f"Error getting all categories: {e}")
            return []
    
    def get_courses(self) -> List[Course]:
        """Get all courses in this category."""
        query = """
        MATCH (cat:CourseCategory {id: $id})<-[:BELONGS_TO]-(c:Course)
        RETURN c
        """
        
        try:
            result = db.execute_query(query, {'id': self.id})
            return [Course.from_dict(record['c']) for record in result]
        except Exception as e:
            print(f"Error getting courses for category: {e}")
            return []

