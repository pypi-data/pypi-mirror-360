#!/usr/bin/env python

# stdlib imports
import copy
import logging
from importlib import import_module

# third party imports
import numpy as np
from openquake.hazardlib import const
from openquake.hazardlib.gsim.base import GMPE
from openquake.hazardlib.gsim.boore_2014 import BooreEtAl2014
from openquake.hazardlib.gsim.campbell_bozorgnia_2014 import (
    CampbellBozorgnia2014,
)
from openquake.hazardlib.imt import PGA, PGV, SA
from openquake.hazardlib.valid import gsim

# local imports
from esi_shakelib.utils.contexts import RuptureContext
from esi_shakelib.utils.gmpe_coeffs import get_gmpe_sa_periods
from esi_shakelib.conversions.imc.boore_kishida_2017 import BooreKishida2017
from esi_shakelib.conversions.imt.abrahamson_bhasin_2020 import (
    AbrahamsonBhasin2020,
)
from esi_shakelib.multiutils import gmpe_gmas
from esi_shakelib.sites import addDepthParameters

# These are imported for their side effects...
import esi_shakelib.gmpe.atkinson_macias_2009
import esi_shakelib.gmpe.zhao_2006
import esi_shakelib.gmpe.kuehn_2020
import esi_shakelib.gmpe.ak_bias_gmms
import esi_shakelib.gmpe.nga_east


def set_sites_depth_parameters(sites, gmpe):
    """
    Need to select the appropriate z1pt0 value for different GMPEs.
    Note that these are required site parameters, so even though
    OQ has these equations built into the class in most cases.
    I have submitted an issue to OQ requesting subclasses of these
    methods that do not require the depth parameters in the
    SitesContext to make this easier.

    Args:
        sites:1 An OQ sites context.
        gmpe: An OQ GMPE instance.

    Returns:
        An OQ sites context with the depth parameters set for the
        requested GMPE.
    """
    if gmpe == "[MultiGMPE]":
        return sites

    addDepthParameters(sites)

    if gmpe in (
        "[AbrahamsonEtAl2014]",
        '[AbrahamsonEtAl2014]\nregion = "TWN"',
        '[AbrahamsonEtAl2014]\nregion = "CHN"',
    ):
        sites.z1pt0 = sites.z1pt0_ask14_cal
    if gmpe == '[AbrahamsonEtAl2014]\nregion = "JPN"':
        sites.z1pt0 = sites.z1pt0_ask14_jpn
    if gmpe == "[ChiouYoungs2014]" or isinstance(gmpe, BooreEtAl2014):
        sites.z1pt0 = sites.z1pt0_cy14_cal

    gmpe_name = f"{gmpe}"
    if "KuehnEtAl202" in gmpe_name:
        if "Japan" in gmpe_name:
            sites.z2pt5 = sites.z2pt5_cb14_jpn
        else:
            sites.z2pt5 = sites.z2pt5_cb14_cal
    if "AbrahamsonGulerce2020S" in gmpe_name:
        if "Japan" in gmpe_name:
            sites.z2pt5 = sites.z2pt5_cb14_jpn
        else:
            sites.z2pt5 = sites.z2pt5_cb14_cal
    if "ZhaoEtAl2006S" in gmpe_name:
        if "Japan" in gmpe_name:
            sites.z2pt5 = sites.z2pt5_cb14_jpn
        else:
            sites.z2pt5 = sites.z2pt5_cb14_cal
    if "AtkinsonMacias2009" in gmpe_name:
        if "Japan" in gmpe_name:
            sites.z2pt5 = sites.z2pt5_cb14_jpn
        else:
            sites.z2pt5 = sites.z2pt5_cb14_cal
    if "KuehnEtAl2020S" in gmpe_name:
        # This is just a WAG at what this GMPE wants
        if "Japan" in gmpe_name:
            sites.z2pt5 = sites.z2pt5_cb14_jpn
        else:
            sites.z2pt5 = sites.z2pt5_cb14_cal
        sites.z1pt0 = sites.z1pt0_cy14_cal

    if "KothaEtAl2020ESHM20" in gmpe_name:
        sites.region = np.zeros_like(sites.vs30)

    if isinstance(gmpe, CampbellBozorgnia2014):
        if (
            gmpe == "[CampbellBozorgnia2014JapanSite]"
            or gmpe == "[CampbellBozorgnia2014HighQJapanSite]"
            or gmpe == "[CampbellBozorgnia2014LowQJapanSite]"
        ):
            sites.z2pt5 = sites.z2pt5_cb14_jpn
        else:
            sites.z2pt5 = sites.z2pt5_cb14_cal
    if (
        gmpe == "[ChiouYoungs2008]"
        or gmpe == "[Bradley2013]"
        or gmpe == "[Bradley2013Volc]"
    ):
        sites.z1pt0 = sites.z1pt0_cy08
    if gmpe == "[CampbellBozorgnia2008]":
        sites.z2pt5 = sites.z2pt5_cb07
    if gmpe == "[AbrahamsonSilva2008]":
        sites.z1pt0 = gmpe._compute_median_z1pt0(sites.vs30)

    return sites


