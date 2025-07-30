"""
Module to implement CB14 basin and M9 modifications to Atkinson and Macias (2009) GSIM.
"""

from esi_shakelib.gmpe.modifiable_gmpes.ak_inter_bias import NSHM_AK_Bias_Correction


class ParkerEtAl2020SInterAK(NSHM_AK_Bias_Correction):
    """
    Returns bias adjustments to the Parker et al. (2020) interface GSIM
    """

    def __init__(self):
        super().__init__(gmpe_name="ParkerEtAl2020SInter")


class AbrahamsonGulerce2020SInterAK(NSHM_AK_Bias_Correction):
    """
    Returns bias adjustments to the Abrahamson and Gulerce (2020) interface GSIM
    """

    def __init__(self):
        super().__init__(gmpe_name="AbrahamsonGulerce2020SInter")


class KuehnEtAl2020SInterAK(NSHM_AK_Bias_Correction):
    """
    Returns bias adjustments to the Kuehn et al. (2020) interface GSIM
    """

    def __init__(self):
        super().__init__(gmpe_name="KuehnEtAl2020SInter")
