"""
Main blueprint for the BIO Knowledge Graph application.
"""
from flask import Blueprint

main_bp = Blueprint('main', __name__)

from . import routes

