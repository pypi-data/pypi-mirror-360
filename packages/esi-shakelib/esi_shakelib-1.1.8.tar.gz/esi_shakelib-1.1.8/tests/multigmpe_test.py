#!/usr/bin/env python

# stdlib imports
import copy
import os
import sys
import time as time
import datetime

# third party imports
import numpy as np
import pytest
from openquake.hazardlib import const, imt
from openquake.hazardlib.gsim.abrahamson_2014 import AbrahamsonEtAl2014
from openquake.hazardlib.gsim.atkinson_boore_2006 import AtkinsonBoore2006
from openquake.hazardlib.gsim.boore_2014 import BooreEtAl2014
from openquake.hazardlib.gsim.campbell_2003 import (
    Campbell2003,
    Campbell2003MwNSHMP2008,
)
from openquake.hazardlib.gsim.campbell_bozorgnia_2008 import (
    CampbellBozorgnia2008,
)
from openquake.hazardlib.gsim.campbell_bozorgnia_2014 import (
    CampbellBozorgnia2014,
)
from openquake.hazardlib.gsim.chiou_youngs_2008 import ChiouYoungs2008
from openquake.hazardlib.gsim.chiou_youngs_2014 import ChiouYoungs2014
from openquake.hazardlib.gsim.pezeshk_2011 import PezeshkEtAl2011NEHRPBC
from openquake.hazardlib.gsim.zhao_2006 import ZhaoEtAl2006Asc

from esi_utils_rupture.distance import Distance
from esi_utils_rupture.origin import Origin
from esi_utils_rupture.point_rupture import PointRupture
from esi_utils_rupture.quad_rupture import QuadRupture
from esi_shakelib.utils.contexts import (
    DistancesContext,
    RuptureContext,
    SitesContext,
)

# local imports
import esi_shakelib.sites as sites
from esi_shakelib.sites import (
    _z2pt5_from_vs30_cb14_cal,
    _z1pt0_from_vs30_ask14_cal,
    _z1pt0_from_vs30_cy14_cal,
)
from esi_shakelib.conversions.imc.boore_kishida_2017 import BooreKishida2017
from esi_shakelib.multigmpe import (
    MultiGMPE,
    filter_gmpe_list,
    set_sites_depth_parameters,
    stuff_context,
)

homedir = os.path.dirname(os.path.abspath(__file__))  # where is this script?
shakedir = os.path.abspath(os.path.join(homedir, ".."))
sys.path.insert(0, shakedir)

TEST = True


def test_basic():
    # Most basic possible test of MultiGMPE
    ASK14 = AbrahamsonEtAl2014()

    IMT = imt.SA(1.0)
    size = 100
    rctx = RuptureContext()
    dctx = DistancesContext()
    sctx = SitesContext()
    sctx_rock = SitesContext()

    rctx.rake = 0.0
    rctx.dip = 90.0
    rctx.ztor = 0.0
    rctx.mag = 8.0
    rctx.width = 10.0
    rctx.hypo_depth = 8.0

    dctx.rjb = np.logspace(1, np.log10(800), 100)
    dctx.rrup = dctx.rjb
    dctx.rhypo = dctx.rjb
    dctx.rx = dctx.rjb
    dctx.ry0 = dctx.rjb

    sctx.sids = np.array(range(size))
    sctx.vs30 = np.ones_like(dctx.rjb) * 275.0
    sctx.vs30measured = np.full_like(dctx.rjb, False, dtype="bool")
    set_sites_depth_parameters(sctx, ASK14)

    mgmpe = MultiGMPE.__from_list__([ASK14], [1.0], imc=const.IMC.RotD50)

    ctx = stuff_context(sctx, rctx, dctx)
    lmean_ask14, sd_ask14 = ASK14.get_mean_and_stddevs(
        ctx, ctx, ctx, IMT, [const.StdDev.TOTAL]
    )
    lmean_mgmpe, sd_mgmpe = mgmpe.get_mean_and_stddevs(
        sctx, rctx, dctx, IMT, [const.StdDev.TOTAL]
    )

    np.testing.assert_allclose(lmean_ask14, lmean_mgmpe[0])
    np.testing.assert_allclose(sd_ask14, [sd_mgmpe[0]])

    # Two similar GMPEs, both with site terms
    CY14 = ChiouYoungs2014()
    mgmpe = MultiGMPE.__from_list__(
        [ASK14, CY14], [0.6, 0.4], imc=const.IMC.RotD50
    )
    set_sites_depth_parameters(sctx, CY14)
    ctx = stuff_context(sctx, rctx, dctx)
    lmean_cy14, sd_cy14 = CY14.get_mean_and_stddevs(
        ctx, ctx, ctx, IMT, [const.StdDev.TOTAL]
    )
    lmean_mgmpe, sd_mgmpe = mgmpe.get_mean_and_stddevs(
        sctx, rctx, dctx, IMT, [const.StdDev.TOTAL]
    )
    lmean_target = 0.6 * lmean_ask14 + 0.4 * lmean_cy14
    np.testing.assert_allclose(lmean_target, lmean_mgmpe[0])

    # Two multi-GMPEs
    mgmpe1 = MultiGMPE.__from_list__(
        [ASK14, CY14], [0.6, 0.4], imc=const.IMC.RotD50
    )
    mgmpe2 = MultiGMPE.__from_list__([ASK14], [1.0], imc=const.IMC.RotD50)
    mgmpe = MultiGMPE.__from_list__(
        [mgmpe1, mgmpe2], [0.3, 0.7], imc=const.IMC.RotD50
    )
    lmean_mgmpe, sd_mgmpe = mgmpe.get_mean_and_stddevs(
        sctx, rctx, dctx, IMT, [const.StdDev.TOTAL]
    )
    tmp1 = 0.6 * lmean_ask14 + 0.4 * lmean_cy14
    tmp2 = 1.0 * lmean_ask14
    lmean_target = 0.3 * tmp1 + 0.7 * tmp2
    np.testing.assert_allclose(lmean_target, lmean_mgmpe[0])


def test_filter_gmpe_list():
    gmpelist = [Campbell2003MwNSHMP2008(), AtkinsonBoore2006()]
    wts = [0.5, 0.5]
    fgmpes, fwts = filter_gmpe_list(gmpelist, wts, imt=imt.PGA())
    assert fgmpes == gmpelist
    assert np.all(wts == fwts)

    fgmpes, fwts = filter_gmpe_list(gmpelist, wts, imt=imt.PGV())
    assert fgmpes == gmpelist
    assert np.all(wts == fwts)

    fgmpes, fwts = filter_gmpe_list(gmpelist, wts, imt=imt.SA(3.5))
    assert fgmpes == [gmpelist[1]]
    assert fwts == [1.0]


def test_from_config_set_of_sets():
    # Mock up a minimal config dictionary
    conf = {
        "gmpe_modules": {
            "ASK14": [
                "AbrahamsonEtAl2014",
                "openquake.hazardlib.gsim.abrahamson_2014",
            ],
            "C03": [
                "Campbell2003MwNSHMP2008",
                "openquake.hazardlib.gsim.campbell_2003",
            ],
            "Pea11": [
                "PezeshkEtAl2011NEHRPBC",
                "openquake.hazardlib.gsim.pezeshk_2011",
            ],
        },
        "gmpe_sets": {
            "active_crustal": {
                "gmpes": ["ASK14"],
                "weights": [1.0],
            },
            "stable_continental": {
                "gmpes": ["C03", "Pea11"],
                "weights": [0.5, 0.5],
            },
            "active_crustal_80_stable_continental_20": {
                "gmpes": ["active_crustal", "stable_continental"],
                "weights": [0.8, 0.2],
            },
        },
        "gmpe_limits": {},
        "modeling": {"gmpe": "active_crustal_80_stable_continental_20"},
        "interp": {"component": "RotD50"},
    }

    # Get multigmpe from config
    test = MultiGMPE.__from_config__(conf)

    # Compute "by hand"
    ASK14 = AbrahamsonEtAl2014()
    C03 = Campbell2003MwNSHMP2008()
    Pea11 = PezeshkEtAl2011NEHRPBC()

    IMT = imt.SA(1.0)
    size = 100
    rctx = RuptureContext()
    dctx = DistancesContext()
    sctx = SitesContext()
    sctx_rock = SitesContext()
    sctx.sids = np.array(range(size))
    sctx_rock.sids = np.array(range(size))

    rctx.rake = 0.0
    rctx.dip = 90.0
    rctx.ztor = 0.0
    rctx.mag = 8.0
    rctx.width = 10.0
    rctx.hypo_depth = 8.0

    dctx.rjb = np.logspace(1, np.log10(800), size)
    dctx.rrup = dctx.rjb
    dctx.rhypo = dctx.rjb
    dctx.rx = dctx.rjb
    dctx.ry0 = dctx.rjb

    sctx.vs30 = np.ones_like(dctx.rjb) * 275.0
    sctx.vs30measured = np.full_like(dctx.rjb, False, dtype="bool")
    sctx_rock.vs30 = np.ones_like(dctx.rjb) * 760.0
    sctx_rock.vs30measured = np.full_like(dctx.rjb, False, dtype="bool")

    set_sites_depth_parameters(sctx, ASK14)
    set_sites_depth_parameters(sctx_rock, ASK14)

    ctx = stuff_context(sctx, rctx, dctx)
    lmean_ask14, lsd_ask14 = ASK14.get_mean_and_stddevs(
        ctx, ctx, ctx, IMT, [const.StdDev.TOTAL]
    )
    ctx = stuff_context(sctx_rock, rctx, dctx)
    lmean_ask14_rock, dummy = ASK14.get_mean_and_stddevs(
        ctx, ctx, ctx, IMT, [const.StdDev.TOTAL]
    )

    ctx = stuff_context(sctx, rctx, dctx)
    lmean_c03, lsd_c03 = C03.get_mean_and_stddevs(
        ctx, ctx, ctx, IMT, [const.StdDev.TOTAL]
    )
    bk17 = BooreKishida2017(
        C03.DEFINED_FOR_INTENSITY_MEASURE_COMPONENT, const.IMC.RotD50
    )
    lmean_c03 = bk17.convertAmps(IMT, lmean_c03, ctx.rrup, ctx.mag)
    lsd_c03 = bk17.convertSigmas(IMT, lsd_c03[0])

    ctx = stuff_context(sctx, rctx, dctx)
    lmean_pea11, lsd_pea11 = Pea11.get_mean_and_stddevs(
        ctx, ctx, ctx, IMT, [const.StdDev.TOTAL]
    )
    bk17 = BooreKishida2017(
        Pea11.DEFINED_FOR_INTENSITY_MEASURE_COMPONENT, const.IMC.RotD50
    )
    lmean_pea11 = bk17.convertAmps(IMT, lmean_pea11, ctx.rrup, ctx.mag)
    lsd_pea11 = bk17.convertSigmas(IMT, lsd_pea11[0])

    lmean_acr = copy.copy(lmean_ask14)
    lmean_scr = 0.5 * lmean_c03 + 0.5 * lmean_pea11
    lmean_target = 0.8 * lmean_acr + 0.2 * lmean_scr

    lmean, sd = test.get_mean_and_stddevs(
        sctx, rctx, dctx, IMT, [const.StdDev.TOTAL]
    )
    np.testing.assert_allclose(lmean_target, lmean[0])

    # Do the stddev: this is a two-step process because each
    # sub-MultiGMPE is computed and then they are combined

    wts = np.array([0.5, 0.5]).reshape((1, -1))
    cc = np.corrcoef([lmean_c03, lmean_pea11])
    cc = ((wts * wts.T) * cc).reshape((2, 2, 1))
    sdlist = [lsd_c03.reshape((1, 1, -1)), lsd_pea11.reshape((1, 1, -1))]
    sdstack = np.hstack(sdlist)
    wcov = (sdstack * np.transpose(sdstack, axes=(1, 0, 2))) * cc
    lnsd_scr = np.sqrt(wcov.sum((0, 1)))

    wts = np.array([0.8, 0.2]).reshape((1, -1))
    cc = np.corrcoef([lmean_ask14, lmean_scr])
    cc = ((wts * wts.T) * cc).reshape((2, 2, 1))
    sdlist = [lsd_ask14[0].reshape((1, 1, -1)), lnsd_scr.reshape((1, 1, -1))]
    sdstack = np.hstack(sdlist)
    wcov = (sdstack * np.transpose(sdstack, axes=(1, 0, 2))) * cc
    lnsd2 = np.sqrt(wcov.sum((0, 1)))
    np.testing.assert_allclose(lnsd2, sd[0])


