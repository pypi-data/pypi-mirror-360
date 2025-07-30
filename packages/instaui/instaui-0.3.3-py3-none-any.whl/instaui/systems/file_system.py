from pathlib import Path
import hashlib


def generate_hash_name_from_path(path: Path):
    return hashlib.sha256(path.as_posix().encode()).hexdigest()[:32]
