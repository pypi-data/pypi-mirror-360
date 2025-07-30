"""
Module to find coefficient tables and SA params of GMPEs.
"""


def get_gmpe_coef_table(gmpe):
    """
    Method for finding the (or "a") GMPE table.

    Notes:

      *  The reason for the complexity here is that there can be multiple
         coefficient tables, and some of them may not have the sa_coeffs
         attribute, which is the main reason for getting the table.
      *  We are also assuming that if there are more than one  coefficient
         table, the range of periods will be the same across all of the
         tables.

    Args:
        gmpe (GMPE): An OQ GMPE instance.

    Returns:
        The associated coefficient table.

    """
    stuff = dir(gmpe)
    coef_list = [s for s in stuff if "COEFFS" in s]
    for coef_sel in coef_list:
        cobj = getattr(gmpe, coef_sel)
        if "sa_coeffs" in dir(cobj):
            return cobj
    raise NotImplementedError(f"GMPE {gmpe} does not contain sa_coeffs attribute.")


def get_gmpe_sa_periods(gmpe):
    """
    Method to extract the SA periods defined by a GMPE.

    Args:
        gmpe (GMPE): A GMPE instance.

    Retunrs:
        list: List of periods.

    """
    if gmpe == "[NGAEast]":
        per = gmpe.per_array
    else:
        ctab = get_gmpe_coef_table(gmpe).sa_coeffs
        ilist = list(ctab.keys())
        per = [i.period for i in ilist]
    return per
