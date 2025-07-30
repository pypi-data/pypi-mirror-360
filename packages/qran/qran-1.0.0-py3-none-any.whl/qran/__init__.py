from importlib.metadata import version

from .mushaf import get_text
from .models import Index


__version__ = version("qran")
__all__ = ["get_text", "Index"]
