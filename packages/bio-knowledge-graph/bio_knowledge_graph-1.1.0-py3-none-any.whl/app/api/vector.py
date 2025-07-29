"""
Vector service API endpoints with local multilingual-e5-base model support.
"""
from flask import request, jsonify, current_app
from . import api_bp
from services.vector_service import VectorService
import logging

logger = logging.getLogger(__name__)

# Global vector service instance
vector_service = None

def get_vector_service():
    """Get or create vector service instance."""
    global vector_service
    if vector_service is None:
        from config import get_config
        config = get_config()
        vector_service = VectorService(
            model_path=config.LOCAL_MODEL_PATH,
            dimension=config.VECTOR_DIMENSION
        )
        # Load model on first access
        vector_service.load_model()
    return vector_service

@api_bp.route('/vector/search', methods=['POST'])
def vector_search():
    """
    Perform vector similarity search using local model.
    
    Request body:
    {
        "query": "search query",
        "k": 10,
        "threshold": 0.5
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Query is required'
            }), 400
        
        query = data['query']
        k = data.get('k', 10)
        threshold = data.get('threshold', 0.5)
        
        # Validate parameters
        if k <= 0 or k > 100:
            return jsonify({
                'status': 'error',
                'message': 'k must be between 1 and 100'
            }), 400
        
        if threshold < 0 or threshold > 1:
            return jsonify({
                'status': 'error',
                'message': 'threshold must be between 0 and 1'
            }), 400
        
        # Perform search
        service = get_vector_service()
        results = service.search(query, k, threshold)
        
        return jsonify({
            'status': 'success',
            'data': {
                'query': query,
                'results': results,
                'total_found': len(results)
            }
        })
        
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/vector/similarity', methods=['POST'])
def compute_similarity():
    """
    Compute similarity between two texts using local model.
    
    Request body:
    {
        "text1": "first text",
        "text2": "second text"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text1' not in data or 'text2' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Both text1 and text2 are required'
            }), 400
        
        text1 = data['text1']
        text2 = data['text2']
        
        # Compute similarity
        service = get_vector_service()
        similarity = service.compute_similarity(text1, text2)
        
        return jsonify({
            'status': 'success',
            'data': {
                'text1': text1,
                'text2': text2,
                'similarity': similarity
            }
        })
        
    except Exception as e:
        logger.error(f"Similarity computation failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/vector/similar/<path:entity_text>', methods=['GET'])
def find_similar_entities(entity_text):
    """
    Find similar entities to the given entity using local model.
    
    Query parameters:
    - k: number of similar entities to return (default: 5)
    - exclude_self: whether to exclude the input entity (default: true)
    """
    try:
        k = request.args.get('k', 5, type=int)
        exclude_self = request.args.get('exclude_self', 'true').lower() == 'true'
        
        # Validate parameters
        if k <= 0 or k > 50:
            return jsonify({
                'status': 'error',
                'message': 'k must be between 1 and 50'
            }), 400
        
        # Find similar entities
        service = get_vector_service()
        results = service.find_similar(entity_text, k, exclude_self)
        
        return jsonify({
            'status': 'success',
            'data': {
                'entity': entity_text,
                'similar_entities': results,
                'total_found': len(results)
            }
        })
        
    except Exception as e:
        logger.error(f"Finding similar entities failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/vector/cluster', methods=['POST'])
def cluster_entities():
    """
    Cluster entities using K-means with local model embeddings.
    
    Request body:
    {
        "texts": ["text1", "text2", ...],
        "n_clusters": 5  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({
                'status': 'error',
                'message': 'texts is required'
            }), 400
        
        texts = data['texts']
        n_clusters = data.get('n_clusters')
        
        # Validate parameters
        if not isinstance(texts, list) or len(texts) < 2:
            return jsonify({
                'status': 'error',
                'message': 'At least 2 texts are required for clustering'
            }), 400
        
        if n_clusters is not None and (n_clusters < 2 or n_clusters > len(texts)):
            return jsonify({
                'status': 'error',
                'message': f'n_clusters must be between 2 and {len(texts)}'
            }), 400
        
        # Perform clustering
        service = get_vector_service()
        results = service.cluster_texts(texts, n_clusters)
        
        return jsonify({
            'status': 'success',
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Clustering failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/vector/embedding', methods=['POST'])
def get_embedding():
    """
    Get embedding vector for text using local model.
    
    Request body:
    {
        "text": "input text"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'message': 'text is required'
            }), 400
        
        text = data['text']
        
        # Get embedding
        service = get_vector_service()
        embedding = service.encode_text(text)
        
        return jsonify({
            'status': 'success',
            'data': {
                'text': text,
                'embedding': embedding.tolist(),
                'dimension': len(embedding)
            }
        })
        
    except Exception as e:
        logger.error(f"Getting embedding failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/vector/index/build', methods=['POST'])
def build_vector_index():
    """
    Build FAISS index from texts using local model.
    
    Request body:
    {
        "texts": ["text1", "text2", ...],
        "metadata": [{"id": 1, "category": "course"}, ...]  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({
                'status': 'error',
                'message': 'texts is required'
            }), 400
        
        texts = data['texts']
        metadata = data.get('metadata', [])
        
        # Validate parameters
        if not isinstance(texts, list) or len(texts) == 0:
            return jsonify({
                'status': 'error',
                'message': 'At least 1 text is required'
            }), 400
        
        if metadata and len(metadata) != len(texts):
            return jsonify({
                'status': 'error',
                'message': 'metadata length must match texts length'
            }), 400
        
        # Build index
        service = get_vector_service()
        success = service.build_index(texts, metadata)
        
        if success:
            return jsonify({
                'status': 'success',
                'data': {
                    'message': 'Index built successfully',
                    'total_vectors': len(texts)
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to build index'
            }), 500
        
    except Exception as e:
        logger.error(f"Building index failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/vector/index/add', methods=['POST'])
def add_to_vector_index():
    """
    Add texts to existing FAISS index.
    
    Request body:
    {
        "texts": ["text1", "text2", ...],
        "metadata": [{"id": 1, "category": "course"}, ...]  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({
                'status': 'error',
                'message': 'texts is required'
            }), 400
        
        texts = data['texts']
        metadata = data.get('metadata', [])
        
        # Validate parameters
        if not isinstance(texts, list) or len(texts) == 0:
            return jsonify({
                'status': 'error',
                'message': 'At least 1 text is required'
            }), 400
        
        if metadata and len(metadata) != len(texts):
            return jsonify({
                'status': 'error',
                'message': 'metadata length must match texts length'
            }), 400
        
        # Add to index
        service = get_vector_service()
        success = service.add_to_index(texts, metadata)
        
        if success:
            return jsonify({
                'status': 'success',
                'data': {
                    'message': 'Texts added to index successfully',
                    'added_vectors': len(texts),
                    'total_vectors': service.index.ntotal if service.index else 0
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to add texts to index'
            }), 500
        
    except Exception as e:
        logger.error(f"Adding to index failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/vector/index/save', methods=['POST'])
def save_vector_index():
    """
    Save FAISS index to files.
    
    Request body:
    {
        "index_path": "path/to/index.bin",  // optional
        "metadata_path": "path/to/metadata.pkl"  // optional
    }
    """
    try:
        data = request.get_json() or {}
        
        index_path = data.get('index_path')
        metadata_path = data.get('metadata_path')
        
        # Save index
        service = get_vector_service()
        success = service.save_index(index_path, metadata_path)
        
        if success:
            return jsonify({
                'status': 'success',
                'data': {
                    'message': 'Index saved successfully',
                    'index_path': service.index_path,
                    'metadata_path': service.metadata_path
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to save index'
            }), 500
        
    except Exception as e:
        logger.error(f"Saving index failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/vector/index/load', methods=['POST'])
def load_vector_index():
    """
    Load FAISS index from files.
    
    Request body:
    {
        "index_path": "path/to/index.bin",  // optional
        "metadata_path": "path/to/metadata.pkl"  // optional
    }
    """
    try:
        data = request.get_json() or {}
        
        index_path = data.get('index_path')
        metadata_path = data.get('metadata_path')
        
        # Load index
        service = get_vector_service()
        success = service.load_index(index_path, metadata_path)
        
        if success:
            return jsonify({
                'status': 'success',
                'data': {
                    'message': 'Index loaded successfully',
                    'total_vectors': service.index.ntotal if service.index else 0,
                    'metadata_count': len(service.metadata)
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to load index'
            }), 500
        
    except Exception as e:
        logger.error(f"Loading index failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/vector/stats', methods=['GET'])
def get_vector_stats():
    """Get vector service statistics."""
    try:
        service = get_vector_service()
        stats = service.get_stats()
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Getting vector stats failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_bp.route('/vector/health', methods=['GET'])
def vector_health_check():
    """Perform health check on vector service."""
    try:
        service = get_vector_service()
        health = service.health_check()
        
        status_code = 200 if health['status'] == 'healthy' else 503
        
        return jsonify({
            'status': 'success',
            'data': health
        }), status_code
        
    except Exception as e:
        logger.error(f"Vector health check failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

