"""
Flask application factory for SolrHelper web interface.
"""
import sys
from flask import Flask
from loguru import logger

from ..solr_client import SolrClient
from .routes.connection import connection_bp
from .routes.search import search_bp
from .routes.record import record_bp
from .routes.api import api_bp


def create_app_for_connection_management(debug=False):
    """Erstellt eine Flask-App für Connection Management mit dynamischer Verbindungsumschaltung."""
    app = Flask(__name__, template_folder='templates')

    # Konfiguriere Logging basierend auf Debug-Modus
    logger.remove()  # Entferne Standard-Handler
    log_level = "DEBUG" if debug else "INFO"
    log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}" if debug else "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}"
    logger.add(sys.stderr, level=log_level, format=log_format)

    # App-State für aktuelle Verbindung
    app.config['CURRENT_CONNECTION'] = None
    app.config['CURRENT_SCHEMA'] = None
    app.config['CURRENT_CLIENT'] = None

    # Register blueprints
    app.register_blueprint(connection_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(record_bp)
    app.register_blueprint(api_bp)

    logger.info("Flask-App für Connection Management erstellt")
    return app


def create_app(solr_url: str, core: str, schema: dict, debug=False):
    """
    Erstellt eine Flask-App mit fester Solr-Verbindung.

    Args:
        solr_url (str): Solr-Server URL
        core (str): Solr-Core Name
        schema (dict): Solr-Schema
        debug (bool): Debug-Modus aktivieren

    Returns:
        Flask: Konfigurierte Flask-App
    """
    app = Flask(__name__, template_folder='templates')

    # Konfiguriere Logging basierend auf Debug-Modus
    logger.remove()  # Entferne Standard-Handler
    log_level = "DEBUG" if debug else "INFO"
    log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}" if debug else "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}"
    logger.add(sys.stderr, level=log_level, format=log_format)

    # Konfiguration im App-Kontext speichern
    app.config['SOLR_URL'] = solr_url
    app.config['CORE'] = core
    app.config['SCHEMA'] = schema

    # Erstelle Client und setze als "aktuelle Verbindung"
    try:
        client = SolrClient(solr_url, core)
        client.check_connection()
        
        app.config['CURRENT_CONNECTION'] = {
            'url': solr_url,
            'core': core,
            'name': f"{core} @ {solr_url}"
        }
        app.config['CURRENT_CLIENT'] = client
        app.config['CURRENT_SCHEMA'] = schema
        
        logger.info(f"Flask-App mit fester Verbindung erstellt: {solr_url}/solr/{core}")
        
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der App mit fester Verbindung: {e}")
        # Fallback: App ohne Verbindung erstellen
        app.config['CURRENT_CONNECTION'] = None
        app.config['CURRENT_CLIENT'] = None
        app.config['CURRENT_SCHEMA'] = None

    # Register blueprints
    app.register_blueprint(connection_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(record_bp)
    app.register_blueprint(api_bp)

    return app