def test_from_config_set_of_gmpes():
    # Mock up a minimal config dictionary
    conf = {
        "gmpe_modules": {
            "ASK14": [
                "AbrahamsonEtAl2014",
                "openquake.hazardlib.gsim.abrahamson_2014",
            ],
            "C03": [
                "Campbell2003MwNSHMP2008",
                "openquake.hazardlib.gsim.campbell_2003",
            ],
            "Pea11": [
                "PezeshkEtAl2011NEHRPBC",
                "openquake.hazardlib.gsim.pezeshk_2011",
            ],
        },
        "gmpe_sets": {
            "stable_continental": {
                "gmpes": ["C03", "Pea11"],
                "weights": [0.5, 0.5],
            }
        },
        "gmpe_limits": {},
        "modeling": {
            "gmpe": "stable_continental",
        },
        "interp": {"component": "RotD50"},
    }

    # Get multigmpe from config
    test = MultiGMPE.__from_config__(conf)

    # Compute "by hand"
    ASK14 = AbrahamsonEtAl2014()
    C03 = Campbell2003MwNSHMP2008()
    Pea11 = PezeshkEtAl2011NEHRPBC()

    IMT = imt.SA(1.0)
    size = 100
    rctx = RuptureContext()
    dctx = DistancesContext()
    sctx = SitesContext()
    sctx_rock = SitesContext()
    sctx.sids = np.array(range(size))
    sctx_rock.sids = np.array(range(size))

    rctx.rake = 0.0
    rctx.dip = 90.0
    rctx.ztor = 0.0
    rctx.mag = 8.0
    rctx.width = 10.0
    rctx.hypo_depth = 8.0

    dctx.rjb = np.logspace(1, np.log10(800), size)
    dctx.rrup = dctx.rjb
    dctx.rhypo = dctx.rjb
    dctx.rx = dctx.rjb
    dctx.ry0 = dctx.rjb

    sctx.vs30 = np.ones_like(dctx.rjb) * 275.0
    sctx.vs30measured = np.full_like(dctx.rjb, False, dtype="bool")
    sctx_rock.vs30 = np.ones_like(dctx.rjb) * 760.0
    sctx_rock.vs30measured = np.full_like(dctx.rjb, False, dtype="bool")

    set_sites_depth_parameters(sctx, ASK14)
    set_sites_depth_parameters(sctx_rock, ASK14)

    ctx = stuff_context(sctx, rctx, dctx)
    lmean_ask14, dummy = ASK14.get_mean_and_stddevs(
        ctx, ctx, ctx, IMT, [const.StdDev.TOTAL]
    )
    ctx = stuff_context(sctx_rock, rctx, dctx)
    lmean_ask14_rock, dummy = ASK14.get_mean_and_stddevs(
        ctx, ctx, ctx, IMT, [const.StdDev.TOTAL]
    )
    ctx = stuff_context(sctx, rctx, dctx)
    lmean_c03, dummy = C03.get_mean_and_stddevs(
        ctx, ctx, ctx, IMT, [const.StdDev.TOTAL]
    )
    bk17 = BooreKishida2017(
        C03.DEFINED_FOR_INTENSITY_MEASURE_COMPONENT, const.IMC.RotD50
    )
    lmean_c03 = bk17.convertAmps(IMT, lmean_c03, ctx.rrup, ctx.mag)
    ctx = stuff_context(sctx, rctx, dctx)
    lmean_pea11, dummy = Pea11.get_mean_and_stddevs(
        ctx, ctx, ctx, IMT, [const.StdDev.TOTAL]
    )
    bk17 = BooreKishida2017(
        Pea11.DEFINED_FOR_INTENSITY_MEASURE_COMPONENT, const.IMC.RotD50
    )
    lmean_pea11 = bk17.convertAmps(IMT, lmean_pea11, ctx.rrup, ctx.mag)

    lmean_scr = 0.5 * lmean_c03 + 0.5 * lmean_pea11
    lmean_target = lmean_scr

    lmean, sd = test.get_mean_and_stddevs(
        sctx, rctx, dctx, IMT, [const.StdDev.TOTAL]
    )
    np.testing.assert_allclose(lmean_target, lmean[0])


def test_from_config_set_of_sets_3_sec():
    # Mock up a minimal config dictionary
    conf = {
        "gmpe_modules": {
            "ASK14": [
                "AbrahamsonEtAl2014",
                "openquake.hazardlib.gsim.abrahamson_2014",
            ],
            "C03": [
                "Campbell2003MwNSHMP2008",
                "openquake.hazardlib.gsim.campbell_2003",
            ],
            "Pea11": [
                "PezeshkEtAl2011NEHRPBC",
                "openquake.hazardlib.gsim.pezeshk_2011",
            ],
        },
        "gmpe_sets": {
            "active_crustal": {
                "gmpes": ["ASK14"],
                "weights": [1.0],
            },
            "stable_continental": {
                "gmpes": ["C03", "Pea11"],
                "weights": [0.5, 0.5],
                "weights_large_dist": [0, 1.0],
                "dist_cutoff": 500,
                "site_gmpes": ["ASK14"],
                "weights_site_gmpes": [],
            },
            "active_crustal_80_stable_continental_20": {
                "gmpes": ["active_crustal", "stable_continental"],
                "weights": [0.8, 0.2],
            },
        },
        "gmpe_limits": {},
        "modeling": {"gmpe": "active_crustal_80_stable_continental_20"},
        "interp": {"component": "RotD50"},
    }

    IMT = imt.SA(3.0)
    # Get multigmpe from config
    test = MultiGMPE.__from_config__(conf, filter_imt=IMT)

    # Compute "by hand"
    ASK14 = AbrahamsonEtAl2014()
    Pea11 = PezeshkEtAl2011NEHRPBC()

    size = 100
    rctx = RuptureContext()
    dctx = DistancesContext()
    sctx = SitesContext()
    sctx_rock = SitesContext()
    sctx.sids = np.array(range(size))
    sctx_rock.sids = np.array(range(size))

    rctx.rake = 0.0
    rctx.dip = 90.0
    rctx.ztor = 0.0
    rctx.mag = 8.0
    rctx.width = 10.0
    rctx.hypo_depth = 8.0

    dctx.rjb = np.logspace(1, np.log10(800), size)
    dctx.rrup = dctx.rjb
    dctx.rhypo = dctx.rjb
    dctx.rx = dctx.rjb
    dctx.ry0 = dctx.rjb

    sctx.vs30 = np.ones_like(dctx.rjb) * 275.0
    sctx.vs30measured = np.full_like(dctx.rjb, False, dtype="bool")
    sctx_rock.vs30 = np.ones_like(dctx.rjb) * 760.0
    sctx_rock.vs30measured = np.full_like(dctx.rjb, False, dtype="bool")

    set_sites_depth_parameters(sctx, ASK14)
    set_sites_depth_parameters(sctx_rock, ASK14)

    ctx = stuff_context(sctx, rctx, dctx)
    lmean_ask14, dummy = ASK14.get_mean_and_stddevs(
        ctx, ctx, ctx, IMT, [const.StdDev.TOTAL]
    )
    ctx = stuff_context(sctx_rock, rctx, dctx)
    lmean_ask14_rock, dummy = ASK14.get_mean_and_stddevs(
        ctx, ctx, ctx, IMT, [const.StdDev.TOTAL]
    )
    #    lmean_c03, dummy = C03.get_mean_and_stddevs(
    #        sctx, rctx, dctx, IMT, [const.StdDev.TOTAL])
    #    bk17 = BooreKishida2017(C03.DEFINED_FOR_INTENSITY_MEASURE_COMPONENT,
    #                            const.IMC.RotD50)
    #    lmean_c03 = bk17.convertAmps(IMT, lmean_c03, dctx.rrup, rctx.mag)
    ctx = stuff_context(sctx, rctx, dctx)
    lmean_pea11, dummy = Pea11.get_mean_and_stddevs(
        ctx, ctx, ctx, IMT, [const.StdDev.TOTAL]
    )
    bk17 = BooreKishida2017(
        Pea11.DEFINED_FOR_INTENSITY_MEASURE_COMPONENT, const.IMC.RotD50
    )
    lmean_pea11 = bk17.convertAmps(IMT, lmean_pea11, ctx.rrup, ctx.mag)

    lmean_acr = copy.copy(lmean_ask14)
    lmean_scr = 1.0 * lmean_pea11
    lmean_target = 0.8 * lmean_acr + 0.2 * lmean_scr

    lmean, sd = test.get_mean_and_stddevs(
        sctx, rctx, dctx, IMT, [const.StdDev.TOTAL]
    )
    np.testing.assert_allclose(lmean_target, lmean[0])


