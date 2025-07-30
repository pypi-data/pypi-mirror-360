"""
Module to implement CB14 basin and M9 modifications to Zhao et al. (2006) GSIM.
"""

from esi_shakelib.gmpe.modifiable_gmpes.m9_basin import M9BasinTerm


class ZhaoEtAl2006SInterBasin(M9BasinTerm):
    """
    Returns basin modification of the Zhao et al. (2009) interface GSIM.
    """

    m9 = False
    SJ = 0

    def __init__(self):
        super().__init__(gmpe_name="ZhaoEtAl2006SInter")


class ZhaoEtAl2006SInterM9Basin(M9BasinTerm):
    """
    Returns M9+basin modification of the Zhao et al. (2009) interface GSIM.
    """

    m9 = True
    SJ = 0

    def __init__(self):
        super().__init__(gmpe_name="ZhaoEtAl2006SInter")


class ZhaoEtAl2006SSlabBasin(M9BasinTerm):
    """
    Returns basin modification of the Zhao et al. (2009) slab GSIM.
    """

    m9 = False
    SJ = 0

    def __init__(self):
        super().__init__(gmpe_name="ZhaoEtAl2006SSlab")


class ZhaoEtAl2006SInterJapanM9Basin(M9BasinTerm):
    """
    Returns Japan M9+basin modification of the Zhao et al. (2009) interface GSIM.
    """

    m9 = True
    SJ = 1

    def __init__(self):
        super().__init__(gmpe_name="ZhaoEtAl2006SInter")


class ZhaoEtAl2006SSlabJapanBasin(M9BasinTerm):
    """
    Returns Japan basin modification of the Zhao et al. (2009) slab GSIM.
    """

    m9 = False
    SJ = 1

    def __init__(self):
        super().__init__(gmpe_name="ZhaoEtAl2006SSlab")


class ZhaoEtAl2006SInterCascadiaM9Basin(M9BasinTerm):
    """
    Returns Cascadia M9+basin modification of the Zhao et al. (2009) interface GSIM.
    """

    m9 = True
    SJ = 0

    def __init__(self):
        super().__init__(gmpe_name="ZhaoEtAl2006SInterCascadia")


class ZhaoEtAl2006SSlabCascadiaBasin(M9BasinTerm):
    """
    Returns Cascadia basin modification of the Zhao et al. (2009) slab GSIM.
    """

    m9 = False
    SJ = 0

    def __init__(self):
        super().__init__(gmpe_name="ZhaoEtAl2006SSlabCascadia")
