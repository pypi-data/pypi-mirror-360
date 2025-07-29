import shutil
from pathlib import Path


def save_module(module_dir_path: str, moduspec: dict, save_to: str) -> str:
    src = Path(module_dir_path)
    if not src.is_dir():
        raise FileNotFoundError(f"Directory not found: {module_dir_path}")

    save_dir = Path(save_to)
    if not save_dir.is_dir():
        save_dir = Path.cwd()

    dest = save_dir / '.modu' / f"{moduspec['name']}@{moduspec['version']}"
    shutil.copytree(src, dest, dirs_exist_ok=True)
    return dest