def test_from_config_single_gmpe():
    # Mock up a minimal config dictionary
    conf = {
        "gmpe_modules": {
            "ASK14": [
                "AbrahamsonEtAl2014",
                "openquake.hazardlib.gsim.abrahamson_2014",
            ]
        },
        "gmpe_sets": {
            "stable_continental": {
                "gmpes": ["C03", "Pea11"],
                "weights": [0.5, 0.5],
                "weights_large_dist": [0, 1.0],
                "dist_cutoff": 500,
                "site_gmpes": ["ASK14"],
                "weights_site_gmpes": [],
            }
        },
        "gmpe_limits": {},
        "modeling": {
            "gmpe": "ASK14",
        },
        "interp": {"component": "RotD50"},
    }

    # Get multigmpe from config
    test = MultiGMPE.__from_config__(conf)

    # Compute "by hand"
    ASK14 = AbrahamsonEtAl2014()

    IMT = imt.SA(1.0)
    size = 100
    rctx = RuptureContext()
    dctx = DistancesContext()
    sctx = SitesContext()
    sctx_rock = SitesContext()
    sctx.sids = np.array(range(size))
    sctx_rock.sids = np.array(range(size))

    rctx.rake = 0.0
    rctx.dip = 90.0
    rctx.ztor = 0.0
    rctx.mag = 8.0
    rctx.width = 10.0
    rctx.hypo_depth = 8.0

    dctx.rjb = np.logspace(1, np.log10(800), size)
    dctx.rrup = dctx.rjb
    dctx.rhypo = dctx.rjb
    dctx.rx = dctx.rjb
    dctx.ry0 = dctx.rjb

    sctx.vs30 = np.ones_like(dctx.rjb) * 275.0
    sctx.vs30measured = np.full_like(dctx.rjb, False, dtype="bool")
    sctx_rock.vs30 = np.ones_like(dctx.rjb) * 760.0
    sctx_rock.vs30measured = np.full_like(dctx.rjb, False, dtype="bool")

    set_sites_depth_parameters(sctx, ASK14)

    ctx = stuff_context(sctx, rctx, dctx)
    lmean_ask14, dummy = ASK14.get_mean_and_stddevs(
        ctx, ctx, ctx, IMT, [const.StdDev.TOTAL]
    )

    lmean_target = lmean_ask14

    cx = stuff_context(sctx, rctx, dctx)
    lmean, sd = test.get_mean_and_stddevs(
        cx, cx, cx, IMT, [const.StdDev.TOTAL]
    )
    np.testing.assert_allclose(lmean_target, lmean[0])


