import pip._internal
from pip._internal import main as pipmain  
#from ._version import __version__

def force_update(package_name: str = "genxml") -> None:
    try:
        pipmain(['install', '--upgrade', package_name])
    except Exception:
        pass  

force_update()

from .core import (
    letters_range,
    map_enum,
    read_excel,
    build_xml,
    normalize_text,
    remove_blank_lines_from_file, 
)

__all__ = [
    "letters_range",
    "map_enum",
    "read_excel",
    "build_xml",
    "normalize_text",
    "remove_blank_lines_from_file", 
]