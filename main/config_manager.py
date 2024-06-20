import json
import os
import logging
from filelock import FileLock, Timeout

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE = "config.json"
LOCK_FILE = CONFIG_FILE + ".lock"
LOCK_TIMEOUT = 10  # seconds

def load_config(default_config=None):
    """
    Load configuration from a JSON file.
    :param default_config: Dictionary with default configuration values.
    :return: Dictionary with configuration values.
    """
    if default_config is None:
        default_config = {}

    if os.path.exists(CONFIG_FILE):
        try:
            with FileLock(LOCK_FILE, timeout=LOCK_TIMEOUT):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError, Timeout) as e:
            logger.error(f"Error loading config file: {e}")
            return default_config
    return default_config

def save_config(config):
    """
    Save configuration to a JSON file.
    :param config: Dictionary with configuration values.
    """
    try:
        with FileLock(LOCK_FILE, timeout=LOCK_TIMEOUT):
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
    except (IOError, Timeout) as e:
        logger.error(f"Error saving config file: {e}")

# Example usage
if __name__ == "__main__":
    default_config = {
        "setting1": "value1",
        "setting2": "value2",
    }

    # Load config
    config = load_config(default_config)
    logger.info(f"Loaded config: {config}")

    # Modify config
    config["setting1"] = "new_value"

    # Save config
    save_config(config)
    logger.info("Config saved.")
