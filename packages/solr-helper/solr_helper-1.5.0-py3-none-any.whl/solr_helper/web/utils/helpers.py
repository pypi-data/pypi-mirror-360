"""
Helper functions for SolrHelper web interface.
"""
import fnmatch
from loguru import logger


def get_field_definition(field_name, schema, doc=None):
    """
    Gets the field definition for a given field name.
    Checks schema fields, dynamic fields, and creates fallback definitions.
    
    Args:
        field_name (str): Name of the field
        schema (dict): Solr schema
        doc (dict, optional): Document to infer field properties from
        
    Returns:
        dict: Field definition with name, type, multiValued, stored properties
    """
    # Check explicit schema fields
    schema_fields_map = {f['name']: f for f in schema.get('fields', [])}
    field_definition = schema_fields_map.get(field_name)
    
    if not field_definition:
        # Check dynamic fields
        for df_pattern in schema.get('dynamic_fields', []):
            if fnmatch.fnmatch(field_name, df_pattern['name']):
                field_definition = df_pattern.copy()
                field_definition['name'] = field_name
                logger.debug(f"Dynamisches Feld erkannt: {field_name} -> {df_pattern['name']}")
                break
    
    # Fallback for fields that only exist in the document
    if not field_definition:
        field_definition = {
            'name': field_name,
            'type': 'unbekannt (nur im Dokument)',
            'multiValued': isinstance(doc.get(field_name) if doc else None, list),
            'stored': True
        }
        logger.debug(f"Unbekanntes Feld im Dokument: {field_name}")
    
    return field_definition


def create_display_fields(doc, schema):
    """
    Creates a list of display fields combining document fields and schema fields.
    
    Args:
        doc (dict): Solr document
        schema (dict): Solr schema
        
    Returns:
        list: List of field display objects with definition, value, and has_value
    """
    # Create map of schema fields
    schema_fields_map = {f['name']: f for f in schema.get('fields', [])}
    
    # Combine document fields and schema fields
    doc_field_names = set(doc.keys())
    all_field_names = sorted(list(doc_field_names.union(schema_fields_map.keys())))
    
    logger.debug(f"Dokument-Felder: {sorted(doc_field_names)}")
    logger.debug(f"Schema-Felder: {sorted(schema_fields_map.keys())}")
    logger.debug(f"Alle Felder: {all_field_names}")
    
    display_fields = []
    for name in all_field_names:
        field_def = get_field_definition(name, schema, doc)
        
        display_fields.append({
            'definition': field_def,
            'value': doc.get(name),
            'has_value': name in doc
        })
    
    logger.debug(f"Display-Felder erstellt: {len(display_fields)} Felder")
    return display_fields


def process_field_value(field_value, is_multi_valued):
    """
    Processes field value based on whether it's multi-valued or not.
    
    Args:
        field_value (str): Raw field value from form
        is_multi_valued (bool): Whether the field is multi-valued
        
    Returns:
        str or list: Processed field value
    """
    if is_multi_valued:
        return field_value.splitlines()
    else:
        return field_value