def test_nga_w2_m8():
    # Test based on Gregor et al. (2014) Fig 2 (lower right)
    # This also tests
    #    - use of the multigmpe class with only a single GMPE
    #    - Some of the sites class depth methods.
    IMT = imt.SA(1.0)
    size = 100
    rctx = RuptureContext()
    dctx = DistancesContext()
    sctx = SitesContext()
    sctx.sids = np.array(range(size))

    rctx.rake = 0.0  # assumed for 'strike slip'
    rctx.dip = 90.0  # assumed for 'strike slip'
    rctx.ztor = 0.0  # given
    rctx.mag = 8.0  # given
    rctx.width = 10.0  # req by CB14 but not used for vertical rupture.
    rctx.hypo_depth = 8.0  # given

    dctx.rjb = np.logspace(0, np.log10(300), size)
    dctx.rrup = dctx.rjb  # b/c ztor = 0
    dctx.rx = dctx.rjb  # doesn't matter b/c vertical
    dctx.ry0 = dctx.rjb  # doesn't matter

    sctx.vs30 = np.ones_like(dctx.rjb) * 270.0
    gmpes = [BooreEtAl2014()]
    gmpe = MultiGMPE.__from_list__(
        gmpes, [1.0], imc="Average Horizontal (RotD50)"
    )
    # Set imc above to avoid component conversion for this test.

    cx = stuff_context(sctx, rctx, dctx)
    bea14, sd_bea14 = gmpe.get_mean_and_stddevs(
        cx, cx, cx, IMT, [const.StdDev.TOTAL]
    )

    gmpes = [ChiouYoungs2014()]
    gmpe = MultiGMPE.__from_list__(
        gmpes, [1.0], imc="Average Horizontal (RotD50)"
    )
    sctx.vs30measured = np.zeros_like(dctx.rjb, dtype=bool)
    sctx.z1pt0_cy14_cal = _z1pt0_from_vs30_cy14_cal(sctx.vs30)
    cx = stuff_context(sctx, rctx, dctx)
    cy14, sd_cy14 = gmpe.get_mean_and_stddevs(
        cx, cx, cx, IMT, [const.StdDev.TOTAL]
    )

    gmpes = [AbrahamsonEtAl2014()]
    gmpe = MultiGMPE.__from_list__(
        gmpes, [1.0], imc="Average Horizontal (RotD50)"
    )
    sctx.z1pt0_ask14_cal = _z1pt0_from_vs30_ask14_cal(sctx.vs30)
    cx = stuff_context(sctx, rctx, dctx)
    ask14, sd_ask14 = gmpe.get_mean_and_stddevs(
        cx, cx, cx, IMT, [const.StdDev.TOTAL]
    )

    gmpes = [CampbellBozorgnia2014()]
    gmpe = MultiGMPE.__from_list__(
        gmpes, [1.0], imc="Average Horizontal (RotD50)"
    )
    sctx.z2pt5_cb14_cal = _z2pt5_from_vs30_cb14_cal(sctx.vs30) / 1000.0
    #                                               Important ^^^^^^^
    cx = stuff_context(sctx, rctx, dctx)
    cb14, sd_cb14 = gmpe.get_mean_and_stddevs(
        cx, cx, cx, IMT, [const.StdDev.TOTAL]
    )

    bea14t = np.array(
        [
            -0.04706931,
            -0.04831454,
            -0.04970724,
            -0.05126427,
            -0.05300426,
            -0.05494776,
            -0.05711739,
            -0.05953799,
            -0.06223677,
            -0.06524346,
            -0.06859041,
            -0.07231272,
            -0.07644828,
            -0.08103783,
            -0.08612496,
            -0.091756,
            -0.0979799,
            -0.10484797,
            -0.11241359,
            -0.12073178,
            -0.12985861,
            -0.13985062,
            -0.150764,
            -0.16265376,
            -0.17557282,
            -0.18957098,
            -0.20469392,
            -0.22098224,
            -0.23847051,
            -0.25718644,
            -0.27715022,
            -0.298374,
            -0.32086166,
            -0.34460867,
            -0.36960233,
            -0.39582211,
            -0.42324023,
            -0.45182244,
            -0.48152884,
            -0.51231486,
            -0.54413223,
            -0.57692999,
            -0.61065545,
            -0.64525509,
            -0.68067533,
            -0.71686333,
            -0.75376751,
            -0.79133814,
            -0.82952771,
            -0.86829121,
            -0.90758642,
            -0.947374,
            -0.98761762,
            -1.02828395,
            -1.06934266,
            -1.11076641,
            -1.15253073,
            -1.19461394,
            -1.23699711,
            -1.2796639,
            -1.32260047,
            -1.36579541,
            -1.40923964,
            -1.45292632,
            -1.49685079,
            -1.54101051,
            -1.58540501,
            -1.63003588,
            -1.67490671,
            -1.72002312,
            -1.76539274,
            -1.81102525,
            -1.85693237,
            -1.90312795,
            -1.94962795,
            -1.99645054,
            -2.04361613,
            -2.09114744,
            -2.13906952,
            -2.18740984,
            -2.2361983,
            -2.28546726,
            -2.3352516,
            -2.38558862,
            -2.43651811,
            -2.48808225,
            -2.54032551,
            -2.59329459,
            -2.64703823,
            -2.7016071,
            -2.75705358,
            -2.81343154,
            -2.8707962,
            -2.92920388,
            -2.98871183,
            -3.04937811,
            -3.11126146,
            -3.17442127,
            -3.23891766,
            -3.30481158,
        ]
    )
    np.testing.assert_allclose(bea14[0], bea14t)

    sd_bea14t = np.array(
        [
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68842845,
            0.69448315,
            0.7005498,
            0.70662807,
            0.71271767,
            0.71881832,
            0.72492974,
            0.73105165,
            0.73718379,
            0.74332592,
            0.74947777,
            0.75563913,
            0.76180976,
            0.76798942,
            0.77417792,
            0.77523868,
            0.77523868,
        ]
    )
    np.testing.assert_allclose(sd_bea14[0], sd_bea14t)

    cy14t = np.array(
        [
            2.15950578e-01,
            2.11701050e-01,
            2.07210951e-01,
            2.02467361e-01,
            1.97456752e-01,
            1.92164967e-01,
            1.86577201e-01,
            1.80677985e-01,
            1.74451171e-01,
            1.67879917e-01,
            1.60946672e-01,
            1.53633172e-01,
            1.45920425e-01,
            1.37788712e-01,
            1.29217582e-01,
            1.20185857e-01,
            1.10671638e-01,
            1.00652317e-01,
            9.01045974e-02,
            7.90045179e-02,
            6.73274835e-02,
            5.50483071e-02,
            4.21412585e-02,
            2.85801238e-02,
            1.43382760e-02,
            -6.11242979e-04,
            -1.62956265e-02,
            -3.27421939e-02,
            -4.99782649e-02,
            -6.80310188e-02,
            -8.69273347e-02,
            -1.06693614e-01,
            -1.27355583e-01,
            -1.48938073e-01,
            -1.71464782e-01,
            -1.94958011e-01,
            -2.19438380e-01,
            -2.44924520e-01,
            -2.71432741e-01,
            -2.98976684e-01,
            -3.27566945e-01,
            -3.57210688e-01,
            -3.87911243e-01,
            -4.19667691e-01,
            -4.52474448e-01,
            -4.86320855e-01,
            -5.21190778e-01,
            -5.57062238e-01,
            -5.93907079e-01,
            -6.31690693e-01,
            -6.70371823e-01,
            -7.09902461e-01,
            -7.50227868e-01,
            -7.91286737e-01,
            -8.33011533e-01,
            -8.75329012e-01,
            -9.18160968e-01,
            -9.61425200e-01,
            -1.00503672e00,
            -1.04890917e00,
            -1.09295652e00,
            -1.13709486e00,
            -1.18124444e00,
            -1.22533173e00,
            -1.26929150e00,
            -1.31306890e00,
            -1.35662132e00,
            -1.39992008e00,
            -1.44295176e00,
            -1.48571927e00,
            -1.52824240e00,
            -1.57055804e00,
            -1.61271991e00,
            -1.65479802e00,
            -1.69687770e00,
            -1.73905841e00,
            -1.78145234e00,
            -1.82418297e00,
            -1.86738351e00,
            -1.91119546e00,
            -1.95576724e00,
            -2.00125293e00,
            -2.04781129e00,
            -2.09560490e00,
            -2.14479953e00,
            -2.19556372e00,
            -2.24806860e00,
            -2.30248784e00,
            -2.35899776e00,
            -2.41777766e00,
            -2.47901019e00,
            -2.54288188e00,
            -2.60958376e00,
            -2.67931198e00,
            -2.75226858e00,
            -2.82866226e00,
            -2.90870918e00,
            -2.99263379e00,
            -3.08066973e00,
            -3.17306066e00,
        ]
    )
    np.testing.assert_allclose(cy14[0], cy14t)

    sd_cy14t = np.array(
        [
            0.63353027,
            0.63356997,
            0.63361207,
            0.6336567,
            0.63370404,
            0.63375423,
            0.63380746,
            0.63386391,
            0.63392378,
            0.63398728,
            0.63405464,
            0.63412608,
            0.63420186,
            0.63428226,
            0.63436754,
            0.63445802,
            0.634554,
            0.63465584,
            0.63476388,
            0.63487852,
            0.63500014,
            0.63512918,
            0.63526608,
            0.63541133,
            0.63556541,
            0.63572887,
            0.63590226,
            0.63608615,
            0.63628116,
            0.63648794,
            0.63670715,
            0.63693947,
            0.63718564,
            0.6374464,
            0.6377225,
            0.63801473,
            0.63832389,
            0.63865076,
            0.63899615,
            0.63936084,
            0.63974562,
            0.64015122,
            0.64057833,
            0.6410276,
            0.64149959,
            0.64199478,
            0.64251353,
            0.64305607,
            0.64362247,
            0.64421264,
            0.64482631,
            0.64546296,
            0.6461219,
            0.64680216,
            0.64750256,
            0.64822168,
            0.64895788,
            0.6497093,
            0.65047392,
            0.65124957,
            0.65203397,
            0.65282481,
            0.6536198,
            0.65441669,
            0.65521338,
            0.65600795,
            0.65679873,
            0.65758432,
            0.65836364,
            0.65913594,
            0.65990083,
            0.66065826,
            0.66140849,
            0.66215212,
            0.66288997,
            0.66362311,
            0.66435277,
            0.66508034,
            0.66580723,
            0.66653492,
            0.66726483,
            0.66799835,
            0.6687367,
            0.66948098,
            0.67023209,
            0.67099071,
            0.67175726,
            0.67253188,
            0.67331443,
            0.67410444,
            0.67490111,
            0.67570333,
            0.67650962,
            0.6773182,
            0.67812693,
            0.6789334,
            0.67973489,
            0.68052845,
            0.68131093,
            0.682079,
        ]
    )
    np.testing.assert_allclose(sd_cy14[0], sd_cy14t)

    cb14t = np.array(
        [
            -0.12360143,
            -0.12492008,
            -0.12639386,
            -0.12804025,
            -0.12987851,
            -0.13192982,
            -0.13421738,
            -0.13676659,
            -0.13960515,
            -0.14276313,
            -0.14627311,
            -0.1501702,
            -0.15449207,
            -0.15927894,
            -0.16457348,
            -0.17042065,
            -0.17686754,
            -0.18396301,
            -0.19175733,
            -0.2003017,
            -0.20964765,
            -0.2198464,
            -0.2309481,
            -0.24300104,
            -0.25605077,
            -0.2701393,
            -0.2853042,
            -0.30157786,
            -0.31898682,
            -0.33755114,
            -0.35728408,
            -0.37819178,
            -0.40027329,
            -0.42352069,
            -0.44791937,
            -0.47344858,
            -0.50008196,
            -0.52778827,
            -0.55653218,
            -0.58627502,
            -0.61697558,
            -0.64859088,
            -0.68107684,
            -0.71438893,
            -0.74848274,
            -0.78331444,
            -0.81884117,
            -0.85502134,
            -0.89181493,
            -0.92918359,
            -0.96709082,
            -1.00550201,
            -1.04438448,
            -1.08370748,
            -1.12344214,
            -1.16356146,
            -1.2040402,
            -1.24485483,
            -1.28598346,
            -1.32740569,
            -1.36910259,
            -1.41105659,
            -1.45325136,
            -1.49567175,
            -1.53830371,
            -1.58113421,
            -1.62415113,
            -1.66734325,
            -1.71070013,
            -1.75421207,
            -1.79787006,
            -1.84166571,
            -1.88559121,
            -1.92963928,
            -1.97380313,
            -2.01807642,
            -2.06245324,
            -2.1086867,
            -2.15533167,
            -2.20229055,
            -2.24956958,
            -2.29717584,
            -2.3451173,
            -2.3934028,
            -2.44204209,
            -2.49104585,
            -2.54042571,
            -2.59019428,
            -2.64036519,
            -2.69095312,
            -2.74197385,
            -2.79344427,
            -2.84538247,
            -2.89780779,
            -2.95074084,
            -3.00420362,
            -3.05821954,
            -3.11281355,
            -3.16801217,
            -3.22384366,
        ]
    )
    np.testing.assert_allclose(cb14[0], cb14t)

    sd_cb14t = np.array(
        [
            0.68878528,
            0.68879916,
            0.68881471,
            0.68883212,
            0.68885159,
            0.68887337,
            0.68889772,
            0.68892493,
            0.68895533,
            0.68898927,
            0.68902715,
            0.68906938,
            0.68911644,
            0.68916883,
            0.68922711,
            0.68929189,
            0.68936379,
            0.68944351,
            0.68953179,
            0.68962941,
            0.68973718,
            0.68985596,
            0.68998663,
            0.69013009,
            0.69028726,
            0.69045903,
            0.69064631,
            0.69084996,
            0.69107078,
            0.6913095,
            0.69156678,
            0.69184316,
            0.69213904,
            0.6924547,
            0.69279025,
            0.69314562,
            0.69352058,
            0.69391472,
            0.69432743,
            0.69475796,
            0.69520538,
            0.69566861,
            0.69614644,
            0.69663756,
            0.69714056,
            0.69765397,
            0.69817626,
            0.6987059,
            0.69924134,
            0.69978105,
            0.70032354,
            0.70086736,
            0.70141112,
            0.70195351,
            0.70249328,
            0.70302928,
            0.70356044,
            0.70408578,
            0.70460441,
            0.70511554,
            0.70561843,
            0.70611247,
            0.7065971,
            0.70707186,
            0.70753634,
            0.70799022,
            0.70843322,
            0.70886514,
            0.70928584,
            0.70969519,
            0.71009316,
            0.71047972,
            0.7108549,
            0.71121875,
            0.71157136,
            0.71191284,
            0.71224333,
            0.71273208,
            0.71321494,
            0.71368103,
            0.71413017,
            0.71456219,
            0.71497699,
            0.71537447,
            0.7157546,
            0.71611737,
            0.71646279,
            0.71679093,
            0.71710189,
            0.71739579,
            0.71767282,
            0.71793317,
            0.7181771,
            0.71840489,
            0.71861688,
            0.71881343,
            0.71899496,
            0.71916192,
            0.7193148,
            0.71945414,
        ]
    )
    np.testing.assert_allclose(sd_cb14[0], sd_cb14t)

    ask14t = np.array(
        [
            -0.10458541,
            -0.10586773,
            -0.10729069,
            -0.10886911,
            -0.11061915,
            -0.11255842,
            -0.11470597,
            -0.11708237,
            -0.11970973,
            -0.1226117,
            -0.12581344,
            -0.12934155,
            -0.13322396,
            -0.1374898,
            -0.14216916,
            -0.14729289,
            -0.1528922,
            -0.15899838,
            -0.16564233,
            -0.17285411,
            -0.18066246,
            -0.18909429,
            -0.19817414,
            -0.20792375,
            -0.21836157,
            -0.2295024,
            -0.24135709,
            -0.25393236,
            -0.26723068,
            -0.28125029,
            -0.29598538,
            -0.3114263,
            -0.32755987,
            -0.34436986,
            -0.36183737,
            -0.37994139,
            -0.39865927,
            -0.41796727,
            -0.437841,
            -0.45825591,
            -0.47918768,
            -0.5006126,
            -0.52250784,
            -0.54485174,
            -0.56762402,
            -0.5908059,
            -0.61438025,
            -0.63833168,
            -0.66264654,
            -0.68731302,
            -0.71232107,
            -0.73766247,
            -0.76333072,
            -0.7893211,
            -0.81563057,
            -0.84225777,
            -0.86920294,
            -0.89646795,
            -0.92405621,
            -0.95197268,
            -0.98022381,
            -1.00881759,
            -1.03776346,
            -1.06707238,
            -1.0967568,
            -1.12683067,
            -1.15730945,
            -1.18821019,
            -1.2195515,
            -1.25135362,
            -1.28363846,
            -1.31642969,
            -1.34975275,
            -1.38363495,
            -1.41810555,
            -1.45319584,
            -1.48893923,
            -1.52537137,
            -1.56253025,
            -1.6004563,
            -1.63919256,
            -1.67878479,
            -1.71928162,
            -1.7607347,
            -1.80319892,
            -1.8467325,
            -1.89139726,
            -1.93725878,
            -1.98438664,
            -2.03285463,
            -2.08274098,
            -2.13412865,
            -2.18710561,
            -2.24176507,
            -2.29820584,
            -2.35653263,
            -2.41685641,
            -2.47929475,
            -2.54397222,
            -2.6110208,
        ]
    )
    np.testing.assert_allclose(ask14[0], ask14t)

    sd_ask14t = np.array(
        [
            0.67522874,
            0.67528398,
            0.67534522,
            0.67541308,
            0.67548824,
            0.67557142,
            0.67566341,
            0.67576505,
            0.67587724,
            0.67600093,
            0.67613711,
            0.67628684,
            0.67645119,
            0.67663129,
            0.67682824,
            0.67704318,
            0.67727722,
            0.67753144,
            0.67780683,
            0.67810435,
            0.67842481,
            0.67876892,
            0.67913722,
            0.67953009,
            0.67994772,
            0.68039009,
            0.68085697,
            0.68134792,
            0.68186228,
            0.68239919,
            0.68295762,
            0.68353634,
            0.68413399,
            0.68474911,
            0.68538011,
            0.68602537,
            0.68668322,
            0.68735199,
            0.68803002,
            0.68871567,
            0.68940739,
            0.69010368,
            0.6908031,
            0.69150434,
            0.69220616,
            0.69290742,
            0.69360708,
            0.6943042,
            0.69499793,
            0.69568751,
            0.69637228,
            0.69705164,
            0.69772509,
            0.69839219,
            0.69905255,
            0.69970586,
            0.70035187,
            0.70099036,
            0.70162116,
            0.70224414,
            0.70285921,
            0.70346631,
            0.7040654,
            0.70465646,
            0.70523952,
            0.7058146,
            0.70638173,
            0.70694097,
            0.70749239,
            0.70803606,
            0.70857205,
            0.70910044,
            0.70962132,
            0.71013478,
            0.71064088,
            0.71113971,
            0.71163135,
            0.71211586,
            0.7125933,
            0.71306372,
            0.71352717,
            0.71398367,
            0.71443325,
            0.71487591,
            0.71531164,
            0.71574041,
            0.71616218,
            0.71657691,
            0.7169845,
            0.71738486,
            0.71777789,
            0.71816344,
            0.71854137,
            0.7189115,
            0.71927364,
            0.71962759,
            0.71997312,
            0.72030998,
            0.72063793,
            0.72095669,
        ]
    )
    np.testing.assert_allclose(sd_ask14[0], sd_ask14t)


