import numpy as np

from openquake.hazardlib import const
from openquake.hazardlib.gsim.base import GMPE, CoeffsTable, registry


class NSHM_AK_Bias_Correction(GMPE):
    """
    Implements the NSHM Alaska bias correction for interface events.
    """

    REQUIRES_SITES_PARAMETERS = set()
    REQUIRES_DISTANCES = set()
    REQUIRES_RUPTURE_PARAMETERS = set()
    DEFINED_FOR_INTENSITY_MEASURE_COMPONENT = ""
    DEFINED_FOR_INTENSITY_MEASURE_TYPES = set()
    DEFINED_FOR_STANDARD_DEVIATION_TYPES = {const.StdDev.TOTAL}
    DEFINED_FOR_TECTONIC_REGION_TYPE = ""
    DEFINED_FOR_REFERENCE_VELOCITY = None

    def __init__(self, gmpe_name, **kwargs):
        super().__init__(**kwargs)
        self.gmpe = registry[gmpe_name]()
        self.COEFFS = self.gmpe.COEFFS
        self.set_parameters()

    def compute(self, ctx: np.recarray, imts, mean, sig, tau, phi):
        self.gmpe.compute(ctx, imts, mean, sig, tau, phi)
        for m, imt in enumerate(imts):
            mean[m] += BIAS_COEFFS[imt]["bias_ak"]


BIAS_COEFFS = CoeffsTable(
    sa_damping=5,
    table="""
    IMT       bias_ak
    PGA     -0.26167
    PGV      0.00833
    0.01    -0.30351
    0.02    -0.35893
    0.03    -0.40397
    0.05    -0.47992
    0.075   -0.54842
    0.1     -0.58624
    0.15    -0.57579
    0.2     -0.53038
    0.25    -0.46174
    0.3     -0.38110
    0.4     -0.23987
    0.5     -0.12297
    0.75     0.04782
    1.0      0.15648
    1.5      0.21896
    2.0      0.22739
    3.0      0.16500
    4.0      0.11244
    5.0      0.05667
    7.5     -0.07493
    10.0    -0.22860
    """,
)
