"""
Flight Display - Aircraft Tracker with Airport Departure Board Style Display

A Python package for tracking nearby aircraft and displaying them in a beautiful
departure board style interface using real-time ADS-B data.
"""

__version__ = "0.1.0"
__author__ = "Flight Display Team"
__email__ = "contact@flightdisplay.dev"

from .tracker import AircraftTracker

__all__ = ["AircraftTracker"]
