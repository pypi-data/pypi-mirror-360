"""
Course API endpoints.
"""
from flask import request, jsonify
from . import api_bp
from models.course import Course, CourseCategory
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/courses', methods=['GET'])
def get_courses():
    """Get all courses."""
    try:
        limit = request.args.get('limit', 100, type=int)
        search = request.args.get('search', '')
        
        if search:
            courses = Course.search(search, limit)
        else:
            courses = Course.get_all(limit)
        
        return jsonify({
            'courses': [course.to_dict() for course in courses],
            'total': len(courses)
        })
        
    except Exception as e:
        logger.error(f"Getting courses failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/courses/<course_id>', methods=['GET'])
def get_course(course_id):
    """Get course by ID."""
    try:
        course = Course.find_by_id(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        return jsonify(course.to_dict())
        
    except Exception as e:
        logger.error(f"Getting course failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/courses', methods=['POST'])
def create_course():
    """Create new course."""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'bio_tag' not in data:
            return jsonify({'error': 'Name and bio_tag are required'}), 400
        
        course = Course(
            name=data['name'],
            bio_tag=data['bio_tag'],
            description=data.get('description', ''),
            skills=data.get('skills', []),
            difficulty_level=data.get('difficulty_level', 1)
        )
        
        if course.save():
            # Add to category if specified
            category = data.get('category')
            if category:
                course.add_to_category(category)
            
            return jsonify(course.to_dict()), 201
        else:
            return jsonify({'error': 'Failed to create course'}), 500
        
    except Exception as e:
        logger.error(f"Creating course failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/courses/<course_id>', methods=['PUT'])
def update_course(course_id):
    """Update course."""
    try:
        course = Course.find_by_id(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            course.name = data['name']
        if 'bio_tag' in data:
            course.bio_tag = data['bio_tag']
        if 'description' in data:
            course.description = data['description']
        if 'skills' in data:
            course.skills = data['skills']
        if 'difficulty_level' in data:
            course.difficulty_level = data['difficulty_level']
        
        if course.save():
            return jsonify(course.to_dict())
        else:
            return jsonify({'error': 'Failed to update course'}), 500
        
    except Exception as e:
        logger.error(f"Updating course failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/courses/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete course."""
    try:
        course = Course.find_by_id(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        if course.delete():
            return jsonify({'message': 'Course deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete course'}), 500
        
    except Exception as e:
        logger.error(f"Deleting course failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/courses/<course_id>/similar', methods=['GET'])
def get_similar_courses(course_id):
    """Get similar courses."""
    try:
        course = Course.find_by_id(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        limit = request.args.get('limit', 10, type=int)
        similar_courses = course.get_similar_courses(limit)
        
        return jsonify({
            'course': course.to_dict(),
            'similar_courses': similar_courses
        })
        
    except Exception as e:
        logger.error(f"Getting similar courses failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all course categories."""
    try:
        categories = CourseCategory.get_all()
        
        return jsonify({
            'categories': [category.to_dict() for category in categories],
            'total': len(categories)
        })
        
    except Exception as e:
        logger.error(f"Getting categories failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/categories', methods=['POST'])
def create_category():
    """Create new course category."""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        category = CourseCategory(
            name=data['name'],
            description=data.get('description', ''),
            level=data.get('level', 1)
        )
        
        if category.save():
            return jsonify(category.to_dict()), 201
        else:
            return jsonify({'error': 'Failed to create category'}), 500
        
    except Exception as e:
        logger.error(f"Creating category failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/categories/<category_id>/courses', methods=['GET'])
def get_category_courses(category_id):
    """Get courses in a category."""
    try:
        # Find category by ID (assuming we have a find_by_id method)
        from models.database import db
        
        query = "MATCH (cat:CourseCategory {id: $id}) RETURN cat"
        result = db.execute_query(query, {'id': category_id})
        
        if not result:
            return jsonify({'error': 'Category not found'}), 404
        
        category_data = result[0]['cat']
        category = CourseCategory.from_dict(category_data)
        courses = category.get_courses()
        
        return jsonify({
            'category': category.to_dict(),
            'courses': [course.to_dict() for course in courses],
            'total': len(courses)
        })
        
    except Exception as e:
        logger.error(f"Getting category courses failed: {e}")
        return jsonify({'error': str(e)}), 500

