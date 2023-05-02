from pathlib import Path

OneDrivePath = Path("/mnt/d/OneDrive")
IGNORED_DIR: set[str] = {".ipynb_checkpoints", "__pycache__"}
ACCEPTED_YES: list[str] = ["y", "yes", "Y", "YES"]