def stuff_context(sites, rup, dists):
    """
    Function to fill a rupture context with the contents of all of the
    other contexts.

    Args:
        sites (SiteCollection): A SiteCollection object.

        rup (RuptureContext): A RuptureContext object.

        dists (DistanceContext): A DistanceContext object.

    Returns:
        RuptureContext: A new RuptureContext whose attributes are all of
        the elements of the three inputs.
    """
    if (
        isinstance(sites, np.recarray)
        and isinstance(rup, np.recarray)
        and isinstance(dists, np.recarray)
        and np.all(sites == rup)
        and np.all(rup == dists)
    ):
        # We're already a rec array
        return rup

    shape = None
    ctx = RuptureContext()
    for name, val in vars(sites).items():
        if name.startswith("__"):
            continue
        # We don't want the sites lons and lats, we want the dists ones
        if name in ["lons", "lats"]:
            continue
        if shape is None:
            shape = val.shape
        setattr(ctx, name, val)
    for name, val in vars(rup).items():
        if name.startswith("__"):
            continue
        if not isinstance(val, np.ndarray):
            val = np.full(shape, val)
        setattr(ctx, name, val)
    for name, val in vars(dists).items():
        if name.startswith("__"):
            continue
        setattr(ctx, name, val)

    ctx.occurrence_rate = np.full(shape, 1e-5)

    cols = []
    arrs = []
    for key, val in vars(ctx).items():
        if key.startswith("__"):
            continue
        cols.append(key)
        arrs.append(val)
    cx = np.rec.fromarrays(arrs, names=cols)
    return cx


def get_gmpe_from_name(name, conf):

    # Only import the NullGMPE when we're testing
    # We'll want to import any other GMPEs we add at the top of this module
    # so that gsim() picks them up; anything in OQ is already included
    if name == "NullGMPE":
        _ = import_module(conf["gmpe_modules"][name][1])
    return gsim(name)


