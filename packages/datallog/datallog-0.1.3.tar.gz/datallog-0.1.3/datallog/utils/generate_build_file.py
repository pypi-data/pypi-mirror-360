import json
from pathlib import Path
import sys
import threading
from typing import Any, Dict
from .get_all_apps import get_all_apps
import json
from .import_module import  import_module
from .generate_step_props import generate_step_props
from .storage import reset_storage

def generate_build_file(deploy_dir: Path, output_file_path: Path) -> Dict[str, Any]:
    apps = get_all_apps(deploy_dir)

    build: Dict[str, Any] = {}
    apps_dir = deploy_dir / "apps"
    print(f"Generating build file for apps in {apps_dir}")
    for app_name in apps:
        try:
            app_file = apps_dir / app_name / f'{app_name}.py'
            num_of_threads = threading.active_count()
            reset_storage()
            import_module(app_file)
            if threading.active_count() > num_of_threads:
                print(f"Warning: {app_name} has threads running, this may cause issues with the build file generation.")
            
        
            step_props = generate_step_props(app_name)
            
            build[app_name] = step_props
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error generating build file for {app_name}: {e}", file=sys.stderr)
            exit(1)
    with open(output_file_path, 'w') as f:
        json.dump(build, f, indent=4)

    return build


if __name__ == "__main__":

    deploy_dir = Path('/deploy')
    output_file_path = Path('/build.json')

    build_file = generate_build_file(deploy_dir, output_file_path)
    