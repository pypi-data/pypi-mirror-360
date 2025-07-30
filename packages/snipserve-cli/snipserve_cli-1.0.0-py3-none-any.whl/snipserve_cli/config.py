import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / '.snipserve'
CONFIG_FILE = CONFIG_DIR / 'config.json'

def get_config_dir():
    """Create and return config directory"""
    CONFIG_DIR.mkdir(exist_ok=True)
    return CONFIG_DIR

def load_config():
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """Save configuration to file"""
    get_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_api_key():
    """Get API key from config or environment"""
    config = load_config()
    return config.get('api_key') or os.getenv('SNIPSERVE_API_KEY')

def get_base_url():
    """Get base URL from config or environment"""
    config = load_config()
    return config.get('base_url') or os.getenv('SNIPSERVE_URL', 'https://snipserve.spkal01.me')