class MultiGMPE(GMPE):
    """
    Implements a GMPE that is the combination of multiple GMPEs.

    """

    DEFINED_FOR_TECTONIC_REGION_TYPE = None
    DEFINED_FOR_INTENSITY_MEASURE_TYPES = None
    DEFINED_FOR_INTENSITY_MEASURE_COMPONENT = None
    DEFINED_FOR_STANDARD_DEVIATION_TYPES = set([const.StdDev.TOTAL])
    REQUIRES_SITES_PARAMETERS = None
    REQUIRES_RUPTURE_PARAMETERS = None
    REQUIRES_DISTANCES = None

    def get_mean_and_stddevs(self, sites, rup, dists, imt, stddev_types):
        """
        See superclass `method <http://docs.openquake.org/oq-hazardlib/master/gsim/index.html#openquake.hazardlib.gsim.base.GroundShakingIntensityModel.get_mean_and_stddevs>`__.

        """  # noqa

        for key, val in rup.__dict__.items():
            if not isinstance(val, np.ndarray):
                setattr(rup, key, np.full_like(sites.vs30, val))

        sd_avail = self.DEFINED_FOR_STANDARD_DEVIATION_TYPES
        if not sd_avail.issuperset(set(stddev_types)):
            raise TypeError("Requested an unavailable stddev_type.")

        if not isinstance(imt, list):
            imt = [imt]
        # Evaluate MultiGMPE:
        lnmu, lnsd = self.__get_mean_and_stddevs__(
            sites, rup, dists, imt, stddev_types
        )

        return lnmu, lnsd

    def __get_mean_and_stddevs__(self, sites, rup, dists, imt, stddev_types):

        nsd = len(stddev_types)
        # ---------------------------------------------------------------------
        # Sort out which set of weights to use
        # ---------------------------------------------------------------------
        wts = self.WEIGHTS

        nimt = len(imt)
        # ---------------------------------------------------------------------
        # This is the array to hold the weighted combination of the GMPEs
        # ---------------------------------------------------------------------
        lnmu = np.zeros((nimt, np.size(sites.vs30)))
        # ---------------------------------------------------------------------
        # Hold on to the individual means and stddevs so we can compute the
        # combined stddev
        # ---------------------------------------------------------------------
        lnmu_list = [[] for _ in range(nimt)]
        lnsd_list = [[] for _ in range(nimt)]

        for i, gmpe in enumerate(self.GMPES):
            # -----------------------------------------------------------------
            # Loop over GMPE list
            # -----------------------------------------------------------------

            set_sites_depth_parameters(sites, gmpe)

            # -----------------------------------------------------------------
            # Select the IMT
            # -----------------------------------------------------------------

            gmpe_imts = [
                imt.__name__
                for imt in list(gmpe.DEFINED_FOR_INTENSITY_MEASURE_TYPES)
            ]

            timt = copy.copy(imt)
            if (
                not isinstance(gmpe, MultiGMPE)
                and PGV() in timt
                and ("PGV" not in gmpe_imts)
            ):
                ab2020 = AbrahamsonBhasin2020(rup.mag)
                pgv_ix = timt.index(PGV())
                timt[pgv_ix] = SA(ab2020.getTref())

            # -----------------------------------------------------------------
            # Grab GMPE_LIMITS in gmpe instance for later as the multigmpe
            # nests downward.
            # -----------------------------------------------------------------
            if hasattr(self, "GMPE_LIMITS"):
                # Remember that GMPE_LIMITS is only present if it is getting
                # loaded from a config... we could change this eventually.
                gmpe.GMPE_LIMITS = self.GMPE_LIMITS

            # -----------------------------------------------------------------
            # Apply GMPE_LIMITS if applicable
            # -----------------------------------------------------------------
            if hasattr(gmpe, "GMPE_LIMITS"):
                gmpes_with_limits = list(gmpe.GMPE_LIMITS.keys())
                gmpe_class_str = str(gmpe).replace("[", "").replace("]", "")
                if gmpe_class_str in gmpes_with_limits:
                    limit_dict = gmpe.GMPE_LIMITS[gmpe_class_str]
                    for k, v in limit_dict.items():
                        if k == "vs30":
                            vs30min = float(v[0])
                            vs30max = float(v[1])
                            sites.vs30 = np.clip(sites.vs30, vs30min, vs30max)
                            addDepthParameters(sites)
                        elif k == "ztor":
                            ztor_min = float(v[0])
                            ztor_max = float(v[1])
                            rup.ztor = np.clip(rup.ztor, ztor_min, ztor_max)

            # -----------------------------------------------------------------
            # Evaluate
            # -----------------------------------------------------------------
            if not isinstance(gmpe, MultiGMPE):
                ctx = stuff_context(sites, rup, dists)
                lmean, lsd = gmpe_gmas(gmpe, ctx, timt, stddev_types)
            else:
                lmean, lsd = gmpe.get_mean_and_stddevs(
                    sites, rup, dists, timt, stddev_types
                )

            if not isinstance(gmpe, MultiGMPE):
                # -------------------------------------------------------------
                # If IMT is PGV and PGV is not given by the GMPE, then
                # convert from the appropriate PSA
                # -------------------------------------------------------------
                if (PGV() in imt) and ("PGV" not in gmpe_imts):
                    tmean, tsd = ab2020.getPGVandSTDDEVS(
                        lmean[pgv_ix],
                        lsd[pgv_ix * nsd : (pgv_ix + 1) * nsd],
                        stddev_types,
                        ctx.rrup,
                        ctx.vs30,
                    )
                    lmean[pgv_ix] = tmean
                    for ix, _ in enumerate(stddev_types):
                        lsd[pgv_ix * nsd + ix] = tsd[ix]

                # -------------------------------------------------------------
                # Convertions due to component definition
                # -------------------------------------------------------------
                imc_in = gmpe.DEFINED_FOR_INTENSITY_MEASURE_COMPONENT
                imc_out = self.DEFINED_FOR_INTENSITY_MEASURE_COMPONENT
                if imc_in != imc_out:
                    bk17 = BooreKishida2017(imc_in, imc_out)
                    for kk, kimt in enumerate(timt):
                        if kimt.string == "MMI":
                            continue
                        lmean[kk] = bk17.convertAmps(
                            kimt, lmean[kk], dists.rrup, rup.mag
                        )
                        #
                        # The extra sigma from the component conversion
                        # appears to apply to the total sigma, so the
                        # question arises as to how to apportion it between
                        # the intra- and inter-event sigma. Here we assume
                        # it all enters as intra-event sigma.
                        #
                        for j, stddev_type in enumerate(stddev_types):
                            if stddev_type == const.StdDev.INTER_EVENT:
                                continue
                            lsd[kk * nsd + j] = bk17.convertSigmas(
                                kimt, lsd[kk * nsd + j]
                            )

            # End: if GMPE is not MultiGMPE

            #
            # At this point lsd will have nimt * len(stddev_types) entries, the
            #

            # -----------------------------------------------------------------
            # Compute weighted mean and collect the elements to compute sd
            # -----------------------------------------------------------------

            for kk, kimt in enumerate(timt):
                lnmu[kk] = lnmu[kk] + wts[i] * lmean[kk]
                lnmu_list[kk].append(lmean[kk])
                lnsd_list[kk] = lnsd_list[kk] + lsd[kk * nsd : (kk + 1) * nsd]

        # -----------------------------------------------------------------
        # The mean is a weighted sum of random variables, so the stddev
        # is the weighted sum of of their covariances (effectively). See:
        # https://en.wikipedia.org/wiki/Variance#Weighted_sum_of_variables
        # for an explanation. Also see:
        # http://usgs.github.io/shakemap/manual4_0/tg_processing.html#ground-motion-prediction
        # for a discussion on the way this is implemented here.
        # -------------------------------------------------------------- # noqa

        nwts = len(wts)
        npwts = np.array(wts).reshape((1, -1))
        lnsd_new = []
        for kk, kimt in enumerate(timt):
            nsites = len(lnmu[kk])
            # Find the correlation coefficients among the gmpes; if there are
            # fewer than 10 points, just use an approximation (noting that the
            # correlation among GMPEs tends to be quite high).
            if nsites < 10:
                cc = np.full((nwts, nwts), 0.95)
                np.fill_diagonal(cc, 1.0)
            else:
                np.seterr(divide="ignore", invalid="ignore")
                cc = np.reshape(np.corrcoef(lnmu_list[kk]), (nwts, nwts))
                np.seterr(divide="warn", invalid="warn")
                cc[np.isnan(cc)] = 1.0

            # Multiply the correlation coefficients by the weights matrix
            # (this is cheaper than multiplying all of elements of each
            # stddev array by their weights since we have to multiply
            # everything by the correlation coefficient matrix anyway))
            cc = ((npwts * npwts.T) * cc).reshape((nwts, nwts, 1))
            for i in range(nsd):
                sdlist = []
                for j in range(nwts):
                    sdlist.append(
                        lnsd_list[kk][j * nsd + i].reshape((1, 1, -1))
                    )
                sdstack = np.hstack(sdlist)
                wcov = (sdstack * np.transpose(sdstack, axes=(1, 0, 2))) * cc
                # This sums the weighted covariance as each point in the output
                lnsd_new.append(np.sqrt(wcov.sum((0, 1))))

        return (lnmu, lnsd_new)

    @classmethod
    def __from_config__(cls, conf, filter_imt=None):
        """
        Construct a MultiGMPE from a config file.

        Args:
            conf (dict): Dictionary of config options.
            filter_imt (IMT): An optional IMT to filter/reweight the GMPE list.

        Returns:
            MultiGMPE object.

        """
        imc = getattr(const.IMC, conf["interp"]["component"])
        selected_gmpe = conf["modeling"]["gmpe"]

        logging.debug("selected_gmpe: %s", selected_gmpe)
        logging.debug("IMC: %s", imc)

        # ---------------------------------------------------------------------
        # Allow for selected_gmpe to be found in either conf['gmpe_sets'] or
        # conf['gmpe_modules'], if it is a GMPE set, then all entries must be
        # either a GMPE or a GMPE set (cannot have a GMPE set that is a mix of
        # GMPEs and GMPE sets).
        # ---------------------------------------------------------------------

        if selected_gmpe in conf["gmpe_sets"].keys():
            selected_gmpe_sets = conf["gmpe_sets"][selected_gmpe]["gmpes"]
            gmpe_set_weights = [
                float(w) for w in conf["gmpe_sets"][selected_gmpe]["weights"]
            ]
            logging.debug("selected_gmpe_sets: %s", selected_gmpe_sets)
            logging.debug("gmpe_set_weights: %s", gmpe_set_weights)

            # -----------------------------------------------------------------
            # If it is a GMPE set, does it contain GMPEs or GMPE sets?
            # -----------------------------------------------------------------

            set_of_gmpes = all(
                s in conf["gmpe_modules"] for s in selected_gmpe_sets
            )
            set_of_sets = all(
                s in conf["gmpe_sets"] for s in selected_gmpe_sets
            )

            if set_of_sets is True:
                mgmpes = []
                mweights = []
                for ix, s in enumerate(selected_gmpe_sets):
                    mgmpe = cls.__multigmpe_from_gmpe_set__(
                        conf, s, filter_imt=filter_imt
                    )
                    if mgmpe is None:
                        continue
                    mgmpes.append(mgmpe)
                    mweights.append(gmpe_set_weights[ix])
                if len(mgmpes) == 0:
                    return None
                mweights = np.array(mweights)
                mweights = mweights / np.sum(mweights)
                out = MultiGMPE.__from_list__(mgmpes, mweights, imc=imc)
            elif set_of_gmpes is True:
                out = cls.__multigmpe_from_gmpe_set__(
                    conf, selected_gmpe, filter_imt=filter_imt
                )
                if out is None:
                    return None
            else:
                raise TypeError(
                    f"{selected_gmpe} must consist exclusively of keys in "
                    "conf['gmpe_modules'] or conf['gmpe_sets']"
                )
        elif selected_gmpe in conf["gmpe_modules"].keys():
            modinfo = conf["gmpe_modules"][selected_gmpe]
            # mod = import_module(modinfo[1])
            # tmpclass = getattr(mod, modinfo[0])
            # out = MultiGMPE.__from_list__([tmpclass()], [1.0], imc=imc)
            out = MultiGMPE.__from_list__(
                [get_gmpe_from_name(modinfo[0], conf)],
                [1.0],
                imc=imc,
                imt=filter_imt,
            )
            if out is None:
                return None
        else:
            raise TypeError(
                "conf['modeling']['gmpe'] must be a key in "
                "conf['gmpe_modules'] or conf['gmpe_sets']"
            )

        out.DESCRIPTION = selected_gmpe

        # ---------------------------------------------------------------------
        # Deal with GMPE limits
        # ---------------------------------------------------------------------
        gmpe_lims = conf["gmpe_limits"]

        # We need to replace the short name in the dictionary key with module
        # name here since the conf is not available within the MultiGMPE class.
        mods = conf["gmpe_modules"]
        mod_keys = mods.keys()
        new_gmpe_lims = {}
        for k, v in gmpe_lims.items():
            if k in mod_keys:
                new_gmpe_lims[mods[k][0]] = v
            else:
                new_gmpe_lims[k] = v

        out.GMPE_LIMITS = new_gmpe_lims

        return out

    @classmethod
    def __multigmpe_from_gmpe_set__(cls, conf, set_name, filter_imt=None):
        """
        Private method for constructing a MultiGMPE from a set_name.

        Args:
            conf (dict): A ShakeMap ConfigObj config object.
            filter_imt (IMT): An optional IMT to filter/reweight the GMPE list.
            set_name (str): Set name; must correspond to a key in
                conf['set_name'].

        Returns:
            MultiGMPE.

        """
        imc = getattr(const.IMC, conf["interp"]["component"])

        selected_gmpes = conf["gmpe_sets"][set_name]["gmpes"]
        selected_gmpe_weights = [
            float(w) for w in conf["gmpe_sets"][set_name]["weights"]
        ]

        # ---------------------------------------------------------------------
        # Import GMPE modules and initialize classes into list
        # ---------------------------------------------------------------------
        gmpes = []
        for g in selected_gmpes:
            # This is the old school way of importing the modules; I'm
            # leaving it in here temporarily just for documentation.
            # mod = import_module(conf['gmpe_modules'][g][1])
            # tmpclass = getattr(mod, conf['gmpe_modules'][g][0])
            # gmpes.append(tmpclass())
            gmpe_name = conf["gmpe_modules"][g][0]
            gmpes.append(get_gmpe_from_name(gmpe_name, conf))

        # ---------------------------------------------------------------------
        # Filter out GMPEs not applicable to this period
        # ---------------------------------------------------------------------
        if filter_imt is not None:
            filtered_gmpes, filtered_wts = filter_gmpe_list(
                gmpes, selected_gmpe_weights, filter_imt
            )
        else:
            filtered_gmpes, filtered_wts = gmpes, selected_gmpe_weights

        # ---------------------------------------------------------------------
        # Construct MultiGMPE
        # ---------------------------------------------------------------------
        logging.debug("    filtered_gmpes: %s", filtered_gmpes)
        logging.debug("    filtered_wts: %s", filtered_wts)

        if len(filtered_gmpes) == 0:
            return None

        mgmpe = MultiGMPE.__from_list__(
            filtered_gmpes,
            filtered_wts,
            imc=imc,
        )

        mgmpe.DESCRIPTION = set_name

        return mgmpe

    @classmethod
    def __from_list__(
        cls,
        gmpes,
        weights,
        imc=const.IMC.GREATER_OF_TWO_HORIZONTAL,
        imt=None,
        reference_vs30=760,
    ):
        """
        Construct a MultiGMPE instance from lists of GMPEs and weights.

        Args:
            gmpes (list): List of OpenQuake
                `GMPE <http://docs.openquake.org/oq-hazardlib/master/gsim/index.html#built-in-gsims>`__
                instances.

            weights (list): List of weights; must sum to 1.0.

            imc: Requested intensity measure component. Must be one listed
                `here <http://docs.openquake.org/oq-hazardlib/master/const.html?highlight=imc#openquake.hazardlib.const.IMC>`__.
                The amplitudes returned by the GMPEs will be converted to this
                IMC. Default is 'GREATER_OF_TWO_HORIZONTAL', which is used by
                ShakeMap. See discussion in
                `this section <http://usgs.github.io/shakemap/tg_choice_of_parameters.html#use-of-peak-values-rather-than-mean>`__
                of the ShakeMap manual.

            reference_vs30:
                Reference rock Vs30 in m/s. We do not check that this matches
                the reference rock in the GMPEs so this is the responsibility
                of the user.

        """  # noqa

        # ---------------------------------------------------------------------
        # Check that GMPE weights sum to 1.0:
        # ---------------------------------------------------------------------

        if np.abs(np.sum(weights) - 1.0) > 1e-7:
            raise ValueError("Weights must sum to one.")

        # ---------------------------------------------------------------------
        # Check that length of GMPE weights equals length of gmpe list
        # ---------------------------------------------------------------------

        if len(weights) != len(gmpes):
            raise ValueError(
                "Length of weights must match length of GMPE list."
            )

        # ---------------------------------------------------------------------
        # Check that gmpes is a list of OQ GMPE instances
        # ---------------------------------------------------------------------

        for g in gmpes:
            if not isinstance(g, GMPE):
                raise ValueError(f'"{g}" is a {type(g)} not a GMPE instance.')

        if imt is not None:
            gmpes, weights = filter_gmpe_list(gmpes, weights, imt)
            if len(gmpes) == 0:
                return None

        self = cls()
        self.GMPES = gmpes
        self.WEIGHTS = weights

        # ---------------------------------------------------------------------
        # Combine the intensity measure types. This is problematic:
        #   - Logically, we should only include the intersection of the sets
        #     of imts for the different GMPEs.
        #   - In practice, this is not feasible because most GMPEs in CEUS and
        #     subduction zones do not have PGV.
        #   - So instead we will use the union of the imts and then convert
        #     to get the missing imts later in get_mean_and_stddevs.
        # ---------------------------------------------------------------------

        imts = [set(g.DEFINED_FOR_INTENSITY_MEASURE_TYPES) for g in gmpes]
        self.DEFINED_FOR_INTENSITY_MEASURE_TYPES = set.union(*imts)

        # ---------------------------------------------------------------------
        # For VirtualIPE class, we also want to know if ALL of the GMPEs are
        # defined for PGV, in which case we will convert from PGV to MI,
        # otherwise use PGA or Sa.
        # ---------------------------------------------------------------------
        haspgv = [
            any(
                "PGV" in imtype.__name__
                for imtype in g.DEFINED_FOR_INTENSITY_MEASURE_TYPES
            )
            for g in gmpes
        ]
        self.ALL_GMPES_HAVE_PGV = all(haspgv)

        # ---------------------------------------------------------------------
        # Store intensity measure types for conversion in get_mean_and_stddevs.
        # ---------------------------------------------------------------------
        self.IMCs = [g.DEFINED_FOR_INTENSITY_MEASURE_COMPONENT for g in gmpes]

        # ---------------------------------------------------------------------
        # Store the component
        # ---------------------------------------------------------------------
        self.DEFINED_FOR_INTENSITY_MEASURE_COMPONENT = imc

        # ---------------------------------------------------------------------
        # Intersection of GMPE standard deviation types
        # ---------------------------------------------------------------------
        stdlist = [set(g.DEFINED_FOR_STANDARD_DEVIATION_TYPES) for g in gmpes]
        self.DEFINED_FOR_STANDARD_DEVIATION_TYPES = set.intersection(*stdlist)

        # ---------------------------------------------------------------------
        # Need union of site parameters, but it is complicated by the
        # different depth parameter flavors.
        # ---------------------------------------------------------------------
        sitepars = [set(g.REQUIRES_SITES_PARAMETERS) for g in gmpes]
        self.REQUIRES_SITES_PARAMETERS = set.union(*sitepars)

        # ---------------------------------------------------------------------
        # Construct a list of whether or not each GMPE has a site term
        # ---------------------------------------------------------------------
        self.HAS_SITE = ["vs30" in g.REQUIRES_SITES_PARAMETERS for g in gmpes]

        self.REFERENCE_VS30 = reference_vs30

        # ---------------------------------------------------------------------
        # Union of rupture parameters
        # ---------------------------------------------------------------------
        ruppars = [set(g.REQUIRES_RUPTURE_PARAMETERS) for g in gmpes]
        self.REQUIRES_RUPTURE_PARAMETERS = set.union(*ruppars)

        # ---------------------------------------------------------------------
        # Union of distance parameters
        # ---------------------------------------------------------------------
        distpars = [set(g.REQUIRES_DISTANCES) for g in gmpes]
        self.REQUIRES_DISTANCES = set.union(*distpars)

        return self

    def __describe__(self):
        """
        Construct a dictionary that describes the MultiGMPE.

        Note: For simplicity, this method ignores issues related to
        GMPEs used for the site term and changes in the GMPE with
        distance. For this level of detail, please see the config files.

        Returns:
            A dictionary representation of the MultiGMPE.
        """
        gmpe_dict = {"gmpes": [], "weights": [], "name": self.DESCRIPTION}

        for i, this_gmpe in enumerate(self.GMPES):
            gmpe_dict["weights"].append(self.WEIGHTS[i])
            if isinstance(this_gmpe, MultiGMPE):
                gmpe_dict["gmpes"].append(this_gmpe.__describe__())
            else:
                gmpe_dict["gmpes"].append(str(this_gmpe))

        return gmpe_dict


