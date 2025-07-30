"""
Sky Ceiling Projector - A realistic starfield and weather projection system.

A Python application that creates beautiful, realistic sky simulations with:
- Enhanced starfield with variable stars, giants, and supergiants
- Detailed weather effects synchronized with real weather data
- Realistic moon phases and sun/moon positioning
- Dynamic celestial events (meteors, satellites, planets)
- Location-based time zones and smooth transitions
"""

__version__ = "1.0.0"
__author__ = "Sean Bailey"
__email__ = "sean_bailey@baileytec.net"
__description__ = "Realistic sky ceiling projector with weather integration"

# Main exports
from .projector import SkySimulator

__all__ = [
    "SkySimulator",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]