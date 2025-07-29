"""
Main routes for the BIO Knowledge Graph application.
"""
from flask import render_template, jsonify
from . import main_bp

@main_bp.route('/')
def index():
    """Home page."""
    return jsonify({
        'message': 'Welcome to BIO Knowledge Graph API',
        'version': '1.0.0',
        'endpoints': {
            'api': '/api',
            'docs': '/api/docs',
            'health': '/api/health'
        }
    })

@main_bp.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'BIO Knowledge Graph'
    })