def filter_gmpe_list(gmpes, wts, imt):
    """
    Method to remove GMPEs from the GMPE list that are not applicable
    to a specific IMT. Rescales the weights to sum to one.

    Args:
        gmpes (list): List of GMPE instances.
        wts (list): List of floats indicating the weight of the GMPEs.
        imt (IMT): OQ IMT to filter GMPE list for.

    Returns:
        tuple: List of GMPE instances and list of weights.

    """
    if wts is None:
        n = len(gmpes)
        wts = [1 / n] * n

    per_max = [np.max(get_gmpe_sa_periods(g)) for g in gmpes]
    per_min = [np.min(get_gmpe_sa_periods(g)) for g in gmpes]
    if imt == PGA():
        sgmpe = [
            g
            for g in gmpes
            if any(
                "PGA" in t.__name__
                for t in g.DEFINED_FOR_INTENSITY_MEASURE_TYPES
            )
        ]
        swts = [
            w
            for g, w in zip(gmpes, wts)
            if any(
                "PGA" in t.__name__
                for t in g.DEFINED_FOR_INTENSITY_MEASURE_TYPES
            )
        ]
    elif imt == PGV():
        sgmpe = []
        swts = []
        for i, this_gmpe in enumerate(gmpes):
            if (
                any(
                    "PGV" in t.__name__
                    for t in this_gmpe.DEFINED_FOR_INTENSITY_MEASURE_TYPES
                )
            ) or (per_max[i] >= 1.0 >= per_min[i]):
                sgmpe.append(this_gmpe)
                swts.append(wts[i])
    else:
        per = imt.period
        sgmpe = []
        swts = []
        for i, this_gmpe in enumerate(gmpes):
            if per_max[i] >= per >= per_min[i]:
                sgmpe.append(this_gmpe)
                swts.append(wts[i])

    if len(sgmpe) == 0:
        return [], []
    #    raise KeyError(f"No applicable GMPEs from GMPE list for {str(imt)}")

    # Scale weights to sum to one
    swts = np.array(swts)
    swts = swts / np.sum(swts)

    return sgmpe, swts
