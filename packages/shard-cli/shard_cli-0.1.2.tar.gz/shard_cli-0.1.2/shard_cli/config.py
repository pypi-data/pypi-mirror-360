#############
# config.py #
#############

import toml
from pathlib import Path
from platformdirs import user_config_dir

DEFAULT_CONFIG = {
    "vault_path": "~/zettel",
    "editor_cmd": "nano",
    "general": {
        "date_format": "%Y%m%d%H%M%S"
    },
    "kasten": {
        "1": "Inbox",
        "2": "Literature Notes",
        "3": "Permanent Notes"
    }
}

def get_config_path() -> Path:
    config_dir = Path(user_config_dir("shard-cli"))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.toml"

def save_config(data: dict):
    config_path = get_config_path()
    with open(config_path, "w") as f:
        toml.dump(data, f)

def load_config() -> dict:
    config_path = get_config_path()
    if not config_path.exists():
        save_config(DEFAULT_CONFIG)
    config = toml.load(config_path)
    # Expand user in vault_path for safe usage
    if "vault_path" in config:
        config["vault_path"] = Path(config["vault_path"]).expanduser()
    else:
        config["vault_path"] = Path(DEFAULT_CONFIG["vault_path"]).expanduser()
    return config
