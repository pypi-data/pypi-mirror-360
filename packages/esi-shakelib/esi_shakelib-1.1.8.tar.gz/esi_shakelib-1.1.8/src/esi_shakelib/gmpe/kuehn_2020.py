"""
Module to implement supported regional models from Kuehn et al. (2020).
This entire module can be removed (and its import into multigmpe.py) as
soon as the next version of openquake-engine hits pypi (v3.20.1 is the
current version).
"""

from openquake.hazardlib.gsim.base import add_alias
from openquake.hazardlib.gsim.kuehn_2020 import (
    KuehnEtAl2020SInter,
    KuehnEtAl2020SSlab,
    SUPPORTED_REGIONS,
    REGION_ALIASES,
)

for region in SUPPORTED_REGIONS[1:]:
    add_alias(
        "KuehnEtAl2020SInter" + REGION_ALIASES[region],
        KuehnEtAl2020SInter,
        region=region,
    )

for region in SUPPORTED_REGIONS[1:]:
    add_alias(
        "KuehnEtAl2020SSlab" + REGION_ALIASES[region],
        KuehnEtAl2020SSlab,
        region=region,
    )
