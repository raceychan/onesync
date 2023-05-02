from pathlib import Path

# Some should be resolved from env
OneDrivePath = Path("/mnt/d/OneDrive")
IGNORED_DIR: set[str] = {".ipynb_checkpoints", "__pycache__"}
ACCEPTED_YES: list[str] = ["y", "yes", "Y", "YES"]
