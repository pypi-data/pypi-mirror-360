from pathlib import Path
from typing import Dict
from instaui.systems import file_system
from instaui.version import __version__ as _INSTA_VERSION

URL = f"/_instaui_{_INSTA_VERSION}/resource"
_THashPart = str
_HASH_PART_MAP: Dict[_THashPart, Path] = {}
_PATH_URL_MAP: Dict[Path, _THashPart] = {}


def get_folder_path(hash_part: str) -> Path:
    return _HASH_PART_MAP[hash_part]


def record_resource(path: Path):
    path = Path(path).resolve()
    is_file = path.is_file()

    folder_path = path.parent if is_file else path

    if folder_path not in _HASH_PART_MAP:
        hash_part = file_system.generate_hash_name_from_path(folder_path)
        _HASH_PART_MAP[hash_part] = folder_path
    else:
        hash_part = _PATH_URL_MAP[folder_path]

    folder_url = f"{URL}/{hash_part}/"

    return f"{folder_url}{path.name}" if is_file else folder_url
