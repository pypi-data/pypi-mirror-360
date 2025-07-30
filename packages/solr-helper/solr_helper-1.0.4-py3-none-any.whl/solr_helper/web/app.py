import json
from flask import Flask, render_template, request, redirect, url_for
from loguru import logger

from ..solr_client import SolrClient

def create_app(solr_url: str, core: str):
    app = Flask(__name__, template_folder='templates')

    # Konfiguration im App-Kontext speichern
    app.config['SOLR_URL'] = solr_url
    app.config['CORE'] = core

    # Schema beim Start laden
    try:
        with open('schema_cache.json', 'r') as f:
            schema = json.load(f)
        app.config['SCHEMA'] = schema
        logger.success("Schema-Cache erfolgreich geladen.")
    except FileNotFoundError:
        logger.error("schema_cache.json nicht gefunden. Bitte zuerst 'show-schema' ausführen.")
        schema = None
        app.config['SCHEMA'] = None

    @app.route('/')
    def index():
        schema = app.config.get('SCHEMA')
        if not schema:
            return "Fehler: Schema nicht geladen. Bitte CLI ausführen, um den Cache zu erstellen.", 500
        unique_key_field = schema.get('unique_key', 'id')
        return render_template('index.html', unique_key_field=unique_key_field)

    @app.route('/search', methods=['POST'])
    def search():
        doc_id = request.form.get('doc_id')
        if doc_id:
            return redirect(url_for('show_record', doc_id=doc_id))
        return redirect(url_for('index'))

    @app.route('/record/<path:doc_id>')
    def show_record(doc_id):
        schema = app.config.get('SCHEMA')
        if not schema:
            return "Fehler: Schema nicht geladen.", 500

        client = SolrClient(solr_url=app.config['SOLR_URL'], core=app.config['CORE'])
        unique_key_field = schema.get('unique_key', 'id')
        
        try:
            # Annahme: SolrClient hat eine Methode get_document_by_id
            doc = client.get_document_by_id(unique_key_field, doc_id)
            if not doc:
                return render_template('record.html', error=f"Kein Dokument mit {unique_key_field} '{doc_id}' gefunden.", unique_key_field=unique_key_field, doc={unique_key_field: doc_id}, schema_fields=schema.get('fields', []))

            return render_template('record.html', doc=doc, schema_fields=schema.get('fields', []), unique_key_field=unique_key_field)
        except Exception as e:
            logger.error(f"Fehler bei der Suche nach Dokument {doc_id}: {e}")
            return render_template('record.html', error=str(e), unique_key_field=unique_key_field, doc={unique_key_field: doc_id}, schema_fields=schema.get('fields', []))

    @app.route('/record/<doc_id>/edit-form/<field_name>')
    def edit_form(doc_id, field_name):
        client = SolrClient(solr_url=app.config['SOLR_URL'], core=app.config['CORE'])
        schema = app.config.get('SCHEMA')
        unique_key_field = schema.get('uniqueKey', 'id')
        doc = client.get_document_by_id(unique_key_field, doc_id)
        field_definition = next((f for f in schema.get('fields', []) if f['name'] == field_name), None)
        doc_value = doc.get(field_name)

        use_atomic_update = client.check_update_log_status()
        warning = None
        if not use_atomic_update:
            warning = "WARNUNG: Der Server unterstützt keine atomaren Updates. Beim Speichern gehen die Inhalte aller nicht-gespeicherten Felder (stored='false') verloren!"

        return render_template('_edit_form.html', doc=doc, doc_id=doc_id, field=field_definition, warning=warning, doc_value=doc_value)

    @app.route('/record/<doc_id>/update', methods=['POST'])
    def update_field(doc_id):
        field_name = request.form.get('field_name')
        field_value = request.form.get('field_value')
        is_multi_valued = request.form.get('is_multi_valued') == 'true'

        client = SolrClient(solr_url=app.config['SOLR_URL'], core=app.config['CORE'])
        schema = app.config.get('SCHEMA')
        unique_key_field = schema.get('uniqueKey', 'id')
        field_definition = next((f for f in schema.get('fields', []) if f['name'] == field_name), None)

        try:
            if is_multi_valued:
                final_value = field_value.splitlines()
            else:
                final_value = field_value

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
            return render_template('_record_row.html', doc=updated_doc, field=field_definition, unique_key_field=unique_key_field)

        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Feldes: {e}")
            # Bei Fehler: Original-Dokument laden und Zeile mit Fehlermeldung rendern
            original_doc = client.get_document_by_id(unique_key_field, doc_id)
            return render_template('_record_row.html', doc=original_doc, field=field_definition, unique_key_field=unique_key_field, error=str(e)), 500

    return app