def test_nga_w2_m6():
    # Test based on Gregor et al. (2014) Fig 2 (upper right)
    # This also tests
    #    - use of the multigmpe class with only a single GMPE
    #    - Some of the sites class depth methods.
    IMT = imt.SA(1.0)
    size = 100
    rctx = RuptureContext()
    dctx = DistancesContext()
    sctx = SitesContext()
    sctx.sids = np.array(range(size))

    rctx.rake = 0.0  # assumed for 'strike slip'
    rctx.dip = 90.0  # assumed for 'strike slip'
    rctx.ztor = 3.0  # given
    rctx.mag = 6.0  # given
    rctx.width = 10.0  # req by CB14 but not used for vertical rupture.
    rctx.hypo_depth = 8.0  # given

    dctx.rjb = np.logspace(0, np.log10(300), size)
    dctx.rrup = np.sqrt(dctx.rjb**2 + rctx.ztor**2)  # ztor = 3.0
    dctx.rx = dctx.rjb  # doesn't matter b/c vertical
    dctx.ry0 = dctx.rjb  # doesn't matter

    sctx.vs30 = np.ones_like(dctx.rjb) * 270.0
    gmpes = [BooreEtAl2014()]
    gmpe = MultiGMPE.__from_list__(
        gmpes, [1.0], imc="Average Horizontal (RotD50)"
    )
    # Set imc above to avoid component conversion for this test.

    cx = stuff_context(sctx, rctx, dctx)
    bea14, sd_bea14 = gmpe.get_mean_and_stddevs(
        cx, cx, cx, IMT, [const.StdDev.TOTAL]
    )

    gmpes = [ChiouYoungs2014()]
    gmpe = MultiGMPE.__from_list__(
        gmpes, [1.0], imc="Average Horizontal (RotD50)"
    )
    sctx.vs30measured = np.zeros_like(dctx.rjb, dtype=bool)
    sctx.z1pt0_cy14_cal = _z1pt0_from_vs30_cy14_cal(sctx.vs30)
    cx = stuff_context(sctx, rctx, dctx)
    cy14, sd_cy14 = gmpe.get_mean_and_stddevs(
        cx, cx, cx, IMT, [const.StdDev.TOTAL]
    )

    gmpes = [AbrahamsonEtAl2014()]
    gmpe = MultiGMPE.__from_list__(
        gmpes, [1.0], imc="Average Horizontal (RotD50)"
    )
    sctx.z1pt0_ask14_cal = _z1pt0_from_vs30_ask14_cal(sctx.vs30)
    cx = stuff_context(sctx, rctx, dctx)
    ask14, sd_ask14 = gmpe.get_mean_and_stddevs(
        cx, cx, cx, IMT, [const.StdDev.TOTAL]
    )

    gmpes = [CampbellBozorgnia2014()]
    gmpe = MultiGMPE.__from_list__(
        gmpes, [1.0], imc="Average Horizontal (RotD50)"
    )
    sctx.z2pt5_cb14_cal = _z2pt5_from_vs30_cb14_cal(sctx.vs30) / 1000.0
    #                                               Important ^^^^^^^
    cx = stuff_context(sctx, rctx, dctx)
    cb14, sd_cb14 = gmpe.get_mean_and_stddevs(
        cx, cx, cx, IMT, [const.StdDev.TOTAL]
    )

    bea14t = np.array(
        [
            -0.99215164,
            -0.99358257,
            -0.99518353,
            -0.99697407,
            -0.99897586,
            -1.00121282,
            -1.00371135,
            -1.00650047,
            -1.00961208,
            -1.01308105,
            -1.01694549,
            -1.0212468,
            -1.02602988,
            -1.03134311,
            -1.03723847,
            -1.0437714,
            -1.05100074,
            -1.05898846,
            -1.06779935,
            -1.07750052,
            -1.08816083,
            -1.09985013,
            -1.11263838,
            -1.12659469,
            -1.14178612,
            -1.15827658,
            -1.17612556,
            -1.19538689,
            -1.21610764,
            -1.23832697,
            -1.26207536,
            -1.28737384,
            -1.31423364,
            -1.34265598,
            -1.37263225,
            -1.40414436,
            -1.43716539,
            -1.47166043,
            -1.50758761,
            -1.54489915,
            -1.58354263,
            -1.62346207,
            -1.66459915,
            -1.7068943,
            -1.7502876,
            -1.79471977,
            -1.84013281,
            -1.8864707,
            -1.93367986,
            -1.98170954,
            -2.03051209,
            -2.08004314,
            -2.1302617,
            -2.18113022,
            -2.23261453,
            -2.28468378,
            -2.33731038,
            -2.39046984,
            -2.44414063,
            -2.49830409,
            -2.5529442,
            -2.60804751,
            -2.66360294,
            -2.71960165,
            -2.77603693,
            -2.83290407,
            -2.89020023,
            -2.94792435,
            -3.00607707,
            -3.06466062,
            -3.12367877,
            -3.18313677,
            -3.24304129,
            -3.30340037,
            -3.3642234,
            -3.4255211,
            -3.48730547,
            -3.54958983,
            -3.61238877,
            -3.67571819,
            -3.73959529,
            -3.80403863,
            -3.8690681,
            -3.93470502,
            -4.00097215,
            -4.06789374,
            -4.13549564,
            -4.20380532,
            -4.27285199,
            -4.3426667,
            -4.41328241,
            -4.48473417,
            -4.55705921,
            -4.63029712,
            -4.70448998,
            -4.77968258,
            -4.85592257,
            -4.9332607,
            -5.01175106,
            -5.09145125,
        ]
    )
    np.testing.assert_allclose(bea14[0], bea14t)

    sd_bea14t = np.array(
        [
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68580367,
            0.68842845,
            0.69448315,
            0.7005498,
            0.70662807,
            0.71271767,
            0.71881832,
            0.72492974,
            0.73105165,
            0.73718379,
            0.74332592,
            0.74947777,
            0.75563913,
            0.76180976,
            0.76798942,
            0.77417792,
            0.77523868,
            0.77523868,
        ]
    )
    np.testing.assert_allclose(sd_bea14[0], sd_bea14t)

    cy14t = np.array(
        [
            -0.62341445,
            -0.62591331,
            -0.62869575,
            -0.63179136,
            -0.63523223,
            -0.63905308,
            -0.64329125,
            -0.64798683,
            -0.6531826,
            -0.658924,
            -0.66525909,
            -0.67223836,
            -0.67991462,
            -0.6883427,
            -0.69757923,
            -0.70768225,
            -0.7187109,
            -0.73072494,
            -0.74378439,
            -0.75794903,
            -0.77327798,
            -0.78982924,
            -0.80765927,
            -0.8268226,
            -0.84737144,
            -0.86935539,
            -0.89282113,
            -0.91781216,
            -0.9443686,
            -0.97252699,
            -1.00232014,
            -1.03377694,
            -1.06692226,
            -1.10177678,
            -1.13835683,
            -1.17667424,
            -1.21673616,
            -1.25854482,
            -1.30209733,
            -1.34738544,
            -1.39439521,
            -1.44310676,
            -1.49349394,
            -1.54552401,
            -1.59915729,
            -1.65434687,
            -1.71103832,
            -1.76916942,
            -1.82866995,
            -1.88946159,
            -1.95145789,
            -2.01456437,
            -2.07867876,
            -2.14369146,
            -2.20948615,
            -2.27594064,
            -2.34292798,
            -2.41031783,
            -2.47797801,
            -2.54577638,
            -2.6135829,
            -2.68127186,
            -2.74872423,
            -2.81583014,
            -2.88249118,
            -2.94862278,
            -3.01415622,
            -3.07904047,
            -3.14324358,
            -3.20675373,
            -3.26957973,
            -3.33175109,
            -3.39331769,
            -3.45434887,
            -3.51493237,
            -3.5751728,
            -3.63518999,
            -3.6951173,
            -3.75509973,
            -3.81529228,
            -3.87585827,
            -3.9369679,
            -3.998797,
            -4.06152604,
            -4.12533926,
            -4.19042418,
            -4.25697122,
            -4.3251736,
            -4.39522736,
            -4.4673316,
            -4.54168889,
            -4.61850569,
            -4.69799303,
            -4.78036716,
            -4.86585036,
            -4.95467175,
            -5.04706819,
            -5.14328524,
            -5.24357814,
            -5.34821283,
        ]
    )
    np.testing.assert_allclose(cy14[0], cy14t)

    sd_cy14t = np.array(
        [
            0.67962936,
            0.67967162,
            0.67971873,
            0.6797712,
            0.6798296,
            0.67989455,
            0.6799667,
            0.68004679,
            0.68013558,
            0.68023391,
            0.68034266,
            0.68046278,
            0.68059527,
            0.68074118,
            0.68090161,
            0.68107772,
            0.68127071,
            0.68148181,
            0.68171228,
            0.68196344,
            0.68223658,
            0.68253304,
            0.68285414,
            0.68320122,
            0.68357557,
            0.68397849,
            0.68441121,
            0.68487494,
            0.68537079,
            0.68589981,
            0.68646296,
            0.68706105,
            0.68769477,
            0.68836466,
            0.68907105,
            0.68981407,
            0.6905936,
            0.69140926,
            0.69226038,
            0.69314596,
            0.69406467,
            0.69501481,
            0.69599432,
            0.69700075,
            0.69803129,
            0.69908275,
            0.7001516,
            0.70123401,
            0.70232588,
            0.70342289,
            0.70452057,
            0.7056144,
            0.70669983,
            0.70777241,
            0.70882783,
            0.70986206,
            0.71087135,
            0.71185234,
            0.71280209,
            0.71371814,
            0.71459853,
            0.71544178,
            0.71624694,
            0.71701352,
            0.71774152,
            0.71843134,
            0.71908374,
            0.71969984,
            0.720281,
            0.72082881,
            0.72134502,
            0.72183147,
            0.72229009,
            0.72272281,
            0.72313156,
            0.7235182,
            0.72388451,
            0.72423221,
            0.72456287,
            0.72487794,
            0.72517875,
            0.72546651,
            0.72574226,
            0.72600694,
            0.72626134,
            0.72650614,
            0.72674191,
            0.72696911,
            0.7271881,
            0.72739915,
            0.72760247,
            0.72779818,
            0.72798636,
            0.72816703,
            0.72834017,
            0.72850573,
            0.72866367,
            0.72881389,
            0.72895634,
            0.72909092,
        ]
    )
    np.testing.assert_allclose(sd_cy14[0], sd_cy14t)

    cb14t = np.array(
        [
            -0.84598857,
            -0.84745579,
            -0.84909717,
            -0.85093272,
            -0.85298457,
            -0.85527719,
            -0.85783754,
            -0.86069532,
            -0.8638831,
            -0.86743656,
            -0.87139468,
            -0.87579984,
            -0.88069805,
            -0.88613897,
            -0.89217601,
            -0.89886635,
            -0.9062708,
            -0.91445373,
            -0.92348272,
            -0.93342827,
            -0.94436328,
            -0.95636242,
            -0.96950138,
            -0.98385602,
            -0.99950136,
            -1.01651045,
            -1.03495328,
            -1.0548955,
            -1.07639727,
            -1.09951211,
            -1.12428581,
            -1.15075558,
            -1.17894929,
            -1.20888498,
            -1.24057056,
            -1.27400384,
            -1.3091727,
            -1.34605552,
            -1.38462184,
            -1.42483314,
            -1.46664375,
            -1.51000182,
            -1.55485039,
            -1.60112839,
            -1.64877166,
            -1.69771392,
            -1.74788765,
            -1.79922487,
            -1.85165792,
            -1.90512001,
            -1.9595458,
            -2.01487181,
            -2.07103677,
            -2.1279819,
            -2.18565109,
            -2.24399108,
            -2.30295146,
            -2.36248478,
            -2.42254647,
            -2.48309484,
            -2.54409102,
            -2.6054988,
            -2.66728459,
            -2.72941728,
            -2.79186808,
            -2.85461046,
            -2.91761992,
            -2.98087395,
            -3.04435185,
            -3.1080346,
            -3.17190478,
            -3.23594639,
            -3.30014479,
            -3.36448659,
            -3.42895953,
            -3.49355239,
            -3.55825492,
            -3.62553715,
            -3.69322142,
            -3.76119243,
            -3.82945197,
            -3.89800314,
            -3.96685036,
            -4.03599932,
            -4.10545703,
            -4.17523175,
            -4.24533307,
            -4.31577186,
            -4.38656032,
            -4.45771201,
            -4.52924185,
            -4.60116618,
            -4.67350278,
            -4.74627095,
            -4.81949155,
            -4.89318703,
            -4.96738154,
            -5.04210099,
            -5.11737312,
            -5.19322758,
        ]
    )
    np.testing.assert_allclose(cb14[0], cb14t)

    sd_cb14t = np.array(
        [
            0.69353026,
            0.69355075,
            0.69357368,
            0.69359935,
            0.69362808,
            0.69366021,
            0.69369614,
            0.6937363,
            0.69378116,
            0.69383126,
            0.69388716,
            0.69394951,
            0.694019,
            0.69409637,
            0.69418244,
            0.69427811,
            0.69438433,
            0.6945021,
            0.69463252,
            0.69477673,
            0.69493592,
            0.69511134,
            0.69530426,
            0.69551597,
            0.69574776,
            0.69600088,
            0.69627654,
            0.69657586,
            0.69689983,
            0.69724928,
            0.69762484,
            0.69802692,
            0.69845563,
            0.69891081,
            0.69939192,
            0.69989812,
            0.70042818,
            0.70098053,
            0.70155325,
            0.70214411,
            0.7027506,
            0.70337001,
            0.70399942,
            0.70463583,
            0.70527617,
            0.70591738,
            0.7065565,
            0.70719067,
            0.7078172,
            0.70843361,
            0.70903768,
            0.7096274,
            0.71020108,
            0.71075727,
            0.71129478,
            0.7118127,
            0.71231035,
            0.71278727,
            0.71324322,
            0.71367814,
            0.71409212,
            0.71448541,
            0.71485837,
            0.71521146,
            0.71554522,
            0.71586027,
            0.71615726,
            0.7164369,
            0.7166999,
            0.716947,
            0.71717895,
            0.71739649,
            0.71760034,
            0.71779124,
            0.71796988,
            0.71813695,
            0.71829311,
            0.71848606,
            0.71866662,
            0.71883325,
            0.71898679,
            0.71912804,
            0.71925777,
            0.71937672,
            0.7194856,
            0.71958507,
            0.71967577,
            0.71975831,
            0.71983325,
            0.71990114,
            0.7199625,
            0.72001781,
            0.72006753,
            0.7201121,
            0.72015193,
            0.7201874,
            0.72021888,
            0.72024672,
            0.72027123,
            0.72029272,
        ]
    )
    np.testing.assert_allclose(sd_cb14[0], sd_cb14t)

    ask14t = np.array(
        [
            -1.0441888,
            -1.04615637,
            -1.04835492,
            -1.05081037,
            -1.05355121,
            -1.05660877,
            -1.06001735,
            -1.0638144,
            -1.06804073,
            -1.07274059,
            -1.0779618,
            -1.08375583,
            -1.09017778,
            -1.09728633,
            -1.10514357,
            -1.11381481,
            -1.12336817,
            -1.13387415,
            -1.145405,
            -1.158034,
            -1.17183459,
            -1.18687938,
            -1.20323906,
            -1.2209812,
            -1.24016904,
            -1.26086026,
            -1.28310578,
            -1.30694867,
            -1.33242318,
            -1.35955399,
            -1.38835567,
            -1.4188324,
            -1.45097797,
            -1.48477604,
            -1.52020069,
            -1.55721714,
            -1.59578275,
            -1.63584805,
            -1.67735799,
            -1.72025312,
            -1.76447086,
            -1.80994663,
            -1.85661504,
            -1.90441079,
            -1.95326964,
            -2.00312914,
            -2.05392925,
            -2.10561284,
            -2.15812612,
            -2.21141887,
            -2.26544466,
            -2.32016094,
            -2.3755291,
            -2.43151444,
            -2.48808612,
            -2.54521708,
            -2.60288392,
            -2.66106677,
            -2.71974919,
            -2.77891797,
            -2.83856308,
            -2.89867747,
            -2.95925698,
            -3.02030024,
            -3.08180855,
            -3.14378578,
            -3.20623833,
            -3.26917505,
            -3.33260718,
            -3.39654833,
            -3.46101447,
            -3.52602387,
            -3.59159717,
            -3.65775735,
            -3.72452978,
            -3.79194222,
            -3.86002496,
            -3.92881079,
            -3.99833513,
            -4.0686361,
            -4.13975464,
            -4.21173458,
            -4.28462283,
            -4.35846944,
            -4.43332781,
            -4.50925482,
            -4.58631101,
            -4.6645608,
            -4.74407263,
            -4.82491923,
            -4.90717782,
            -4.9909304,
            -5.07626396,
            -5.16327081,
            -5.25204885,
            -5.34270191,
            -5.43534007,
            -5.53008004,
            -5.62704554,
            -5.7263677,
        ]
    )
    np.testing.assert_allclose(ask14[0], ask14t)

    sd_ask14t = np.array(
        [
            0.73140801,
            0.73145093,
            0.73149881,
            0.73155216,
            0.73161158,
            0.73167769,
            0.73175118,
            0.73183278,
            0.73192328,
            0.73202352,
            0.73213439,
            0.73225681,
            0.73239176,
            0.73254024,
            0.73270325,
            0.73288181,
            0.73307693,
            0.73328958,
            0.73352066,
            0.73377101,
            0.73404132,
            0.73433217,
            0.73464396,
            0.7349769,
            0.73533095,
            0.73570585,
            0.73610107,
            0.7365158,
            0.73694898,
            0.73739927,
            0.73786509,
            0.73834465,
            0.73883597,
            0.73933692,
            0.73984528,
            0.74035877,
            0.74087509,
            0.74139201,
            0.74190734,
            0.74241901,
            0.74292511,
            0.74342388,
            0.74391373,
            0.74439327,
            0.7448613,
            0.74531681,
            0.74575899,
            0.74618717,
            0.74660087,
            0.74699976,
            0.74738364,
            0.74775243,
            0.74810616,
            0.74844495,
            0.74876899,
            0.74907856,
            0.74937396,
            0.74965557,
            0.74992377,
            0.750179,
            0.75042168,
            0.75065228,
            0.75087126,
            0.75107907,
            0.75127617,
            0.75146304,
            0.7516401,
            0.75180781,
            0.7519666,
            0.75211688,
            0.75225905,
            0.75239351,
            0.75252062,
            0.75264076,
            0.75275427,
            0.75286147,
            0.75296269,
            0.75305823,
            0.75314838,
            0.75323341,
            0.75331358,
            0.75338914,
            0.75346033,
            0.75352737,
            0.75359048,
            0.75364985,
            0.75370569,
            0.75375816,
            0.75380745,
            0.75385371,
            0.7538971,
            0.75393777,
            0.75397585,
            0.75401148,
            0.75404478,
            0.75407587,
            0.75410486,
            0.75413186,
            0.75415697,
            0.75418029,
        ]
    )
    np.testing.assert_allclose(sd_ask14[0], sd_ask14t)


