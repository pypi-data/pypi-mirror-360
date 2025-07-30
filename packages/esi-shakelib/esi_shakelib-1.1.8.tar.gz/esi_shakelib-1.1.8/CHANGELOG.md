# main
    - Fix ffsimmer bug to handle the 180 degree longitude sensibly

## 1.1.8 / 2025-07-08
    FFSimmer:
    - Use Huang et al aspect ratio equations.
    - Make depth a normal distribution.
    - Make dx a normal distribution per Mai et al.
    - Make dy a Weibull distribution per Mai et al.
    - Add new constraints: aspect_ratio, min/max_sz_depth.

## 1.1.7 / 2025-05-21
    - Set ffsimmer seismogenic depths to 20 and 15 km (for active and stable).
    - Fix bug when no dyfi observations have min_nresp responses.

## 1.1.6 / 2025-04-01
    - Fix bug in generic_site_amplification() to address change in OQ.

## 1.1.5 / 2025-03-31
    - Set the seismogenic depths of the ACR and SCR regions.

## 1.1.4 / 2025-03-20
    - Refactor to use OQ's _get_cb14_basin_term() rather than the old CB14 get_basin_term()
    - Set OQ version to 1.23.1 in pyproject.toml.

## 1.1.3 / 2025-03-17
    - Initialize mean, sig, tau, and phi to zero in multiutils.py.                          
    - Fix cx bug in ffsimmer.

## 1.1.2 / 2025-03-08
    - Performance enhancements to FFSimmer.

## 1.1.1 / 2025-02-27
    - Refactor strings for sqlite to single quote string literals.
    - Refactor to emove a bunch of linter warnings.
    - Eliminate a bunch of deprecation warnings (datetime.utcnow(), etc.)

## 1.1.0 / 2025-01-24

    - Pin OQ to less than 3.22.
    - Add code in multigmpe to handle ztor constraints from modules.conf.

## 1.0.16 / 2024-10-07
    - Fix pipelines to use S3 buckets to download slab data.
    - Fix station.py to handle autogmp packets' h1, h2, z channels.

## 1.0.15 / 2024-09-28
    - Update .gitlab-ci.yml to us python 3.12 image.
    - Update package versions in pyproject.toml for python 3.12.

## 1.0.14 / 2024-09-24
    - Fix bugs in ffsimmer compute_points discovered by Kishor and Davis.

## 1.0.13 / 2024-08-31
    - Fix handling of openquake imt specifiers to be consistent with latest OQ.

## 1.0.12 / 2024-08-26
    - Added NSHM-specific versions of GMMs: Atkinson-Macias 2009, Zhao 2006, AK
      versions of Parker 2020, Abrahamson Gulerce 2020, and Kuehn 2020.
    - Made contexts dummy classes, and turned OQ input context into a recarray. Made
      several context attributes into arrays instead of scalars.
    - Make multigmpe return None when no gmm can make a specified period.
    - Refactor model module to not report IMTs that cannot be predicted with specified
      gmpes. All other multigmpes are IMT-specific.
    - Fix bug in FFSimmer uncertainties that was uncovered by Davis E.
    - Add sites parameters for several new gmms.
    - Removed sites and large distance params and code from multigmpe.
    - Fixed many, many linter complaints. 

## 1.0.11 / 2024-08-21
    - Fix bug in ordering of STDDEV types in ffsimmer.

## 1.0.10 / 2024-07-16
    - Remove mixed effects regression in favor of law of total variance in FFSimmer. 
    - Change default Vs30 from 686 to 760 in Sites class.

## 1.0.9 / 2024-07-08
    - Fix N/S flip bug in FFSimmer; limit numpy version to <2.0.

## 1.0.8 / 2024-06-05
    - Various improvements to FFSimmer.

## 1.0.7 / 2024-05-28
    - Add depth range to FFSimmer; clean up interface to not have origin as an                
      argument (it is provided by rff); clean cruft out of VirtualIPE;

## 1.0.6 / 2024-05-16
    - Fix bug in origin in FFSimmer: _tectonic_region to _tectonic_region

## 1.0.5 / 2024-04-23
    - Add FFSimmer and GenericSiteAmplification; revise multigmpe, etc.

## 1.0.4 / 2023-11-28

- pyproject.toml: Pin openquake.engine to version 3.18.0 and add alpha-shapes dependency.

## 1.0.3 / 2023-11-27

- Add get_shakelib_version() function to utils.
- Update CI to have deploy depend on test deploy job

## 1.0.2 / 2023-11-17

- Fix the order of quotes around the tectonic regions in mulltigmpe.py
- Add coverage explicitly to gitlab-ci.yml

## 1.0.1 / 2023-11-15

- Fix the order of quotes around the tectonic regions in mulltigmpe.py
- Add coverage explicitly to gitlab-ci.yml

## 1.0.0 / 2023-10-10

- Initial commit and construction of the repository
- Adding in CI workflow for testing, deployment, etc.
- Fixing strec configuration issues
- Fixing existing dependency issues
- Using dynamic versioning with setuptools_scm
