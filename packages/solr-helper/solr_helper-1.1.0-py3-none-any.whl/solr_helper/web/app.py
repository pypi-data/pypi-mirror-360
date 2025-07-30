import fnmatch
from flask import Flask, render_template, request, redirect, url_for
from loguru import logger

from ..solr_client import SolrClient

def create_app(solr_url: str, core: str, schema: dict):
    app = Flask(__name__, template_folder='templates')

    # Konfiguration im App-Kontext speichern
    app.config['SOLR_URL'] = solr_url
    app.config['CORE'] = core
    app.config['SCHEMA'] = schema

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
                                     schema_fields=sorted_schema_fields)

            # Kombiniere Schema-Felder und Dokument-Felder
            doc_field_names = set(doc.keys())
            all_field_names = sorted(list(doc_field_names.union(schema_fields_map.keys())))
            
            display_fields = []
            for name in all_field_names:
                if name in schema_fields_map:
                    display_fields.append(schema_fields_map[name])
                else:
                    # Es ist ein dynamisches Feld oder eines, das nicht im Basisschema ist
                    display_fields.append({
                        'name': name,
                        'type': 'dynamisch',
                        'multiValued': isinstance(doc.get(name), list),
                        'stored': True # Annahme, da wir den Wert haben
                    })

            return render_template('record.html', 
                                 doc=doc, 
                                 schema=schema, 
                                 unique_key_field=unique_key_field, 
                                 schema_fields=display_fields)
        except Exception as e:
            logger.error(f"Fehler bei der Suche nach Dokument {doc_id}: {e}")
            sorted_schema_fields = sorted(schema.get('fields', []), key=lambda x: x['name'])
            return render_template('record.html', 
                                 error=str(e), 
                                 unique_key_field=unique_key_field, 
                                 doc={unique_key_field: doc_id}, 
                                 schema=schema,
                                 schema_fields=sorted_schema_fields)

    @app.route('/record/<doc_id>/edit-form/<field_name>')
    def edit_form(doc_id, field_name):
        client = SolrClient(solr_url=app.config['SOLR_URL'], core=app.config['CORE'])
        schema = app.config.get('SCHEMA')
        unique_key_field = schema.get('unique_key', 'id')
        doc = client.get_document_by_id(unique_key_field, doc_id)
        field_definition = next((f for f in schema.get('fields', []) if f['name'] == field_name), None)

        # Wenn das Feld nicht statisch definiert ist, prüfe, ob es ein dynamisches Feld ist
        if not field_definition:
            for df_pattern in schema.get('dynamic_fields', []):
                if fnmatch.fnmatch(field_name, df_pattern['name']):
                    field_definition = df_pattern.copy()
                    field_definition['name'] = field_name  # Überschreibe das Muster mit dem konkreten Namen
                    break
        
        # Fallback für Felder, die nur im Dokument existieren (nicht im Schema)
        if not field_definition:
            field_definition = {
                'name': field_name,
                'type': 'unbekannt (nur im Dokument)',
                'multiValued': isinstance(doc.get(field_name), list),
                'stored': True
            }
        doc_value = doc.get(field_name)

        use_atomic_update = client.check_update_log_status()
        warning = None
        if not use_atomic_update:
            warning = "WARNUNG: Der Server unterstützt keine atomaren Updates. Beim Speichern gehen die Inhalte aller nicht-gespeicherten Felder (stored='false') verloren!"

        return render_template('_edit_form.html', doc=doc, doc_id=doc_id, field=field_definition, warning=warning, doc_value=doc_value)

    @app.route('/record/<doc_id>/add-field', methods=['POST'])
    def add_field(doc_id):
        """Fügt einem Dokument ein neues Feld hinzu."""
        schema = app.config['SCHEMA']
        unique_key_field = schema.get('unique_key', 'id')
        client = SolrClient(solr_url=app.config['SOLR_URL'], core=app.config['CORE'])
        
        new_field_name = request.form.get('new_field_name')
        new_field_value = request.form.get('new_field_value')

        if not new_field_name or not new_field_value:
            logger.warning("Versuch, ein leeres Feld hinzuzufügen. Aktion wird ignoriert.")
            return redirect(url_for('show_record', doc_id=doc_id))

        try:
            use_atomic_update = client.check_update_log_status()
            copy_fields = schema.get('copy_fields', [])
            client.update_document_field(
                use_atomic_update=use_atomic_update,
                unique_key_field=unique_key_field,
                doc_id=doc_id,
                field_name=new_field_name,
                field_value=new_field_value,
                copy_fields=copy_fields
            )
            logger.success(f"Feld '{new_field_name}' wurde zu Dokument '{doc_id}' hinzugefügt/aktualisiert.")

        except Exception as e:
            logger.error(f"Schwerwiegender Fehler beim Hinzufügen des Feldes: {e}")

        return redirect(url_for('show_record', doc_id=doc_id))

    @app.route('/record/<doc_id>/update-field', methods=['POST'])
    def update_field(doc_id):
        field_name = request.form.get('field_name')
        field_value = request.form.get('field_value')
        is_multi_valued = request.form.get('is_multi_valued') == 'true'

        client = SolrClient(solr_url=app.config['SOLR_URL'], core=app.config['CORE'])
        schema = app.config.get('SCHEMA')
        unique_key_field = schema.get('unique_key', 'id')

        # Logik zur Felddefinition, die dynamische Felder berücksichtigt
        field_definition = next((f for f in schema.get('fields', []) if f['name'] == field_name), None)
        
        # Vor dem Update das Originaldokument holen, um es im Fehlerfall parat zu haben
        original_doc = client.get_document_by_id(unique_key_field, doc_id)

        if not field_definition:
            for df_pattern in schema.get('dynamic_fields', []):
                if fnmatch.fnmatch(field_name, df_pattern['name']):
                    field_definition = df_pattern.copy()
                    field_definition['name'] = field_name
                    break
        
        if not field_definition:
            field_definition = {
                'name': field_name,
                'type': 'unbekannt (nur im Dokument)',
                'multiValued': isinstance(original_doc.get(field_name), list),
                'stored': True
            }

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
            return render_template('_record_row.html', doc=original_doc, field=field_definition, unique_key_field=unique_key_field, error=str(e)), 500

    return app
