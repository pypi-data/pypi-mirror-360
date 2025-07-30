"""Handles reading and writing database configuration for the Astra DB connection."""

import os
import json
from types import SimpleNamespace

CONFIG_FILE = "astra_config.json"  # Configuration file path

def read_db_config():
    """Reads the database configuration from the config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return SimpleNamespace(**data)
    return None

def write_db_config(api_endpoint, token, cohere_api_key):
    """Writes the database configuration to the config file."""
    config = {
        "api_endpoint": api_endpoint.strip(),
        "token": token.strip(),
        "cohere_api_key": cohere_api_key.strip()
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4)