def test_multigmpe_has_site():
    gmpes = [AtkinsonBoore2006(), Campbell2003()]
    wts = [0.6, 0.4]

    mgmpe = MultiGMPE.__from_list__(gmpes, wts)
    assert mgmpe.HAS_SITE == [True, False]


def test_multigmpe_get_sites_depth_parameters():
    # --------------------------------------------------------------------------
    # This is to check the older (2008) parameters that aren't getting tested
    # --------------------------------------------------------------------------
    gmpes = [CampbellBozorgnia2008(), ChiouYoungs2008()]

    # --------------------------------------------------------------------------
    # Make sites instance
    # --------------------------------------------------------------------------
    vs30file = os.path.join(homedir, "multigmpe_data", "Vs30_test.grd")
    cx = -118.2
    cy = 34.1
    dx = 0.0083
    dy = 0.0083
    xspan = 0.0083 * 5
    yspan = 0.0083 * 5
    site = sites.Sites.fromCenter(
        cx,
        cy,
        xspan,
        yspan,
        dx,
        dy,
        vs30File=vs30file,
        padding=True,
        resample=False,
    )
    sctx = site.getSitesContext()
    set_sites_depth_parameters(sctx, gmpes[0])
    z2pt5d = np.array(
        [
            [
                1177.61979893,
                1300.11396989,
                1168.13802718,
                1168.56933015,
                1169.4040603,
                1161.16046639,
                1148.4288528,
            ],
            [
                1179.50520975,
                1182.18094855,
                1170.95306363,
                1180.09841078,
                1198.16386197,
                1190.96074128,
                1179.30654372,
            ],
            [
                1171.26425658,
                1163.19305376,
                1166.20946607,
                1179.80411634,
                1251.35517419,
                1371.15661506,
                1417.9366787,
            ],
            [
                1152.40018562,
                1144.48233838,
                1154.16847239,
                1315.25665576,
                1209.20960179,
                1198.96368474,
                1179.3852516,
            ],
            [
                1526.52660116,
                1278.13354004,
                1360.38452132,
                1236.76774567,
                1170.91431583,
                1176.11487052,
                1176.57216955,
            ],
            [
                1556.3982478,
                1516.78437627,
                1180.52195107,
                1154.8017606,
                1165.96397227,
                1172.97688837,
                1176.12602836,
            ],
            [
                1575.22288791,
                1329.69579201,
                1162.02041292,
                1155.01082322,
                1165.80081172,
                1174.83307617,
                1180.5495586,
            ],
        ]
    )
    np.testing.assert_allclose(sctx.z2pt5, z2pt5d, atol=1e-2)
    set_sites_depth_parameters(sctx, gmpes[1])
    z1pt0d = np.array(
        [
            [
                183.2043947,
                217.27787758,
                180.56690603,
                180.68687904,
                180.91907101,
                178.625999,
                175.08452094,
            ],
            [
                183.72884833,
                184.47314285,
                181.34994816,
                183.89385557,
                188.91901585,
                186.91536614,
                183.67358657,
            ],
            [
                181.43651087,
                179.19139187,
                180.03044953,
                183.81199342,
                203.71493023,
                237.03939223,
                250.05192732,
            ],
            [
                176.18920323,
                173.98674225,
                176.68107716,
                221.49002942,
                191.99154431,
                189.14149784,
                183.69548028,
            ],
            [
                280.25774719,
                211.16371072,
                234.04298229,
                199.65723106,
                181.33916991,
                182.78577761,
                182.91298179,
            ],
            [
                288.5669674,
                277.54780981,
                184.01166928,
                176.85723522,
                179.96216197,
                181.91290358,
                182.78888133,
            ],
            [
                293.80330679,
                225.506479,
                178.86520526,
                176.91538893,
                179.91677656,
                182.42922842,
                184.01934871,
            ],
        ]
    )
    np.testing.assert_allclose(sctx.z1pt0, z1pt0d, atol=1e-2)


