"""
Semantic API endpoints.
"""
from flask import request, jsonify
from . import api_bp
from services.semantic_service import SemanticService
import logging

logger = logging.getLogger(__name__)

# Initialize semantic service
semantic_service = SemanticService()

@api_bp.route('/semantic/disambiguate', methods=['POST'])
def disambiguate_entity():
    """Disambiguate entity based on context."""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        context = data.get('context', '')
        candidates = data.get('candidates', [])
        
        result = semantic_service.disambiguate_entity(text, context, candidates)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Entity disambiguation failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/semantic/relations', methods=['POST'])
def suggest_relations():
    """Suggest relations between entities."""
    try:
        data = request.get_json()
        
        if not data or 'entity1' not in data or 'entity2' not in data:
            return jsonify({'error': 'Both entity1 and entity2 are required'}), 400
        
        entity1 = data['entity1']
        entity2 = data['entity2']
        
        relations = semantic_service.suggest_entity_relations(entity1, entity2)
        
        return jsonify({
            'entity1': entity1,
            'entity2': entity2,
            'relations': relations
        })
        
    except Exception as e:
        logger.error(f"Relation suggestion failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/semantic/category/<entity_name>', methods=['GET'])
def get_entity_category(entity_name):
    """Get category of an entity."""
    try:
        category = semantic_service.get_entity_category(entity_name)
        
        return jsonify({
            'entity': entity_name,
            'category': category
        })
        
    except Exception as e:
        logger.error(f"Getting entity category failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/semantic/related/<entity_name>', methods=['GET'])
def get_related_entities(entity_name):
    """Get entities related to the given entity."""
    try:
        relation_type = request.args.get('type', None)
        
        related = semantic_service.get_related_entities(entity_name, relation_type)
        
        return jsonify({
            'entity': entity_name,
            'relation_type': relation_type,
            'related_entities': related
        })
        
    except Exception as e:
        logger.error(f"Getting related entities failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/semantic/bio-label', methods=['POST'])
def infer_bio_label():
    """Infer BIO label for an entity."""
    try:
        data = request.get_json()
        
        if not data or 'entity' not in data:
            return jsonify({'error': 'Entity is required'}), 400
        
        entity = data['entity']
        position = data.get('position', 'B')
        
        bio_label = semantic_service.infer_bio_label(entity, position)
        
        return jsonify({
            'entity': entity,
            'position': position,
            'bio_label': bio_label
        })
        
    except Exception as e:
        logger.error(f"BIO label inference failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/semantic/validate-sequence', methods=['POST'])
def validate_bio_sequence():
    """Validate BIO sequence."""
    try:
        data = request.get_json()
        
        if not data or 'sequence' not in data:
            return jsonify({'error': 'Sequence is required'}), 400
        
        sequence = data['sequence']
        
        if not isinstance(sequence, list):
            return jsonify({'error': 'Sequence must be a list of [token, label] pairs'}), 400
        
        issues = semantic_service.validate_bio_sequence(sequence)
        
        return jsonify({
            'sequence': sequence,
            'issues': issues,
            'is_valid': len(issues) == 0
        })
        
    except Exception as e:
        logger.error(f"BIO sequence validation failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/semantic/ontology', methods=['GET'])
def get_ontology():
    """Get ontology structure."""
    try:
        format_type = request.args.get('format', 'json')
        
        ontology = semantic_service.export_ontology(format_type)
        
        return jsonify(ontology)
        
    except Exception as e:
        logger.error(f"Getting ontology failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/semantic/stats', methods=['GET'])
def get_semantic_stats():
    """Get semantic service statistics."""
    try:
        stats = semantic_service.get_ontology_stats()
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Getting semantic stats failed: {e}")
        return jsonify({'error': str(e)}), 500

