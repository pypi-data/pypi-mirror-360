"""
Module to implement CB14 basin and M9 modifications to Atkinson and Macias (2009) GSIM.
"""

from esi_shakelib.gmpe.modifiable_gmpes.m9_basin import M9BasinTerm


class AtkinsonMacias2009basin(M9BasinTerm):
    """
    Returns basin modification of the Atkinson and Macias (2009) GSIM.
    """

    m9 = False
    SJ = 0

    def __init__(self):
        super().__init__(gmpe_name="AtkinsonMacias2009")


class AtkinsonMacias2009M9basin(M9BasinTerm):
    """
    Returns M9+basin modification of the Atkinson and Macias (2009) GSIM.
    """

    m9 = True
    SJ = 0

    def __init__(self):
        super().__init__(gmpe_name="AtkinsonMacias2009")


class AtkinsonMacias2009Japanbasin(M9BasinTerm):
    """
    Returns Japan basin modification of the Atkinson and Macias (2009) GSIM.
    """

    m9 = False
    SJ = 1

    def __init__(self):
        super().__init__(gmpe_name="AtkinsonMacias2009")


class AtkinsonMacias2009JapanM9basin(M9BasinTerm):
    """
    Returns Japan M9+basin modification of the Atkinson and Macias (2009) GSIM.
    """

    m9 = True
    SJ = 1

    def __init__(self):
        super().__init__(gmpe_name="AtkinsonMacias2009")
