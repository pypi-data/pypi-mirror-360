
import pathlib
from typing import List

from .errors import InvalidAppError

def get_all_apps(path: pathlib.Path) -> List[str]:
    apps = []
    apps_dir = path / "apps"
    if not apps_dir.exists():
        raise InvalidAppError(f"Apps directory not found at {apps_dir}")
    for app in apps_dir.iterdir():
        if app.is_dir():
            app_name = app.name
            if app_name.startswith(".") or app_name == "__pycache__":
                continue
            app_file = app / f"{app_name}.py"
            if app_file.exists():
                apps.append(app_name)
    return apps