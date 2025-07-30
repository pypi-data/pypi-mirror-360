import pytest
from konfig_master import load

# A list of all valid configuration files to test
VALID_CONFIGS = ["tests/settings.json", "tests/settings.yaml", "tests/settings.toml"]

@pytest.mark.parametrize("config_file", VALID_CONFIGS)
def test_load_valid_configs(config_file):
    """
    Tests loading of all supported valid file formats.
    """
    config = load(config_file)
    
    # Test dictionary-style access
    assert config['database']['port'] == 5432
    
    # Test dot-notation access
    assert config.get('database.users')[0] == "admin"
    assert config.get('logging.enabled') is True
    
    # Test that the host is unique to the file type
    assert ".local" in config.get('database.host')

def test_file_not_found():
    """
    Tests that a FileNotFoundError is raised for a non-existent file.
    """
    with pytest.raises(FileNotFoundError):
        load("non_existent_file.yaml")