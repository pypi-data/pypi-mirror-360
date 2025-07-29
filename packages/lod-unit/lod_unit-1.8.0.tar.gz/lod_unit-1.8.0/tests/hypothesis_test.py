"""Tests for the conversion functions in the `lod` module using Hypothesis."""

from hypothesis import given, strategies as st
import astropy.units as u
from lod_unit import lod, lod_eq
from astropy.tests.helper import assert_quantity_allclose


@given(
    diam=st.floats(min_value=0.1, max_value=100.0),
    lam=st.floats(min_value=10.0, max_value=1000.0),
    separation=st.floats(min_value=1.0, max_value=100.0),
)
def test_conversion_cycle(diam: float, lam: float, separation: float):
    """Test that conversion from λ/D to arcseconds and back yields the original value."""
    diam = diam * u.m
    lam = lam * u.nm
    separation_lod = separation * lod

    # Convert to arcseconds and back
    result_arcsec = separation_lod.to(u.arcsec, lod_eq(lam, diam))
    result_lod = result_arcsec.to(lod, lod_eq(lam, diam))

    # Check if we're close to the original value
    assert_quantity_allclose(result_lod, separation_lod, atol=1e-12 * lod)


@given(lam=st.floats(min_value=1e-10, max_value=1e10), diam=st.just(10.0))
# Using `just` for a fixed value
def test_extreme_wavelengths(lam: float, diam: float):
    """Test conversion with a range of wavelengths, including edge cases."""
    diam = diam * u.m
    lam = lam * u.nm
    separation_lod = 3 * lod

    result = separation_lod.to(u.arcsec, lod_eq(lam, diam))
    # Ensure we're getting the right unit type
    assert result.unit == u.arcsec


@given(lam=st.floats(), D=st.floats(), sep=st.floats())
def test_fuzz_lod_eq(lam: float, D: float, sep: float) -> None:
    """Test the `lod_eq` function with random inputs."""
    lam = lam * u.m
    D = D * u.m
    sep = sep * lod
    sep.to(u.rad, lod_eq(lam=lam, D=D))
