"""
Annotation API endpoints.
"""
from flask import request, jsonify
from . import api_bp
from services.annotation_service import AnnotationService
import logging

logger = logging.getLogger(__name__)

# Initialize annotation service
annotation_service = AnnotationService()

@api_bp.route('/annotate', methods=['POST'])
def annotate_text():
    """Annotate text with BIO labels."""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        context = data.get('context', '')
        use_llm = data.get('use_llm', True)
        use_vector = data.get('use_vector', True)
        
        # Perform annotation
        result = annotation_service.annotate_text(
            text=text,
            context=context,
            use_llm=use_llm,
            use_vector=use_vector
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Annotation failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/annotate/batch', methods=['POST'])
def batch_annotate():
    """Batch annotate multiple texts."""
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({'error': 'Texts array is required'}), 400
        
        texts = data['texts']
        context = data.get('context', '')
        use_llm = data.get('use_llm', True)
        use_vector = data.get('use_vector', True)
        
        if not isinstance(texts, list):
            return jsonify({'error': 'Texts must be an array'}), 400
        
        results = []
        for text in texts:
            result = annotation_service.annotate_text(
                text=text,
                context=context,
                use_llm=use_llm,
                use_vector=use_vector
            )
            results.append(result)
        
        return jsonify({
            'results': results,
            'total': len(results)
        })
        
    except Exception as e:
        logger.error(f"Batch annotation failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/annotate/suggestions', methods=['POST'])
def get_annotation_suggestions():
    """Get annotation suggestions for text."""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        k = data.get('k', 5)
        
        suggestions = annotation_service.get_annotation_suggestions(text, k)
        
        return jsonify({
            'text': text,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"Getting suggestions failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/annotate/validate', methods=['POST'])
def validate_annotation():
    """Validate BIO annotation sequence."""
    try:
        data = request.get_json()
        
        if not data or 'tokens' not in data or 'labels' not in data:
            return jsonify({'error': 'Tokens and labels are required'}), 400
        
        tokens = data['tokens']
        labels = data['labels']
        
        if len(tokens) != len(labels):
            return jsonify({'error': 'Tokens and labels must have same length'}), 400
        
        validation = annotation_service.llm_service.validate_annotation(tokens, labels)
        
        return jsonify(validation)
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/annotate/save', methods=['POST'])
def save_annotation():
    """Save annotation result to knowledge graph."""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data or 'annotation' not in data:
            return jsonify({'error': 'Text and annotation are required'}), 400
        
        text = data['text']
        annotation_result = data['annotation']
        document_id = data.get('document_id')
        
        success = annotation_service.save_annotation(text, annotation_result, document_id)
        
        if success:
            return jsonify({'message': 'Annotation saved successfully'})
        else:
            return jsonify({'error': 'Failed to save annotation'}), 500
        
    except Exception as e:
        logger.error(f"Saving annotation failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/annotate/explain', methods=['POST'])
def explain_annotation():
    """Get explanation for annotation decisions."""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data or 'annotation' not in data:
            return jsonify({'error': 'Text and annotation are required'}), 400
        
        text = data['text']
        annotation = data['annotation']
        
        explanation = annotation_service.llm_service.generate_annotation_explanation(text, annotation)
        
        return jsonify({
            'text': text,
            'explanation': explanation
        })
        
    except Exception as e:
        logger.error(f"Generating explanation failed: {e}")
        return jsonify({'error': str(e)}), 500

