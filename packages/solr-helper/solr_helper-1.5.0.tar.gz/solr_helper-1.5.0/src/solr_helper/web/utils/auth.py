"""
Authentication and authorization utilities for SolrHelper web interface.
"""
from functools import wraps
from flask import current_app, redirect, url_for


def require_connection(f):
    """
    Decorator that ensures a Solr connection is active before executing the route.
    Redirects to connection management if no connection is available.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config.get('CURRENT_CONNECTION'):
            return redirect(url_for('connection.connections'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_client():
    """Returns the current Solr client or None if not connected."""
    return current_app.config.get('CURRENT_CLIENT')


def get_current_schema():
    """Returns the current Solr schema or None if not connected."""
    return current_app.config.get('CURRENT_SCHEMA')


def get_current_connection():
    """Returns the current connection info or None if not connected."""
    return current_app.config.get('CURRENT_CONNECTION')


def is_connected():
    """Returns True if a Solr connection is active."""
    return bool(current_app.config.get('CURRENT_CONNECTION'))
