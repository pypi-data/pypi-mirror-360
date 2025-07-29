"""
Knowledge graph management API endpoints.
"""
from flask import request, jsonify
from . import api_bp
from models.database import db
from services.annotation_service import AnnotationService
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/graph/stats', methods=['GET'])
def get_graph_stats():
    """Get knowledge graph statistics."""
    try:
        stats = db.get_database_stats()
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Getting graph stats failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/graph/query', methods=['POST'])
def execute_cypher_query():
    """Execute Cypher query on the knowledge graph."""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        parameters = data.get('parameters', {})
        
        # Security check - only allow read queries
        query_lower = query.lower().strip()
        if any(keyword in query_lower for keyword in ['create', 'delete', 'set', 'remove', 'merge']):
            return jsonify({'error': 'Only read queries are allowed'}), 403
        
        result = db.execute_query(query, parameters)
        
        return jsonify({
            'query': query,
            'parameters': parameters,
            'result': result,
            'count': len(result)
        })
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/graph/nodes/<node_type>', methods=['GET'])
def get_nodes_by_type(node_type):
    """Get nodes by type."""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        query = f"MATCH (n:{node_type}) RETURN n LIMIT $limit"
        result = db.execute_query(query, {'limit': limit})
        
        nodes = [record['n'] for record in result]
        
        return jsonify({
            'node_type': node_type,
            'nodes': nodes,
            'count': len(nodes)
        })
        
    except Exception as e:
        logger.error(f"Getting nodes failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/graph/relationships/<relationship_type>', methods=['GET'])
def get_relationships_by_type(relationship_type):
    """Get relationships by type."""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        query = f"""
        MATCH (a)-[r:{relationship_type}]->(b)
        RETURN a, r, b
        LIMIT $limit
        """
        result = db.execute_query(query, {'limit': limit})
        
        relationships = []
        for record in result:
            relationships.append({
                'source': record['a'],
                'relationship': record['r'],
                'target': record['b']
            })
        
        return jsonify({
            'relationship_type': relationship_type,
            'relationships': relationships,
            'count': len(relationships)
        })
        
    except Exception as e:
        logger.error(f"Getting relationships failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/graph/path', methods=['POST'])
def find_path():
    """Find path between two nodes."""
    try:
        data = request.get_json()
        
        if not data or 'start_node' not in data or 'end_node' not in data:
            return jsonify({'error': 'Start and end nodes are required'}), 400
        
        start_node = data['start_node']
        end_node = data['end_node']
        max_length = data.get('max_length', 5)
        
        query = """
        MATCH path = shortestPath((start)-[*..%d]-(end))
        WHERE start.name = $start_name AND end.name = $end_name
        RETURN path
        """ % max_length
        
        result = db.execute_query(query, {
            'start_name': start_node,
            'end_name': end_node
        })
        
        return jsonify({
            'start_node': start_node,
            'end_node': end_node,
            'path': result[0]['path'] if result else None,
            'found': len(result) > 0
        })
        
    except Exception as e:
        logger.error(f"Finding path failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/graph/neighbors/<node_id>', methods=['GET'])
def get_node_neighbors(node_id):
    """Get neighbors of a node."""
    try:
        depth = request.args.get('depth', 1, type=int)
        
        query = """
        MATCH (n {id: $node_id})-[*1..%d]-(neighbor)
        RETURN DISTINCT neighbor
        """ % depth
        
        result = db.execute_query(query, {'node_id': node_id})
        
        neighbors = [record['neighbor'] for record in result]
        
        return jsonify({
            'node_id': node_id,
            'depth': depth,
            'neighbors': neighbors,
            'count': len(neighbors)
        })
        
    except Exception as e:
        logger.error(f"Getting neighbors failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/graph/subgraph', methods=['POST'])
def get_subgraph():
    """Get subgraph around specified nodes."""
    try:
        data = request.get_json()
        
        if not data or 'nodes' not in data:
            return jsonify({'error': 'Nodes array is required'}), 400
        
        nodes = data['nodes']
        depth = data.get('depth', 1)
        
        if not isinstance(nodes, list):
            return jsonify({'error': 'Nodes must be an array'}), 400
        
        # Build query to get subgraph
        node_conditions = ' OR '.join([f'n.id = "{node}"' for node in nodes])
        
        query = f"""
        MATCH (n)-[r*1..{depth}]-(m)
        WHERE {node_conditions}
        RETURN n, r, m
        """
        
        result = db.execute_query(query)
        
        # Process result to extract nodes and relationships
        subgraph_nodes = set()
        subgraph_relationships = []
        
        for record in result:
            # Add nodes
            if 'n' in record:
                subgraph_nodes.add(record['n']['id'])
            if 'm' in record:
                subgraph_nodes.add(record['m']['id'])
            
            # Add relationships
            if 'r' in record and record['r']:
                for rel in record['r']:
                    subgraph_relationships.append(rel)
        
        return jsonify({
            'input_nodes': nodes,
            'depth': depth,
            'subgraph': {
                'nodes': list(subgraph_nodes),
                'relationships': subgraph_relationships
            },
            'node_count': len(subgraph_nodes),
            'relationship_count': len(subgraph_relationships)
        })
        
    except Exception as e:
        logger.error(f"Getting subgraph failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/graph/build-index', methods=['POST'])
def build_graph_index():
    """Build vector index from knowledge graph data."""
    try:
        annotation_service = AnnotationService()
        annotation_service.build_vector_index_from_db()
        
        return jsonify({'message': 'Vector index built from knowledge graph successfully'})
        
    except Exception as e:
        logger.error(f"Building graph index failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/graph/initialize', methods=['POST'])
def initialize_graph():
    """Initialize knowledge graph with basic structure."""
    try:
        # Create indexes
        db.create_indexes()
        
        return jsonify({'message': 'Knowledge graph initialized successfully'})
        
    except Exception as e:
        logger.error(f"Graph initialization failed: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/graph/export', methods=['GET'])
def export_graph():
    """Export knowledge graph data."""
    try:
        format_type = request.args.get('format', 'json')
        
        if format_type == 'json':
            # Export as JSON
            nodes_query = "MATCH (n) RETURN n"
            relationships_query = "MATCH (a)-[r]->(b) RETURN a, r, b"
            
            nodes_result = db.execute_query(nodes_query)
            relationships_result = db.execute_query(relationships_query)
            
            export_data = {
                'nodes': [record['n'] for record in nodes_result],
                'relationships': [
                    {
                        'source': record['a'],
                        'relationship': record['r'],
                        'target': record['b']
                    }
                    for record in relationships_result
                ]
            }
            
            return jsonify(export_data)
        else:
            return jsonify({'error': f'Unsupported format: {format_type}'}), 400
        
    except Exception as e:
        logger.error(f"Graph export failed: {e}")
        return jsonify({'error': str(e)}), 500

