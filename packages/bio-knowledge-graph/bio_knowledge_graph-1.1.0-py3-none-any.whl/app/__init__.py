"""
Flask application factory for BIO Knowledge Graph.
"""
from flask import Flask
from flask_cors import CORS
from config import config
import logging

def create_app(config_name='default'):
    """Create Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register blueprints
    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from .main import main_bp
    app.register_blueprint(main_bp)
    
    return app

