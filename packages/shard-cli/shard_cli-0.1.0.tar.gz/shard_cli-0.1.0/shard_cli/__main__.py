###############
# __main__.py #
###############

from shard.config import load_config
from shard.commands import app

# load the default config into the proper directory
# ~/.config/shard/ for unix users
#
config = load_config()
print(config["vault_path"])      # pathlib.Path with expanded home
print(config["editor_cmd"])      # e.g. "nano"
print(config["kasten"])          # dict of kasten ids and names
print(config["general"]["date_format"])

if __name__ == "__main__":
    app()