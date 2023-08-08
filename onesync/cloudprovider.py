from pathlib import Path


class CloudProvider:
    def create(self):
        ...

    def get(self):
        ...

    def put(self):
        ...

    def delete(self):
        ...


class OneDrive(CloudProvider):
    root_dir: Path
