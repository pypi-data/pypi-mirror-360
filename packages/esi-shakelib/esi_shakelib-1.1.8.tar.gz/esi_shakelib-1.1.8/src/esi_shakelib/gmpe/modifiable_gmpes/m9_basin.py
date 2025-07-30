"""
Module to apply M9 and CB14 basin terms to modified GMPEs.
"""

import numpy as np

from openquake.hazardlib import const
from openquake.hazardlib.gsim.base import GMPE, registry
from openquake.hazardlib.gsim.mgmpe.cb14_basin_term import _get_cb14_basin_term

from esi_shakelib.utils.gmpe_coeffs import get_gmpe_coef_table


class M9BasinTerm(GMPE):
    """
    Implements the NSHM "M9" basin term to be applied to other GMMs for
    Cascadia.
    """

    REQUIRES_SITES_PARAMETERS = {"z2pt5"}
    REQUIRES_DISTANCES = set()
    REQUIRES_RUPTURE_PARAMETERS = set()
    DEFINED_FOR_INTENSITY_MEASURE_COMPONENT = ""
    DEFINED_FOR_INTENSITY_MEASURE_TYPES = set()
    DEFINED_FOR_STANDARD_DEVIATION_TYPES = {const.StdDev.TOTAL}
    DEFINED_FOR_TECTONIC_REGION_TYPE = ""
    DEFINED_FOR_REFERENCE_VELOCITY = None

    m9 = False
    SJ = 0

    def __init__(self, gmpe_name, **kwargs):
        super().__init__(**kwargs)
        self.gmpe = registry[gmpe_name]()
        self.COEFFS = get_gmpe_coef_table(self.gmpe)
        self.set_parameters()

    def compute(self, ctx: np.recarray, imts, mean, sig, tau, phi):
        self.gmpe.compute(ctx, imts, mean, sig, tau, phi)
        for m, imt in enumerate(imts):
            fb = _get_cb14_basin_term(imt, ctx, self.SJ)
            if self.m9:
                fb_m9 = np.log(2.0)
                idx = ctx.z2pt5 > 6.0
                if imt.period > 1.9:
                    fb[idx] = fb_m9
            mean[m] += fb
