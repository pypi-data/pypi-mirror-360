<p align="center">
  <img src="https://raw.githubusercontent.com/juanaldayparejo/archnemesis-dist/main/docs/images/archnemesis_logo_black_background.png" alt="archNEMESIS logo" width="400"/>
</p>

[![DOI](https://img.shields.io/badge/version-v1.0.4-red)](https://doi.org/10.5281/zenodo.15789739)
[![Documentation](https://img.shields.io/badge/readthedocs-latest-blue)](https://archnemesis.readthedocs.io)
[![GitHub](https://img.shields.io/badge/github-code-green)](https://github.com/juanaldayparejo/archnemesis-dist)
[![archNEMESIS](https://img.shields.io/badge/archNEMESIS-reference-yellow)](https://doi.org/10.48550/arXiv.2501.16452)
[![NEMESIS](https://img.shields.io/badge/NEMESIS-reference-yellow)](https://doi.org/10.1016/j.jqsrt.2007.11.006)
[![Discord](https://img.shields.io/badge/discord-join-pink)](https://discord.gg/Te43qbrVFK)

__________

ArchNEMESIS is an open-source Python package developed for the analysis of remote sensing spectroscopic observations of planetary atmospheres. 
It is based on the widely used NEMESIS (Non-linear Optimal Estimator for MultivariatE Spectral analySIS) radiative transfer and retrieval tool, 
which has been extensively used for the investigation of a wide variety of planetary environments.

ArchNEMESIS is currently maintained by [Juan Alday](https://research.open.ac.uk/people/ja22256) and [Joseph Penn](https://www.physics.ox.ac.uk/our-people/penn).
The [NEMESIS](https://nemesiscode.github.io/index.html) algorithm, code archNEMESIS is based on, was originally developed by [Patrick Irwin](https://www.physics.ox.ac.uk/our-people/irwin).

If interested users are missing key points in the documentation, would appreciate seeing jupyter notebooks for certain purposes, or want to report issues, please do so by contacting us or joining our [Discord](https://discord.gg/Te43qbrVFK) channel.


## Documentation
For full documentation, visit [archnemesis.readthedocs.io](https://archnemesis.readthedocs.io/en/latest/).


## Installation

There are three main ways to install **archNEMESIS**, depending on your use case:

### Installing from GitHub (developer mode)

The latest version of code has to be downloaded from [Github](https://github.com/juanaldayparejo/archnemesis-dist.git) under a [GNU General Public License v3](LICENSE). To do so, type in the command window:

```bash
git clone https://github.com/juanaldayparejo/archnemesis-dist.git
```

Before installing archNEMESIS, we recommend users to create and load a new Python [virtual environment](https://docs.python.org/3/library/venv.html) for a clean install:

```bash
python -m venv name_of_virtual_environment/
source name_of_virtual_environment/bin/activate
```

Then move into the package directory:

```bash
cd archnemesis-dist
```

Finally, we need to install the library. Given that archNEMESIS is a highly dynamic package were new additions are frequently introduced, we recommend installing the package but keeping it editable by typing:

```bash
pip install --editable .
```

This will install archNEMESIS, but with the ability to update any changes made to the code (e.g., when introducing new model parameterisations or methods). In addition, it will install all the required libraries archNEMESIS depends on.


### Installing from PyPI

The simplest way to install archNEMESIS is via PyPI.  
We recommend doing this inside a clean Python virtual environment:

```bash
python -m venv archnemesis-env
source archnemesis-env/bin/activate
pip install archnemesis
```

This will install the latest stable release of the package along with its dependencies.
It is the recommended method if you just want to use the library without editing the source code.

## Contributing to archNEMESIS

If you want to contribute to the development of archNEMESIS, please follow our [Contribution Guidelines](CONTRIBUTING.md).

## Citing archNEMESIS

If archNEMESIS has been significant in your research, we suggest citing the following articles:

- archNEMESIS reference publication:
   - Alday, J., Penn, J., Irwin, P. G. J., Mason, J. P., Yang, J., 2025. archNEMESIS: an open-source Python package for analysis of planetary atmospheric spectra. *Preprint in arXiv*. doi: [10.48550/ARXIV.2501.16452](https://doi.org/10.48550/ARXIV.2501.16452).

- NEMESIS reference publication:
   - Irwin, P. G. J., Teanby, N. A., De Kok, R., Fletcher, L. N., Howett, C. J. A., Tsang, C. C. C., ... & Parrish, P. D. (2008). The NEMESIS planetary atmosphere radiative transfer and retrieval tool. *Journal of Quantitative Spectroscopy and Radiative Transfer*, 109(6), 1136-1150. doi: [10.1016/j.jqsrt.2007.11.006](https://doi.org/10.1016/j.jqsrt.2007.11.006).

## Support 

If you have questions, suggestions, or encounter issues, you can:

- Open an issue on the [GitHub Issues page](https://github.com/juanaldayparejo/archnemesis-dist/issues)
- Ask questions on the [GitHub Discussions tab](https://github.com/juanaldayparejo/archnemesis-dist/discussions)
- Join our [Discord](https://discord.gg/Te43qbrVFK) channel.
- Contact the maintainer via email: juan.alday@open.ac.uk

Please note: This is a research software package maintained as time allows. While we aim to respond in a timely manner (i.e., within a week), we cannot guarantee a fixed response time.

## Revision history

- [1.0.5]() (8 July, 2025)
   - New release of archNEMESIS for publication at Journal of Open Research Software.
   - Fixed minor bugs throughout the code.
   - Added unit test for calculation of optical properties using Mie Theory.
   - Updated setup file to avoid dependency conflicts.

- [1.0.4](https://doi.org/10.5281/zenodo.15789739) (2 July, 2025)
   - New release of archNEMESIS for release on PyPI and Docker Hub.

- [1.0.3](https://doi.org/10.5281/zenodo.15699119) (19 June, 2025)
   - New release of archNEMESIS for first release on PyPI.

- [1.0.2](https://doi.org/10.5281/zenodo.15698743) (19 June, 2025)
   - Fixed minor bugs throughout the code.
   - Included new model parameterisations.
   - Included new automatic tests (e.g., forward models for solar occultation and limb geometry).
   - Flags now identified with ENUMS rather than magic numbers.
   - Model parameterisations now defined as classes.

- [1.0.1](https://doi.org/10.5281/zenodo.15123560) (2 April, 2025)
   - Fixed minor bugs throughout the code.
   - Implementation of Oren-Nayar surface reflectance model.
   - Implementation of different surface reflectance models in multiple scattering calculations.
   - Included new automatic tests.
   - Included new model parameterisations.

- [1.0.0](https://doi.org/10.5281/zenodo.14746548) (27 January, 2025)
    - First release for publication at Journal of Open Research Software.

## Dependencies

- Numerical calculations: [numpy](https://numpy.org/); [scipy](https://scipy.org/)
- Visualisations: [matplotlib](https://matplotlib.org/); [basemap](https://matplotlib.org/basemap/stable/); [corner](https://corner.readthedocs.io/en/latest/)
- File handling: [h5py](https://www.h5py.org/)
- Optimisation: [numba](https://numba.pydata.org/); [joblib](https://joblib.readthedocs.io/en/stable/)
- Nested sampling: [pymultinest](https://johannesbuchner.github.io/PyMultiNest/)
- Extraction of ERA-5 model profiles: [cdsapi](https://pypi.org/project/cdsapi/); [pygrib](https://jswhit.github.io/pygrib/)  

