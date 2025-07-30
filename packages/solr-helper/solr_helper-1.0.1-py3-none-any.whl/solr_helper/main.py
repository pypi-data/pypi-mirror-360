# Importiert die notwendigen Bibliotheken
import click  # Für die Erstellung von Kommandozeilen-Interfaces
from flask import Flask  # Das Web-Framework für unsere Anwendung
import json  # Für die Formatierung der JSON-Ausgabe
from loguru import logger  # Für einfaches und effektives Logging

# Importiert unseren neuen SolrClient und die zentrale Konfigurationsfunktion
from .solr_client import SolrClient
from .web.app import create_app
import os
from .config import load_solr_config

import functools

def pass_solr_config(f):
    @click.pass_context
    @functools.wraps(f)
    def new_func(ctx, *args, **kwargs):
        solr_url, core = load_solr_config(ctx.obj.get('solr_url'), ctx.obj.get('core'))
        return f(solr_url, core, *args, **kwargs)
    return new_func

# Erstellt die Flask-Anwendung
app = Flask(__name__)

@app.route('/')
def home():
    """Zeigt die Startseite an."""
    logger.info("Startseite wurde aufgerufen.")
    return "<h1>Hallo vom SolrHelper!</h1>"

# Globale Optionen für alle Kommandos (werden an alle weitergereicht)
@click.group()
@click.option('--solr-url', default=None, help='Basis-URL des Solr-Servers, z.B. http://localhost:8983')
@click.option('--core', default=None, help='Name des Solr-Cores, z.B. testing')
@click.pass_context
def cli(ctx, solr_url, core):
    """Ein Helfer-Tool für die Interaktion mit Solr."""
    logger.remove()
    logger.add(lambda msg: click.echo(msg, err=True), colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    logger.info("SolrHelper wird gestartet...")
    # Speichere die Konfigurationsparameter im Context-Objekt
    ctx.ensure_object(dict)
    ctx.obj['solr_url'] = solr_url
    ctx.obj['core'] = core

@cli.command()
@click.option('--host', default='127.0.0.1', help='Der Host, auf dem der Server laufen soll.')
@click.option('--port', default=5000, help='Der Port, auf dem der Server lauschen soll.')
@click.option('--debug', is_flag=True, help='Aktiviert den Debug-Modus.')
@click.pass_context
def run(ctx, host, port, debug):
    """Startet den Flask-Entwicklungsserver."""
    logger.info(f"Starte den Server auf http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

@cli.command(name="test-connection")
@pass_solr_config
def test_connection(solr_url, core):
    """Prüft die Verbindung zum Solr-Core."""
    try:
        client = SolrClient(solr_url=solr_url, core=core)
        if client.check_connection():
            logger.success(f"Verbindung zu Solr-Core '{core}' unter '{solr_url}' erfolgreich.")
        else:
            logger.error("Verbindung fehlgeschlagen.")
            raise click.ClickException("Verbindung konnte nicht hergestellt werden.")
    except Exception as e:
        logger.error(f"Fehler beim Verbindungs-Test: {e}")
        raise click.ClickException("Ein unerwarteter Fehler ist aufgetreten.")

@cli.command()
@click.option('--host', default='127.0.0.1', help='Host für den Webserver.')
@click.option('--port', default=5000, help='Port für den Webserver.')
@pass_solr_config
def start_web(solr_url, core, host, port):
    """Startet den Flask-Webserver für die UI."""
    schema_cache_file = 'schema_cache.json'
    
    # Prüfen, ob der Schema-Cache existiert. Wenn nicht, erstellen.
    if not os.path.exists(schema_cache_file):
        logger.info(f"'{schema_cache_file}' nicht gefunden. Rufe Schema von Solr ab...")
        try:
            client = SolrClient(solr_url=solr_url, core=core)
            schema = client.get_schema()
            with open(schema_cache_file, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)
            logger.success(f"Schema erfolgreich in '{schema_cache_file}' gespeichert.")
        except Exception as e:
            logger.error(f"Konnte Schema nicht abrufen und speichern: {e}")
            raise click.ClickException("Der Webserver konnte nicht gestartet werden, da das Schema nicht abrufbar war.")

    app = create_app(solr_url=solr_url, core=core)
    logger.info(f"Starte Webserver auf http://{host}:{port}")
    app.run(host=host, port=port, debug=True)

@cli.command()
@click.option('--format', type=click.Choice(['json', 'table'], case_sensitive=False), 
              default='table', help='Ausgabeformat (json oder table)')
@pass_solr_config
def show_schema(solr_url, core, format):
    """Zeigt das Schema des aktuellen Solr-Cores an."""
    try:
        client = SolrClient(solr_url=solr_url, core=core)
        schema = client.get_schema()
        
        # Zwischenspeichern der Schema-Infos als JSON-Datei
        schema_cache_file = 'schema_cache.json'
        with open(schema_cache_file, 'w') as f:
            json.dump(schema, f, indent=2)
        
        if format == 'json':
            print(json.dumps(schema, indent=2, ensure_ascii=False))
        else:
            print(f"\nSchema für Core: {schema.get('core', '-')}")
            print("-" * 80)
            print("Felder:")
            print("-" * 80)
            fields = schema.get('fields', [])
            field_names = set()
            for field in fields:
                field_names.update(field.keys())
            field_names = sorted(list(field_names))
            print(f"{'Name':<30} | " + " | ".join(f"{name:<20}" for name in field_names))
            print("-" * (30 + len(field_names) * 20))
            for field in fields:
                print(f"{field.get('name', '-'): <30} | " + " | ".join(f"{field.get(name, '-'): <20}" for name in field_names))
            print("\nFeldtypen:")
            print("-" * 80)
            for name, ftype in schema.get('fieldTypes', {}).items():
                print(f"- {name}: {ftype.get('class', '-')}")
            print(f"\nPrimärschlüssel: {schema.get('uniqueKey', '-')}")
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Schemas: {e}")
        raise click.ClickException("Konnte das Schema nicht abrufen. Bitte überprüfen Sie die Verbindungseinstellungen.")

    @functools.wraps(f)
    def new_func(ctx, *args, **kwargs):
        solr_url, core = load_solr_config(ctx.obj.get('solr_url'), ctx.obj.get('core'))
        return f(solr_url, core, *args, **kwargs)
    return new_func

if __name__ == '__main__':
    cli()
