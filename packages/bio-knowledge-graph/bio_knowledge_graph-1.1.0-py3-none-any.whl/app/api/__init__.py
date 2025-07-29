"""
API blueprint for the BIO Knowledge Graph application.
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

from . import annotation, course, semantic, vector, graph

