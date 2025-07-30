"""
Record display and editing routes for SolrHelper web interface.
"""
from flask import Blueprint, render_template, request, redirect, url_for
from loguru import logger

from ..utils.auth import require_connection, get_current_client, get_current_schema, get_current_connection
from ..utils.helpers import get_field_definition, create_display_fields, process_field_value

# Create blueprint
record_bp = Blueprint('record', __name__)


@record_bp.route('/record/<path:doc_id>')
@require_connection
def show_record(doc_id):
    """Zeigt die Details eines Solr-Dokuments an."""
    schema = get_current_schema()
    client = get_current_client()
    connection = get_current_connection()
    
    if not schema or not client:
        return redirect(url_for('connection.connections'))

    unique_key_field = schema.get('unique_key', 'id')

    try:
        doc = client.get_document_by_id(unique_key_field, doc_id)
        
        # Erstelle eine Map von Feldnamen zu Felddefinitionen aus dem Schema
        schema_fields_map = {f['name']: f for f in schema.get('fields', [])}
        
        if not doc:
            sorted_schema_fields = sorted(schema_fields_map.values(), key=lambda x: x['name'])
            return render_template('record.html', 
                                 error=f"Kein Dokument mit {unique_key_field} '{doc_id}' gefunden.", 
                                 unique_key_field=unique_key_field, 
                                 doc={unique_key_field: doc_id}, 
                                 schema=schema, 
                                 schema_fields=sorted_schema_fields,
                                 current_connection=connection)

        # Erstelle Display-Felder (kombiniert Dokument- und Schema-Felder)
        display_fields = create_display_fields(doc, schema)
        sorted_schema_fields = sorted(schema_fields_map.values(), key=lambda x: x['name'])
        
        return render_template('record.html', 
                             doc=doc, 
                             unique_key_field=unique_key_field, 
                             schema=schema, 
                             display_fields=display_fields, 
                             schema_fields=sorted_schema_fields,
                             current_connection=connection)
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Dokuments {doc_id}: {e}")
        schema_fields_map = {f['name']: f for f in schema.get('fields', [])}
        sorted_schema_fields = sorted(schema_fields_map.values(), key=lambda x: x['name'])
        return render_template('record.html', 
                             error=str(e), 
                             unique_key_field=unique_key_field, 
                             doc={unique_key_field: doc_id}, 
                             schema=schema, 
                             schema_fields=sorted_schema_fields,
                             current_connection=connection)


@record_bp.route('/record/<doc_id>/edit-form/<field_name>')
@require_connection
def edit_form(doc_id, field_name):
    """Zeigt das Edit-Formular für ein spezifisches Feld an."""
    client = get_current_client()
    schema = get_current_schema()
    
    if not client or not schema:
        return redirect(url_for('connection.connections'))
        
    unique_key_field = schema.get('unique_key', 'id')
    doc = client.get_document_by_id(unique_key_field, doc_id)
    field_definition = get_field_definition(field_name, schema, doc)
    doc_value = doc.get(field_name)

    use_atomic_update = client.check_update_log_status()
    warning = None
    if not use_atomic_update:
        warning = "WARNUNG: Der Server unterstützt keine atomaren Updates. Beim Speichern gehen die Inhalte aller nicht-gespeicherten Felder (stored='false') verloren!"

    return render_template('_edit_form.html', 
                         doc=doc, 
                         doc_id=doc_id, 
                         field=field_definition, 
                         warning=warning, 
                         doc_value=doc_value)


@record_bp.route('/record/<doc_id>/add-field', methods=['POST'])
@require_connection
def add_field(doc_id):
    """Fügt einem Dokument ein neues Feld hinzu."""
    schema = get_current_schema()
    client = get_current_client()
    
    if not client or not schema:
        return redirect(url_for('connection.connections'))
        
    unique_key_field = schema.get('unique_key', 'id')
    field_name = request.form.get('field_name')
    field_value = request.form.get('field_value')

    if not field_name:
        return redirect(url_for('record.show_record', doc_id=doc_id))

    try:
        # Hole das aktuelle Dokument
        doc = client.get_document_by_id(unique_key_field, doc_id)
        if not doc:
            return redirect(url_for('record.show_record', doc_id=doc_id))

        # Verwende die intelligente update_document_field Methode
        use_atomic_update = client.check_update_log_status()
        copy_fields = schema.get('copy_fields', [])

        client.update_document_field(
            use_atomic_update=use_atomic_update,
            unique_key_field=unique_key_field,
            doc_id=doc_id,
            field_name=field_name,
            field_value=field_value,
            copy_fields=copy_fields
        )

        logger.info(f"Feld '{field_name}' zu Dokument {doc_id} hinzugefügt")

    except Exception as e:
        logger.error(f"Fehler beim Hinzufügen des Feldes '{field_name}' zu Dokument {doc_id}: {e}")

    return redirect(url_for('record.show_record', doc_id=doc_id))


@record_bp.route('/record/<doc_id>/update-field', methods=['POST'])
@require_connection
def update_field(doc_id):
    """Aktualisiert ein Feld in einem Dokument."""
    field_name = request.form.get('field_name')
    field_value = request.form.get('field_value')
    is_multi_valued = request.form.get('is_multi_valued') == 'true'

    client = get_current_client()
    schema = get_current_schema()

    if not client or not schema:
        return redirect(url_for('connection.connections'))

    unique_key_field = schema.get('unique_key', 'id')

    # Hole das Originaldokument für Fallback
    original_doc = client.get_document_by_id(unique_key_field, doc_id)
    field_definition = get_field_definition(field_name, schema, original_doc)

    try:
        final_value = process_field_value(field_value, is_multi_valued)

        use_atomic_update = client.check_update_log_status()
        copy_fields = schema.get('copy_fields', [])

        client.update_document_field(
            use_atomic_update=use_atomic_update,
            unique_key_field=unique_key_field,
            doc_id=doc_id,
            field_name=field_name,
            field_value=final_value,
            copy_fields=copy_fields
        )

        # Bei Erfolg: Dokument neu laden und die aktualisierte Zeile rendern
        updated_doc = client.get_document_by_id(unique_key_field, doc_id)
        return render_template('_record_row.html',
                             doc=updated_doc,
                             field=field_definition,
                             unique_key_field=unique_key_field)

    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Feldes: {e}")
        # Bei Fehler: Original-Dokument laden und Zeile mit Fehlermeldung rendern
        return render_template('_record_row.html',
                             doc=original_doc,
                             field=field_definition,
                             unique_key_field=unique_key_field,
                             error=str(e)), 500
