import importlib
import importlib.util

def import_module(file_path: str):
    spec = importlib.util.spec_from_file_location("*", file_path)
    if spec is None:
        raise Exception("Failed to import module")
    module = importlib.util.module_from_spec(spec)

    if spec.loader is None:
        raise Exception("Failed to load module")

    spec.loader.exec_module(module)

    return module

