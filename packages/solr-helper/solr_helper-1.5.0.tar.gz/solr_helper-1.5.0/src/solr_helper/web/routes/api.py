"""
HTMX API routes for SolrHelper web interface.
"""
from flask import Blueprint, request
from loguru import logger

from ..utils.auth import require_connection, get_current_client, get_current_schema

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/search', methods=['POST'])
def api_search():
    """HTMX-kompatible Suchroute die HTML-Fragmente zurückgibt."""
    # Prüfe ob Verbindung aktiv ist
    client = get_current_client()
    schema = get_current_schema()
    
    if not client or not schema:
        return '<div class="alert alert-warning">Keine Verbindung aktiv. <a href="/connections" class="link">Verbindung auswählen</a></div>'
        
    search_type = request.form.get('search_type', 'id')
    search_query = request.form.get('search_query', '').strip()
    search_field = request.form.get('search_field', '').strip()
    
    if not search_query:
        return '<div class="alert alert-info">Bitte gib einen Suchbegriff ein.</div>'
    
    unique_key_field = schema.get('unique_key', 'id')
    
    if search_type == 'id':
        # ID-Suche: Direkt zum Dokument
        try:
            doc = client.get_document_by_id(unique_key_field, search_query)
            if doc:
                return f'''
                <div class="alert alert-success">
                    <span>Dokument gefunden!</span>
                    <a href="/record/{search_query}" class="btn btn-sm btn-primary ml-2">Dokument öffnen</a>
                </div>
                '''
            else:
                return f'<div class="alert alert-warning">Kein Dokument mit {unique_key_field} "{search_query}" gefunden.</div>'
        except Exception as e:
            return f'<div class="alert alert-error">Fehler bei der Suche: {str(e)}</div>'
    else:
        # Textsuche: Kompakte Ergebnisliste anzeigen (mit Substring-Matching)
        if not search_field or not search_field.strip():
            return '<div class="alert alert-warning">Für Textsuche muss ein Feld ausgewählt werden.</div>'
            
        try:
            results = client.search_documents(search_query, field=search_field, rows=5, start=0)
            
            if results['numFound'] == 0:
                field_info = f' in Feld "{search_field}"' if search_field else ''
                return f'<div class="alert alert-info">Keine Ergebnisse für "{search_query}"{field_info} gefunden.</div>'
            
            # Generiere kompakte HTML für Suchergebnisse
            html = f'''
            <div class="card bg-base-100 shadow-xl">
                <div class="card-body">
                    <h3 class="card-title">Suchergebnisse</h3>
                    <div class="alert alert-info mb-4">
                        <span><strong>{results["numFound"]}</strong> Ergebnisse für "{search_query}"{f' in Feld "{search_field}"' if search_field else ''}</span>
                    </div>
                    <div class="space-y-2">
            '''
            
            highlighting = results.get('highlighting', {})
            
            for doc in results['docs'][:5]:  # Nur erste 5 anzeigen
                doc_id = doc.get(unique_key_field, 'N/A')
                
                # Highlighting-Snippets für dieses Dokument
                doc_highlights = highlighting.get(doc_id, {})
                highlight_snippets = []
                
                for field_name, snippets in doc_highlights.items():
                    if snippets:  # Nur wenn Snippets vorhanden
                        for snippet in snippets[:2]:  # Max 2 Snippets pro Feld
                            highlight_snippets.append(f'<span class="badge badge-outline badge-xs mr-1">{field_name}</span>{snippet}')
                
                html += f'''
                <div class="p-3 bg-base-200 rounded">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <div class="font-mono text-sm font-semibold mb-2">{doc_id}</div>
                            {'<div class="text-sm space-y-1">' + '<br>'.join(highlight_snippets) + '</div>' if highlight_snippets else '<div class="text-xs text-gray-500">Keine Textvorschau verfügbar</div>'}
                        </div>
                        <a href="/record/{doc_id}" class="btn btn-primary btn-sm ml-3">Bearbeiten</a>
                    </div>
                </div>
                '''
            
            html += '</div>'
            
            if results['numFound'] > 5:
                html += f'''
                <div class="card-actions justify-center mt-4">
                    <a href="/search-results?query={search_query}{'&field=' + search_field if search_field else ''}" 
                       class="btn btn-outline">Alle {results["numFound"]} Ergebnisse anzeigen</a>
                </div>
                '''
            
            html += '''
                </div>
            </div>
            '''
            
            return html
            
        except Exception as e:
            return f'<div class="alert alert-error">Fehler bei der Textsuche: {str(e)}</div>'
