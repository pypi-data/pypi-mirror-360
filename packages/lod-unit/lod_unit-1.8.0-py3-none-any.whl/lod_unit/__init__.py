"""Initialization for the λ/D unit and equivalency conversion module.

This module makes available the :py:data:`lod` unit, representing the ratio of
wavelength to diameter (λ/D), and :py:func:`lod_eq`, a function providing an
equivalency for converting between λ/D and standard angular units. These tools
are designed to facilitate calculations and conversions in optical systems and
astronomical observations where λ/D is a commonly used metric.

The module is built on the Astropy units and equivalencies framework, ensuring
compatibility with the Astropy ecosystem.

When imported, this module automatically extends astropy's units system to make
the λ/D unit available through the standard astropy.units interface.

Available Items:

- :py:data:`lod` A unit representing λ/D.

- :py:func:`lod_eq` A function to convert between λ/D and angular units, given wavelength and diameter.
"""

__all__ = ["lod", "lod_eq"]
from .lod_unit import lod, lod_eq
import astropy.units as u

from ._version import __version__

setattr(u, "lod", lod)
setattr(u.equivalencies, "lod", lod_eq)
