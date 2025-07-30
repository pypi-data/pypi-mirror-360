import json
from pathlib import Path
import yaml # Requires PyYAML
import toml # Requires toml

class Config(dict):
    """
    A dictionary-like object that allows accessing nested keys using dot notation.
    Example: config.get('database.host')
    """
    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = Config(value)

    def get(self, key, default=None):
        """
        Retrieves a value using dot notation.
        """
        keys = key.split('.')
        val = self
        try:
            for k in keys:
                val = val[k]
            return val
        except (KeyError, TypeError):
            return default

def load(filepath: str | Path):
    """
    Loads a configuration file based on its extension.
    Supports .json, .yaml, and .toml.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {filepath}")

    suffix = path.suffix.lower()
    
    with open(path, 'r') as f:
        if suffix == '.json':
            data = json.load(f)
        elif suffix in ['.yaml', '.yml']:
            data = yaml.safe_load(f)
        elif suffix == '.toml':
            data = toml.load(f)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
            
    return Config(data)