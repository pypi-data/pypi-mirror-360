from importlib.resources import as_file, files
from pathlib import Path


def get_fixture_path(asset_name: str) -> Path:
    with as_file(files(__name__).joinpath(asset_name)) as path:
        return Path(path)
