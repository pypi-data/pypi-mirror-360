"""This module contains tests for the lod_unit module."""

import astropy.units as u
from lod_unit import lod, lod_eq
from astropy.tests.helper import assert_quantity_allclose


def test_separation_to_arcsec():
    """Test the conversion from separation to arcseconds."""
    diam = 10 * u.m
    lam = 500 * u.nm
    separation_lod = 3 * lod
    result = separation_lod.to(u.arcsec, lod_eq(lam, diam))  # pyright: ignore

    expected_arcsec = 0.03093972 * u.arcsec

    # Using astropy's quantity_allclose for comparison due to potential floating-point inaccuracies
    (
        assert_quantity_allclose(result, expected_arcsec),
        f"Expected {expected_arcsec}, got {result}",
    )  # pyright: ignore


def test_arcsec_to_separation():
    """Test the conversion from arcseconds to separation."""
    diam = 10 * u.m
    lam = 500 * u.nm
    separations_as = [0.1, 0.5, 1] * u.arcsec
    expected_lod = [9.69627362, 48.48136811, 96.96273622] * lod
    result = separations_as.to(lod, lod_eq(lam, diam))

    (
        assert_quantity_allclose(result, expected_lod),
        f"Expected {expected_lod}, got {result}",
    )  # pyright: ignore
