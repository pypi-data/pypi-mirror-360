"""
Search routes for SolrHelper web interface.
"""
from flask import Blueprint, render_template, request, redirect, url_for
from loguru import logger

from ..utils.auth import require_connection, get_current_client, get_current_schema, get_current_connection

# Create blueprint
search_bp = Blueprint('search', __name__)


@search_bp.route('/')
def index():
    """Zeigt Hauptseite oder Connection Management je nach Status."""
    connection = get_current_connection()
    if connection:
        # Verbindung aktiv -> normale Hauptseite
        schema = get_current_schema()
        if not schema:
            return "Fehler: Schema nicht geladen.", 500

        unique_key_field = schema.get('unique_key', 'id')
        client = get_current_client()
        indexed_fields = client.get_indexed_fields(schema) if client else []

        return render_template('index.html',
                             unique_key_field=unique_key_field,
                             indexed_fields=indexed_fields,
                             current_connection=connection)

    # Keine Verbindung -> Connection Management
    return redirect(url_for('connection.connections'))


@search_bp.route('/search', methods=['POST'])
@require_connection
def search():
    """Verarbeitet Suchanfragen und leitet zu entsprechenden Ergebnisseiten weiter."""
    search_type = request.form.get('search_type', 'id')
    search_query = request.form.get('search_query', '').strip()
    search_field = request.form.get('search_field', '').strip()
    
    if not search_query:
        return redirect(url_for('search.index'))
    
    if search_type == 'id':
        # ID-Suche: Direkt zum Dokument weiterleiten
        return redirect(url_for('record.show_record', doc_id=search_query))
    else:
        # Textsuche: Zu den Suchergebnissen weiterleiten
        if search_field:
            return redirect(url_for('search.search_results', query=search_query, field=search_field))
        else:
            return redirect(url_for('search.search_results', query=search_query))


@search_bp.route('/search-results')
@require_connection
def search_results():
    """Zeigt Suchergebnisse für Textsuchen an."""
    query = request.args.get('query', '').strip()
    field = request.args.get('field', '').strip()
    start = int(request.args.get('start', 0))
    rows = 20  # Anzahl Ergebnisse pro Seite
    
    if not query:
        return redirect(url_for('search.index'))
    
    schema = get_current_schema()
    client = get_current_client()
    connection = get_current_connection()
    
    if not schema or not client:
        return redirect(url_for('connection.connections'))
    
    unique_key_field = schema.get('unique_key', 'id')
    
    try:
        results = client.search_documents(query, field=field if field else None, rows=rows, start=start)
        
        return render_template('search_results.html',
                             query=query,
                             field=field,
                             results=results,
                             unique_key_field=unique_key_field,
                             schema=schema,
                             current_connection=connection)
    except Exception as e:
        logger.error(f"Fehler bei der Suche mit Query '{query}' in Feld '{field}': {e}")
        return render_template('search_results.html',
                             query=query,
                             field=field,
                             results={'docs': [], 'numFound': 0, 'start': 0, 'rows': rows},
                             unique_key_field=unique_key_field,
                             schema=schema,
                             current_connection=connection,
                             error=str(e))
