<div align="left">
  <img src="https://github.com/yidapa/salam/blob/master/docs/logo/salam-logo.jpg" height="160px"/>
</div>


# A Python tool for High-Throughput Virtual Screening of Organic Chromophores driven by Structural Crossover, Mutation and Machine Learning.

[!PyPI version](https://pypi.org/project/salam/)
[!Documentation status](https://salam.readthedocs.io/en/latest/)

[Documentation](https://salam.readthedocs.io/en/latest/) | [Colab Tutorial](https://github.com/yidapa/salam/blob/master/docs/tutorials) |


### Table of contents:

- [Requirements](#requirements)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [About Us](#about-us)
- [Citing SALAM](#citing-salam)

## Requirements

SALAM currently supports Python 3.7 and later versions, and requires these packages on any condition.

- [joblib](https://pypi.python.org/pypi/joblib)
- [NumPy](https://numpy.org/)
- [pandas](http://pandas.pydata.org/)
- [scikit-learn](https://scikit-learn.org/stable/)
- [SciPy](https://www.scipy.org/)
- [rdkit](https://www.rdkit.org/)
- [DeepChem](https://deepchem.io/)
  
[The source for this project is available here][src].


## Installation

SALAM can be installed using pip as

```bash
pip install salam
```


## Getting Started

The SALAM project maintains a collection of [tutorials](https://github.com/yidapa/salam/blob/master/docs/tutorials).

Typical usage is: 
```bash
python  salam  salam_paras.inp  &>  salam.logfile  &
```


## About Us

SALAM is currently maintained by C. J. Tu. Anyone is free to join and contribute!

## Citing SALAM

If you have used SALAM in the course of your research, we ask that you cite it.

There is still no official SALAM publication, the recommended citation is:  

SALAM: an HTVS tool for organic materials. https://github.com/yidapa/salam




[src]: https://github.com/yidapa/salam