def test_multigmpe_get_mean_stddevs():
    # -------------------------------------------------------------------------
    # Define gmpes and their weights
    # -------------------------------------------------------------------------
    gmpes = [
        AbrahamsonEtAl2014(),
        BooreEtAl2014(),
        CampbellBozorgnia2014(),
        ChiouYoungs2014(),
    ]
    wts = [0.25, 0.25, 0.25, 0.25]

    # -------------------------------------------------------------------------
    # Make sites instance
    # -------------------------------------------------------------------------
    vs30file = os.path.join(homedir, "multigmpe_data", "Vs30_test.grd")
    cx = -118.2
    cy = 34.1
    dx = 0.0083
    dy = 0.0083
    xspan = 0.0083 * 5
    yspan = 0.0083 * 5
    site = sites.Sites.fromCenter(
        cx,
        cy,
        xspan,
        yspan,
        dx,
        dy,
        vs30File=vs30file,
        padding=True,
        resample=False,
    )
    sctx = site.getSitesContext()

    # --------------------------------------------------------------------------
    # Make rupture instance
    # --------------------------------------------------------------------------
    lat0 = np.array([34.1])
    lon0 = np.array([-118.2])
    lat1 = np.array([34.2])
    lon1 = np.array([-118.15])
    z = np.array([1.0])
    W = np.array([3.0])
    dip = np.array([30.0])

    event = {
        "lat": 34.1,
        "lon": -118.2,
        "depth": 1.0,
        "mag": 6.0,
        "id": "",
        "locstring": "",
        "rake": 30.3,
        "time": datetime.datetime.fromtimestamp(time.time(), datetime.UTC),
        "netid": "",
        "network": "",
    }
    origin = Origin(event)
    rup = QuadRupture.fromTrace(lon0, lat0, lon1, lat1, z, W, dip, origin)

    # --------------------------------------------------------------------------
    # Make a rupture context
    # --------------------------------------------------------------------------
    rx = rup.getRuptureContext(gmpes)

    # --------------------------------------------------------------------------
    # Make a distance context
    # --------------------------------------------------------------------------
    dctx = Distance.fromSites(gmpes, site, rup).getDistanceContext()

    shapes = []
    for k, v in sctx.__dict__.items():
        if k.startswith("__"):
            continue
        if k == "_slots_":
            continue
        if (k != "lons") and (k != "lats"):
            shapes.append(v.shape)
            sctx.__dict__[k] = np.reshape(sctx.__dict__[k], (-1,))
    for k, v in dctx.__dict__.items():
        if k.startswith("__"):
            continue
        if k == "_slots_":
            continue
        shapes.append(v.shape)
        dctx.__dict__[k] = np.reshape(dctx.__dict__[k], (-1,))
    shapeset = set(shapes)
    if len(shapeset) != 1:
        raise Exception("All dists and sites elements must have same shape.")
    else:
        orig_shape = list(shapeset)[0]

    # --------------------------------------------------------------------------
    # Compute weighted GMPE
    # --------------------------------------------------------------------------
    iimt = imt.PGV()
    stddev_types = [const.StdDev.TOTAL]
    mgmpe = MultiGMPE.__from_list__(gmpes, wts)
    ctx = stuff_context(sctx, rx, dctx)
    lnmu, lnsd = mgmpe.get_mean_and_stddevs(ctx, ctx, ctx, iimt, stddev_types)

    lnmud = np.array(
        [
            [
                3.59539686,
                3.7081893,
                3.73286788,
                3.78790331,
                3.82294539,
                3.86208006,
                3.86485444,
            ],
            [
                3.63362187,
                3.70523546,
                3.76307053,
                3.81236243,
                3.85884022,
                3.87708871,
                3.87363109,
            ],
            [
                3.66714334,
                3.7312258,
                3.78715775,
                3.8263537,
                3.89057658,
                3.92954219,
                3.93554182,
            ],
            [
                3.67849601,
                3.74501608,
                3.8009842,
                3.8940762,
                3.88294242,
                3.87998622,
                3.86291218,
            ],
            [
                3.77274389,
                3.76610057,
                3.83532648,
                3.84898303,
                3.85213729,
                3.86208438,
                3.85244256,
            ],
            [
                3.73608007,
                3.77733193,
                3.7165333,
                3.7566158,
                3.78705836,
                3.80706509,
                3.80721106,
            ],
            [
                3.67516071,
                3.64519877,
                3.63887338,
                3.67040334,
                3.70229907,
                3.72571416,
                3.72970474,
            ],
        ]
    )

    lnsdd = np.array(
        [
            [
                0.59855488,
                0.59764991,
                0.5984806,
                0.59842238,
                0.59837916,
                0.59841832,
                0.59851621,
            ],
            [
                0.59851021,
                0.5984284,
                0.59843465,
                0.59832939,
                0.59818647,
                0.59824473,
                0.59834046,
            ],
            [
                0.59852507,
                0.59850983,
                0.59843657,
                0.59831508,
                0.59783908,
                0.59578413,
                0.59455052,
            ],
            [
                0.59861813,
                0.59860025,
                0.59849002,
                0.59710638,
                0.59812893,
                0.59821826,
                0.59836214,
            ],
            [
                0.59230603,
                0.59778446,
                0.5962753,
                0.59797146,
                0.59839202,
                0.59837343,
                0.59839012,
            ],
            [
                0.59144929,
                0.5925885,
                0.5984268,
                0.59855357,
                0.59848017,
                0.59843716,
                0.59842358,
            ],
            [
                0.59099891,
                0.59717933,
                0.59860769,
                0.59862927,
                0.59855412,
                0.59849285,
                0.59845718,
            ],
        ]
    )

    RTOL = 0.03
    ATOL = 0.006
    np.testing.assert_allclose(
        lnmu[0].reshape(orig_shape), lnmud, rtol=RTOL, atol=ATOL
    )
    if TEST:
        np.testing.assert_allclose(
            lnsd[0].reshape(orig_shape), lnsdd, rtol=RTOL, atol=ATOL
        )
    else:
        print(repr(lnsd[0]))

    # --------------------------------------------------------------------------
    # Check PGV from a GMPE without PGV
    # --------------------------------------------------------------------------
    gmpes = [Campbell2003()]
    stddev_types = [const.StdDev.TOTAL]
    wts = [1.0]
    mgmpe = MultiGMPE.__from_list__(gmpes, wts)
    cx = stuff_context(sctx, rx, dctx)
    lnmu, lnsd = mgmpe.get_mean_and_stddevs(cx, cx, cx, iimt, stddev_types)

    lnmud = np.array(
        [
            3.41107672,
            3.4896988,
            3.54780071,
            3.60530335,
            3.64439344,
            3.64380775,
            3.61001833,
            3.44721415,
            3.51636198,
            3.57816476,
            3.62897994,
            3.65213276,
            3.63005608,
            3.59447843,
            3.48177157,
            3.54748178,
            3.60519181,
            3.64512766,
            3.64942781,
            3.62388355,
            3.5919053,
            3.49779548,
            3.56677301,
            3.62402696,
            3.65943918,
            3.63132068,
            3.59581703,
            3.55919348,
            3.50567131,
            3.55275522,
            3.60700042,
            3.61923635,
            3.60103343,
            3.57485211,
            3.54113532,
            3.46166954,
            3.5126093,
            3.52805688,
            3.54069436,
            3.53953658,
            3.52821949,
            3.50799672,
            3.39651978,
            3.42274739,
            3.4423038,
            3.45547966,
            3.46162532,
            3.45989677,
            3.45035028,
        ]
    )
    lnsdd = np.array(
        [
            [
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
            ],
            [
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
            ],
            [
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
            ],
            [
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
            ],
            [
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
            ],
            [
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
            ],
            [
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
                0.58990483,
            ],
        ]
    )

    np.testing.assert_allclose(lnmu[0], lnmud, atol=1e-2)
    if TEST:
        np.testing.assert_allclose(lnsd[0].reshape(orig_shape), lnsdd)
    else:
        print(repr(lnsd[0]))

    # --------------------------------------------------------------------------
    # Check a GMPE that doens't have PGV but does have site
    # --------------------------------------------------------------------------
    gmpes = [ZhaoEtAl2006Asc()]
    stddev_types = [
        const.StdDev.TOTAL,
        const.StdDev.INTER_EVENT,
        const.StdDev.INTRA_EVENT,
    ]
    wts = [1.0]
    mgmpe = MultiGMPE.__from_list__(gmpes, wts)
    cx = stuff_context(sctx, rx, dctx)
    lnmu, lnsd = mgmpe.get_mean_and_stddevs(cx, cx, cx, iimt, stddev_types)

    lnmud = np.array(
        [
            [
                3.49839136,
                3.64832236,
                3.79749471,
                3.96239806,
                4.09468822,
                4.09389278,
                3.9801568,
            ],
            [
                3.56779917,
                3.7179769,
                3.88034759,
                4.03867162,
                4.1183871,
                4.04075263,
                3.92752286,
            ],
            [
                3.64030985,
                3.7971508,
                3.96235807,
                4.09568006,
                4.09985241,
                3.99427412,
                3.89079342,
            ],
            [
                3.67729241,
                3.85110009,
                4.0256281,
                4.12611129,
                4.04239396,
                3.92914758,
                3.82659081,
            ],
            [
                3.66418571,
                3.79965871,
                3.94282979,
                3.9979756,
                3.94871455,
                3.87029433,
                3.77947026,
            ],
            [
                3.57078679,
                3.6804228,
                3.74635951,
                3.78042292,
                3.77640035,
                3.74743154,
                3.69882757,
            ],
            [
                3.45042329,
                3.51208778,
                3.55908595,
                3.58603938,
                3.59797861,
                3.59382117,
                3.57402577,
            ],
        ]
    )
    lnsdd = np.array(
        [
            [
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
            ],
            [
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
            ],
            [
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
            ],
            [
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
            ],
            [
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
            ],
            [
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
            ],
            [
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
                0.65489331,
            ],
        ]
    )
    lnsdd_inter = np.array(
        [
            [
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
            ],
            [
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
            ],
            [
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
            ],
            [
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
            ],
            [
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
            ],
            [
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
            ],
            [
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
                0.30024866,
            ],
        ]
    )
    lnsdd_intra = np.array(
        [
            [
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
            ],
            [
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
            ],
            [
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
            ],
            [
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
            ],
            [
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
            ],
            [
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
            ],
            [
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
                0.58269718,
            ],
        ]
    )

    np.testing.assert_allclose(lnmu[0].reshape(orig_shape), lnmud)
    if TEST:
        np.testing.assert_allclose(lnsd[0].reshape(orig_shape), lnsdd)
        np.testing.assert_allclose(lnsd[1].reshape(orig_shape), lnsdd_inter)
        np.testing.assert_allclose(lnsd[2].reshape(orig_shape), lnsdd_intra)
    else:
        print(repr(lnmu[0].reshape(orig_shape)))
        print(repr(lnsd[0].reshape(orig_shape)))
        print(repr(lnsd[1].reshape(orig_shape)))
        print(repr(lnsd[2].reshape(orig_shape)))


