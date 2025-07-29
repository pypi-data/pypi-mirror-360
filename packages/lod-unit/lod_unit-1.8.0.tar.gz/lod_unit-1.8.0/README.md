<p align="center">
  <img width = 100 src="https://raw.githubusercontent.com/coreyspohn/lod_unit/main/docs/_static/logo.png" alt="lod_unit logo" />
  <br><br>
</p>

<p align="center">
  <a href="https://codecov.io/gh/CoreySpohn/lod_unit"><img src="https://img.shields.io/codecov/c/github/coreyspohn/lod_unit?token=UCUVYCRWVG&style=flat-square&logo=codecov" alt="Codecov"/></a>
  <a href="https://pypi.org/project/lod_unit/"><img src="https://img.shields.io/pypi/v/lod_unit.svg?style=flat-square" alt="PyPI"/></a>
  <a href="https://lod-unit.readthedocs.io"><img src="https://readthedocs.org/projects/lod_unit/badge/?version=latest&style=flat-square" alt="Documentation Status"/></a>
  <a href="https://github.com/coreyspohn/lod_unit/actions/workflows/ci.yml/"><img src="https://img.shields.io/github/actions/workflow/status/coreyspohn/lod_unit/ci.yml?branch=main&logo=github&style=flat-square" alt="CI"/></a>
</p>




- - -

# lod_unit

This is set up to make it easy to keep coronagraph information in λ/D space with an astropy unit called `lod` ("<ins>L</ins>ambda <ins>O</ins>ver <ins>D</ins>"). Convert into angular units (or vise versa) with an astropy [Equivalency](https://docs.astropy.org/en/stable/units/equivalencies.html) relationship `lod`. See documentation [here](https://lod-unit.readthedocs.io).

## Installation
```bash
pip install lod_unit
```
## Use
Typical use will look like
```python
import astropy.units as u
from astropy.units import equivalencies as equiv
import lod_unit

diam = 10*u.m
lam = 500*u.nm
separation_lod = 3 * u.lod
separation_lod.to(u.arcsec, equiv.lod(lam, diam))
>> <Quantity 0.03093972 arcsec>

separations_as = [0.1, 0.5, 1]*u.arcsec
separations_as.to(u.lod, equiv.lod(lam, diam))
>> <Quantity [ 9.69627362, 48.48136811, 96.96273622] λ/D>
```

### Gosh Corey, that's a lot of releases with no changes

This was a testing place for GitHub tools on the assumption no one would
notice. Go away.
