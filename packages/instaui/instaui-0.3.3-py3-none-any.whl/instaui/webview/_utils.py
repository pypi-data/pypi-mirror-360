from pathlib import Path
import shutil


def reset_dir(dir_path: Path):
    if dir_path.exists():
        shutil.rmtree(dir_path)
    dir_path.mkdir(exist_ok=True)
