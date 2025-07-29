import os
import pathlib
import sys
import importlib.util
import zipfile
import tempfile
import json
import shutil
import atexit
from typing import Optional
from . import __version__
from .transpiler import parse_clyp

_loaded_clb_modules = {}
_temp_dirs = []


def cleanup_clb_temps():
    for temp_dir in _temp_dirs:
        shutil.rmtree(temp_dir, ignore_errors=True)
    _temp_dirs.clear()


atexit.register(cleanup_clb_temps)


def clyp_include(clb_path: str, calling_file: str):
    """
    Loads a .clb file, checks for compatibility, and imports the module.
    """
    base_dir = pathlib.Path(calling_file).parent
    clb_file_path = base_dir / clb_path

    if not clb_file_path.exists():
        raise FileNotFoundError(f"CLB file not found: {clb_file_path}")

    clb_abs_path = str(clb_file_path.resolve())
    if clb_abs_path in _loaded_clb_modules:
        return _loaded_clb_modules[clb_abs_path]

    temp_dir = tempfile.mkdtemp()
    _temp_dirs.append(temp_dir)

    try:
        with zipfile.ZipFile(clb_file_path, "r") as zf:
            zf.extract("metadata.json", temp_dir)
            with open(pathlib.Path(temp_dir) / "metadata.json", "r") as f:
                metadata = json.load(f)

            if metadata.get("clyp_version") != __version__:
                print(
                    f"Warning: Clyp version mismatch. File was built with {metadata.get('clyp_version')}, running {__version__}.",
                    file=sys.stderr,
                )
            if metadata.get("platform") != sys.platform:
                print(
                    f"Warning: Platform mismatch. File was built for {metadata.get('platform')}, running on {sys.platform}.",
                    file=sys.stderr,
                )

            module_filename = metadata["module_filename"]
            zf.extract(module_filename, temp_dir)

            module_path = pathlib.Path(temp_dir) / module_filename
            module_name = module_path.stem.split(".")[0]

            sys.path.insert(0, temp_dir)

            spec = importlib.util.find_spec(module_name)
            if spec is None:
                raise ImportError(f"Could not find compiled module spec in {clb_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            _loaded_clb_modules[clb_abs_path] = module
            # Make the module available globally
            globals()[module_name] = module
            return module

    except Exception as e:
        shutil.rmtree(temp_dir)
        if temp_dir in _temp_dirs:
            _temp_dirs.remove(temp_dir)
        raise ImportError(f"Failed to load CLB file {clb_path}: {e}")


def clyp_import(module_name: str, current_file_path: Optional[str] = None) -> object:
    """
    Imports a .clyp file as a Python module.
    """
    module_path = module_name.replace(".", os.path.sep) + ".clyp"

    search_paths = []
    if current_file_path:
        search_paths.append(os.path.dirname(current_file_path))
    search_paths.extend(sys.path)

    found_path = None
    for path in search_paths:
        potential_path = os.path.join(path, module_path)
        if os.path.exists(potential_path):
            found_path = os.path.abspath(potential_path)
            break

    if not found_path:
        raise ImportError(
            f"Could not find clyp module '{module_name}' at '{module_path}'"
        )

    module_key = f"clyp_module.{found_path}"

    if module_key in sys.modules:
        return sys.modules[module_key]

    with open(found_path, "r") as f:
        clyp_code = f.read()

    python_code = parse_clyp(clyp_code, file_path=found_path)

    spec = importlib.util.spec_from_loader(module_name, loader=None, origin=found_path)
    if spec is None:
        raise ImportError(f"Could not create spec for clyp module '{module_name}'")

    module = importlib.util.module_from_spec(spec)

    setattr(module, "__file__", found_path)

    sys.modules[module_key] = module
    sys.modules[module_name] = module

    exec(python_code, module.__dict__)

    return module


def find_clyp_imports(file_path: str):
    """
    Parses a .clyp file and returns a list of imported modules.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        clyp_code = f.read()

    imports = []
    for line in clyp_code.split("\n"):
        if line.strip().startswith("import "):
            parts = line.strip().split()
            if len(parts) > 1:
                imports.append(parts[1])
    return imports
