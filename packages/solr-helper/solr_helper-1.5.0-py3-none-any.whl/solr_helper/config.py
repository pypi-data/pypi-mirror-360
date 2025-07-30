import os
from pathlib import Path

try:
    import toml
except ImportError:
    toml = None

DEFAULT_SOLR_URL = "http://localhost:8983"
DEFAULT_CORE = "testing"

def load_solr_config(cli_solr_url=None, cli_core=None):
    """
    Lädt die Solr-Konfiguration aus CLI, ENV, config.toml oder Default.
    Reihenfolge: CLI > ENV > config.toml > Default
    """
    # 1. CLI
    solr_url = cli_solr_url
    core = cli_core

    # 2. ENV
    if not solr_url:
        solr_url = os.environ.get("SOLRHELPER_SOLR_URL")
    if not core:
        core = os.environ.get("SOLRHELPER_CORE")

    # 3. config.toml (erst Projekt, dann Home)
    config = {}
    if not solr_url or not core:
        config_paths = [
            Path.cwd() / "config.toml",
            Path.home() / ".solrhelper" / "config.toml"
        ]
        for cfg_path in config_paths:
            if cfg_path.exists() and toml:
                with open(cfg_path, "r") as f:
                    try:
                        config = toml.load(f)
                        break
                    except Exception:
                        pass
        if not solr_url:
            solr_url = config.get("solr_url")
        if not core:
            core = config.get("core")

    # 4. Defaults
    if not solr_url:
        solr_url = DEFAULT_SOLR_URL
    if not core:
        core = DEFAULT_CORE

    return solr_url.rstrip("/"), core