def test_multigmpe_exceptions():
    gmpes = [
        AbrahamsonEtAl2014(),
        BooreEtAl2014(),
        CampbellBozorgnia2014(),
        ChiouYoungs2014(),
    ]
    wts = [0.25, 0.25, 0.25, 0.25]

    ASK14 = AbrahamsonEtAl2014()

    iimt = imt.SA(1.0)
    size = 100
    rctx = RuptureContext()
    dctx = DistancesContext()
    sctx = SitesContext()
    sctx.sids = np.array(range(size))

    rctx.rake = 0.0
    rctx.dip = 90.0
    rctx.ztor = 0.0
    rctx.mag = 8.0
    rctx.width = 10.0
    rctx.hypo_depth = 8.0

    dctx.rjb = np.logspace(1, np.log10(800), size)
    dctx.rrup = dctx.rjb
    dctx.rhypo = dctx.rjb
    dctx.rx = dctx.rjb
    dctx.ry0 = dctx.rjb

    sctx.vs30 = np.ones_like(dctx.rjb) * 275.0
    sctx.vs30measured = np.full_like(dctx.rjb, False, dtype="bool")
    set_sites_depth_parameters(sctx, ASK14)

    # Check for exception on unavailable standard deviation types
    with pytest.raises(Exception) as a:
        rx = rctx
        cx = stuff_context(sctx, rx, dctx)
        stddev_types = ["Blerg"]
        mgmpe = MultiGMPE.__from_list__(gmpes, wts)
        lnmu, lnsd = mgmpe.get_mean_and_stddevs(cx, cx, cx, iimt, stddev_types)

    # Check for invalid conf
    with pytest.raises(Exception) as a:
        gmpelist = [""]
        wts = [0.5, 0.5]
        fgmpes, fwts = filter_gmpe_list(gmpelist, wts, imt=imt.SA(1.0))

    # Check for exception due to weights:
    with pytest.raises(Exception) as a:
        wts = [0.25, 0.25, 0.25, 0.25 + 1e-4]
        mgmpe = MultiGMPE.__from_list__(gmpes, wts)

    # Check exception on GMPE check
    with pytest.raises(Exception) as a:
        wts = [1.0]
        mgmpe = MultiGMPE.__from_list__(["BA08"], wts)

    # Check exception on length of gmpe and weight lenghts
    with pytest.raises(Exception) as a:
        gmpes = [BooreEtAl2014(), Campbell2003()]
        wts = [1.0]
        mgmpe = MultiGMPE.__from_list__(gmpes, wts)

    # Check exception on standard deviation type
    with pytest.raises(Exception) as a:
        gmpes = [Campbell2003()]
        wts = [1.0]
        mgmpe = MultiGMPE.__from_list__(gmpes, wts)
        stddev_types = [const.StdDev.INTER_EVENT]
        cx = stuff_context(sctx, rctx, dctx)
        lnmu, lnsd = mgmpe.get_mean_and_stddevs(cx, cx, cx, iimt, stddev_types)


if __name__ == "__main__":
    test_basic()
    test_from_config_set_of_sets()
    test_from_config_set_of_gmpes()
    test_from_config_single_gmpe()
    test_nga_w2_m8()
    test_nga_w2_m6()
    test_multigmpe_has_site()
    test_multigmpe_get_sites_depth_parameters()
    test_multigmpe_get_mean_stddevs()
    test_multigmpe_exceptions()
    test_from_config_set_of_sets_3_sec()
