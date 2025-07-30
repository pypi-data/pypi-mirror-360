import os
import warnings
from typing import List, Optional
import importlib.metadata
import sys

def get_requirement(
    path: Optional[str] = None,
    strip: bool = False,
    deduplicate: bool = True
) -> Optional[List[str]]:
    """
    Reads a requirements.txt file and returns a list of dependencies.

    Parameters:
    ----------
    path : str or None
        Path to the requirements.txt file. If None, looks for it in the current directory.
    strip : bool
        If True, strips version specifiers (e.g., 'requests==2.0' → 'requests')
    deduplicate : bool
        If True, removes duplicate packages

    Returns:
    -------
    list[str] or None
        List of requirement lines or None if file not found.
    """
    if path is None:
        path = os.path.join(os.getcwd(), "requirements.txt")

    if not os.path.exists(path):
            
            ##### Detect if called from CLI#####
            is_cli = sys.argv[0].endswith(".py") or os.path.basename(sys.argv[0]) in {"reqbuddy"}

            message = (
                f"'{path}' not found.\n"
                f"{'👉 Use: reqbuddy find' if is_cli else '👉 Use `find_requirement()` to generate it.'}"
            )

            if is_cli:
                print(message, file=sys.stderr)
            else:
                warnings.warn(message, stacklevel=2)

            return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except UnicodeDecodeError:
        with open(path, "r", encoding="latin-1") as f:
            lines = f.read().splitlines()

    requirements = []
    seen = set()
    version_operators = ["==", ">=", "<=", "~=", "!=", ">", "<"]

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        
        if " #" in line:
            line = line.split(" #", 1)[0].strip()

        
        name = line
        if strip:
            for op in version_operators:
                if op in line:
                    name = line.split(op, 1)[0].strip()
                    break
            line = name

        if deduplicate and name in seen:
            continue

        seen.add(name)
        requirements.append(line)

    return requirements





def find_requirement(strip: bool = False, save: bool = True) -> List[str]:
    """
    Returns a list of installed packages in the current Python environment,
    and optionally saves them to a requirements.txt file.

    Parameters:
    ----------
        strip (bool): If True, only package names are returned without version numbers.
                               If False, returns package names with versions (e.g., 'package==version').
        save (bool): If True, saves the output to 'requirements.txt'. Defaults to True.

    Returns:
    -------
        List[str]: A list of installed packages as strings.
    """
    packages = []
    for dist in importlib.metadata.distributions():
        name = dist.metadata["Name"]
        version = dist.version
        pkg_str = name if strip else f"{name}=={version}"
        packages.append(pkg_str)

    if save:
        with open("requirements.txt", "w") as f:
            for pkg in packages:
                f.write(pkg + "\n")

    return packages