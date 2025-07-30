# Importiert die notwendigen Bibliotheken
import pysolr  # Python-Bibliothek für die Interaktion mit Solr
from loguru import logger  # Für das Logging
from typing import Dict, Any, Optional, List
import requests  # Für direkte HTTP-Anfragen an die Solr-API


class SolrClient:
    """Ein Client für die Kommunikation mit einem Solr-Server."""

    def __init__(self, solr_url: str = "http://localhost:8983/solr", core: str = "testing"):
        """
        Initialisiert den Solr-Client mit pysolr.

        Args:
            solr_url (str): Die Basis-URL des Solr-Servers (ohne Core, sollte mit /solr enden, z.B. http://localhost:8983/solr).
            core (str): Der Name des Solr-Cores, mit dem kommuniziert werden soll.
        """
        # Sicherstellen, dass die Basis-URL auf /solr endet
        if not solr_url.rstrip('/').endswith('/solr'):
            logger.warning(f"solr_url '{solr_url}' endet nicht auf '/solr'. '/solr' wird automatisch ergänzt.")
            solr_url = solr_url.rstrip('/') + '/solr'
        # Konstruiert die vollständige URL zum Solr-Core
        self.core_url = f"{solr_url.rstrip('/')}/{core}"
        # Initialisiert die pysolr-Instanz
        self.solr = pysolr.Solr(self.core_url, timeout=10)
        self._update_log_status = None  # Cache für den Status
        logger.info(f"Solr-Client für Core-URL '{self.core_url}' initialisiert.")

    def check_connection(self) -> bool:
        """
        Überprüft, ob eine Verbindung zum Solr-Core hergestellt werden kann.
        Verwendet die search-Methode von pysolr, die mit allen Solr-Versionen kompatibel ist.

        Returns:
            bool: True, wenn die Verbindung erfolgreich ist, sonst False.
        """
        logger.info(f"Überprüfe Solr-Verbindung an: {self.core_url}")

        try:
            # Führt eine einfache Suche ohne Ergebnisse durch
            # Die search-Methode wirft eine Ausnahme, wenn die Verbindung fehlschlägt
            self.solr.search('*:*', rows=0)
            logger.success("Verbindung zum Solr-Core erfolgreich hergestellt.")
            return True
            
        except pysolr.SolrError as e:
            # Fängt Solr-spezifische Fehler ab
            logger.error(f"Fehler bei der Verbindung zum Solr-Core: {e}")
            return False
        except Exception as e:
            # Fängt alle anderen Fehler ab (z.B. Netzwerkprobleme)
            logger.error(f"Unbekannter Fehler bei der Verbindung zum Solr-Core: {e}")
            return False
            
    def get_schema(self) -> Dict[str, Any]:
        """
        Ruft das Schema des Solr-Cores ab und gibt die wichtigsten Strukturen (fields, fieldTypes, dynamicFields, copyFields, uniqueKey, core) im Original-Format zurück.
        Die Feldnamen werden nicht verändert, damit sie für spätere Verarbeitung und UI-Generierung direkt nutzbar sind.

        Returns:
            Dict[str, Any]: Das Schema-JSON mit den wichtigsten Keys.
        """
        try:
            schema_url = f"{self.core_url}/schema"
            response = requests.get(schema_url, params={'wt': 'json'})
            response.raise_for_status()
            schema_data = response.json().get('schema', {})
            result = {
                'core': self.core_url.split('/')[-1],
                'unique_key': schema_data.get('uniqueKey'),
                'fields': schema_data.get('fields', []),
                'field_types': schema_data.get('fieldTypes', []),
                'dynamic_fields': schema_data.get('dynamicFields', []),
                'copy_fields': schema_data.get('copyFields', [])
            }
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Fehler beim Abrufen des Schemas: {e}")
            raise
        except Exception as e:
            logger.error(f"Unbekannter Fehler beim Verarbeiten des Schemas: {e}")
            raise

    def get_indexed_fields(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrahiert alle indizierten Felder aus dem Schema.

        Args:
            schema (Dict[str, Any]): Das Schema-Dictionary vom get_schema() Aufruf.

        Returns:
            List[Dict[str, Any]]: Liste der indizierten Felder mit Name und Typ.
        """
        indexed_fields = []

        # Statische Felder durchgehen
        for field in schema.get('fields', []):
            # Prüfe ob das Feld indiziert ist (indexed=true oder nicht explizit auf false gesetzt)
            if field.get('indexed', True):  # Default ist True wenn nicht angegeben
                indexed_fields.append({
                    'name': field['name'],
                    'type': field.get('type', 'unknown'),
                    'multiValued': field.get('multiValued', False)
                })

        # Dynamische Felder durchgehen
        for field in schema.get('dynamic_fields', []):
            if field.get('indexed', True):
                indexed_fields.append({
                    'name': field['name'],
                    'type': field.get('type', 'unknown'),
                    'multiValued': field.get('multiValued', False),
                    'dynamic': True
                })

        # Nach Name sortieren
        indexed_fields.sort(key=lambda x: x['name'])

        logger.debug(f"Gefunden {len(indexed_fields)} indizierte Felder")
        return indexed_fields

    def get_document_by_id(self, unique_key_field: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Ruft ein einzelnes Dokument anhand seiner ID (Unique Key) aus Solr ab.

        Args:
            unique_key_field (str): Der Name des Unique-Key-Feldes im Schema.
            doc_id (str): Die ID des zu suchenden Dokuments.

        Returns:
            Optional[Dict[str, Any]]: Das gefundene Dokument als Dictionary oder None, wenn nichts gefunden wurde.
        """
        try:
            query = f'{unique_key_field}:"{doc_id}"'
            results = self.solr.search(q=query)
            if results.docs:
                return results.docs[0]
            return None
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Dokuments mit ID {doc_id}: {e}")
            raise



    def search_documents(self, query: str, field: str = None, rows: int = 10, start: int = 0) -> Dict[str, Any]:
        """
        Führt eine Textsuche aus - entweder allgemein oder in einem spezifischen Feld.

        Args:
            query (str): Der Suchbegriff für die Textsuche.
            field (str, optional): Spezifisches Feld für die Suche. Wenn None, wird in allen Feldern gesucht.
            rows (int): Anzahl der zurückzugebenden Ergebnisse (Standard: 10).
            start (int): Startposition für Paginierung (Standard: 0).

        Returns:
            Dict[str, Any]: Dictionary mit 'docs' (Liste der Dokumente), 'numFound' (Gesamtanzahl) und 'start' (Startposition).
        """
        try:
            # Query aufbauen
            if not query.strip():
                search_query = "*:*"
            elif field and field.strip():
                # Feldspezifische Substring-Suche
                # Escape special characters in query for Solr
                escaped_query = query.replace('"', '\\"').replace('*', '\\*').replace('?', '\\?')
                # Verwende Wildcards für Substring-Suche: *Begriff*
                search_query = f'{field}:*{escaped_query}*'
            else:
                # Kein Feld angegeben - das sollte durch die UI verhindert werden
                logger.warning("Textsuche ohne Feldangabe - das sollte nicht passieren!")
                raise ValueError("Für Textsuche muss ein Feld angegeben werden")

            logger.info(f"Führe Suche aus: '{search_query}' (rows={rows}, start={start})")

            # Highlighting-Parameter für Solr
            highlighting_params = {
                'hl': 'true',                    # Highlighting aktivieren
                'hl.fl': '*',                    # Alle Felder highlighten
                'hl.simple.pre': '<mark class="bg-yellow-200 px-1 rounded">',  # HTML-Tag für Hervorhebung (Start)
                'hl.simple.post': '</mark>',     # HTML-Tag für Hervorhebung (Ende)
                'hl.fragsize': 150,              # Snippet-Länge
                'hl.snippets': 3,                # Max. Anzahl Snippets pro Feld
                'hl.maxAnalyzedChars': 1000000,  # Max. Zeichen für Analyse
                'hl.requireFieldMatch': 'false'  # Highlighting auch in anderen Feldern
            }

            # Wenn spezifisches Feld angegeben, nur dieses highlighten
            if field and field.strip():
                highlighting_params['hl.fl'] = field

            results = self.solr.search(q=search_query, rows=rows, start=start, **highlighting_params)

            return {
                'docs': results.docs,
                'numFound': results.hits,
                'start': start,
                'rows': rows,
                'query': search_query,
                'highlighting': getattr(results, 'highlighting', {})
            }
        except Exception as e:
            logger.error(f"Fehler bei der Suche mit Query '{query}' in Feld '{field}': {e}")
            raise

    def check_update_log_status(self) -> bool:
        """Prüft, ob der <updateLog/> in der solrconfig.xml für den Core aktiviert ist."""
        if self._update_log_status is not None:
            return self._update_log_status

        try:
            config_url = f"{self.core_url}/config"
            response = requests.get(config_url, params={'wt': 'json'})
            response.raise_for_status()
            config = response.json()
            # Ältere Solr-Versionen geben einen flachen Schlüssel zurück, z.B. 'updateHandlerupdateLog'.
            # Wir prüfen beide Varianten: die moderne, verschachtelte und die alte, flache.
            update_handler_config = config.get('config', {}).get('updateHandler', {})
            has_nested_update_log = 'updateLog' in update_handler_config
            has_flat_update_log = 'updateHandlerupdateLog' in config.get('config', {})

            has_update_log = has_nested_update_log or has_flat_update_log
            logger.info(f"UpdateLog-Status für {self.core_url} ist: {'Aktiviert' if has_update_log else 'Deaktiviert'}")
            self._update_log_status = has_update_log
            return has_update_log
        except requests.exceptions.RequestException as e:
            logger.warning(f"Konnte Konfiguration nicht abrufen, um UpdateLog-Status zu prüfen: {e}. Nehme an, er ist deaktiviert.")
            self._update_log_status = False
            return False

    def _update_atomic(self, unique_key_field: str, doc_id: str, field_name: str, field_value: Any):
        """Führt ein atomares Update für ein einzelnes Feld durch."""
        doc_update = {
            unique_key_field: doc_id,
            field_name: {'set': field_value}
        }
        self.solr.add([doc_update], commit=True)
        logger.info("Atomares Update durchgeführt.")

    def _update_full_document(self, unique_key_field: str, doc_id: str, field_name: str, field_value: Any, copy_fields: list = None):
        """Führt ein Update durch, indem das gesamte Dokument neu indiziert wird."""
        if copy_fields is None:
            copy_fields = []
        doc = self.get_document_by_id(unique_key_field, doc_id)
        if not doc:
            raise ValueError(f"Dokument mit ID '{doc_id}' nicht gefunden.")
        doc[field_name] = field_value
        if '_version_' in doc:
            del doc['_version_']
        dest_fields = {cf['dest'] for cf in copy_fields}
        for df in dest_fields:
            if df in doc:
                del doc[df]
        self.solr.add([doc], commit=True)
        logger.info("Full-Document-Update durchgeführt.")

    def update_document_field(self, use_atomic_update: bool, unique_key_field: str, doc_id: str, field_name: str, field_value: Any, copy_fields: list = None):
        """Aktualisiert ein Feld in einem Solr-Dokument basierend auf der gewählten Strategie."""
        try:
            if use_atomic_update:
                self._update_atomic(unique_key_field, doc_id, field_name, field_value)
            else:
                self._update_full_document(unique_key_field, doc_id, field_name, field_value, copy_fields)
            logger.success(f"Feld '{field_name}' für Dokument '{doc_id}' erfolgreich aktualisiert.")
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Feldes '{field_name}' für Dokument '{doc_id}': {e}")
            raise

    def update_document(self, doc: Dict[str, Any]):
        """
        Aktualisiert ein komplettes Dokument in Solr.

        Args:
            doc (Dict[str, Any]): Das zu aktualisierende Dokument
        """
        try:
            self.solr.add([doc], commit=True)
            logger.info(f"Dokument erfolgreich aktualisiert")
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Dokuments: {e}")
            raise
