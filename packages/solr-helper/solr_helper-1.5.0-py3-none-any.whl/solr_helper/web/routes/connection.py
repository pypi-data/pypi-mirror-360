"""
Connection management routes for SolrHelper web interface.
"""
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
from loguru import logger

from ...solr_client import SolrClient

# Create blueprint
connection_bp = Blueprint('connection', __name__)


@connection_bp.route('/connections')
def connections():
    """Zeigt die Connection Management Seite an."""
    return render_template('connections.html')


@connection_bp.route('/use-connection/<connection_id>')
def use_connection(connection_id):
    """Wechselt zur angegebenen Verbindung."""
    return render_template('use_connection.html', connection_id=connection_id)


@connection_bp.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Testet eine Solr-Verbindung ohne die App neu zu starten."""
    try:
        data = request.get_json()
        url = data.get('url')
        core = data.get('core')
        
        if not url or not core:
            return jsonify({'success': False, 'error': 'URL und Core sind erforderlich'})
        
        # Teste die Verbindung
        client = SolrClient(url, core)
        client.check_connection()
        
        logger.info(f"Verbindungstest erfolgreich: {url}/solr/{core}")
        return jsonify({'success': True, 'message': 'Verbindung erfolgreich getestet'})
        
    except Exception as e:
        logger.error(f"Fehler beim Testen der Verbindung: {e}")
        return jsonify({'success': False, 'error': str(e)})


@connection_bp.route('/api/switch-connection', methods=['POST'])
def switch_connection_api():
    """Wechselt die aktuelle Solr-Verbindung zur Laufzeit."""
    try:
        data = request.get_json()
        url = data.get('url')
        core = data.get('core')
        name = data.get('name', f"{core} @ {url}")
        
        if not url or not core:
            return jsonify({'success': False, 'error': 'URL und Core sind erforderlich'})
        
        # Erstelle neuen Client und teste Verbindung
        client = SolrClient(url, core)
        client.check_connection()
        
        # Lade Schema
        schema = client.get_schema()
        indexed_fields = client.get_indexed_fields(schema)
        
        # Aktualisiere App-Konfiguration
        current_app.config['CURRENT_CONNECTION'] = {
            'url': url,
            'core': core,
            'name': name
        }
        current_app.config['CURRENT_CLIENT'] = client
        current_app.config['CURRENT_SCHEMA'] = schema
        current_app.config['INDEXED_FIELDS'] = indexed_fields
        
        logger.success(f"Erfolgreich zu Verbindung '{name}' gewechselt")
        return jsonify({
            'success': True, 
            'message': f"Erfolgreich zu '{name}' gewechselt",
            'connection': {
                'url': url,
                'core': core,
                'name': name
            }
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Wechseln der Verbindung: {e}")
        return jsonify({'success': False, 'error': str(e)})
