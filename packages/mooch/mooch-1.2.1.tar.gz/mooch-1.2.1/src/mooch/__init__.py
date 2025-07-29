from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

from mooch.location.location import Location
from mooch.settings.settings import Settings

__all__ = ["Location", "Settings"]
