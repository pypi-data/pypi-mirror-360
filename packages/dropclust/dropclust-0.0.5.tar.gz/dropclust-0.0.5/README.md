# <p>  <b>DropClust</b> </p>

<!-- [![Documentation Status](https://readthedocs.org/projects/cellpose/badge/?version=latest)](https://cellpose.readthedocs.io/en/latest/?badge=latest) -->
<!-- [![PyPI version](https://badge.fury.io/py/cellpose-plus.svg)](https://badge.fury.io/py/cellpose-plus)
[![Downloads](https://pepy.tech/badge/cellpose-plus)](https://pepy.tech/project/cellpose-plus)
[![Downloads](https://pepy.tech/badge/cellpose-plus/month)](https://pepy.tech/project/cellpose-plus)
[![Python version](https://img.shields.io/pypi/pyversions/cellpose-plus)](https://pypistats.org/packages/cellpose-plus)
[![Licence: GPL v3](https://img.shields.io/github/license/ITMO-MMRM-lab/cellpose)](https://github.com/ITMO-MMRM-lab/cellpose/blob/master/LICENSE) -->
<!-- [![Contributors](https://img.shields.io/github/contributors-anon/ITMO-MMRM-lab/cellpose)](https://github.com/ITMO-MMRM-lab/cellpose/graphs/contributors) -->
<!-- [![website](https://img.shields.io/website?url=https%3A%2F%2Fwww.cellpose.org)](https://www.cellpose.org) -->
<!-- [![repo size](https://img.shields.io/github/repo-size/ITMO-MMRM-lab/cellpose)](https://github.com/ITMO-MMRM-lab/cellpose/) -->
<!-- [![GitHub stars](https://img.shields.io/github/stars/ITMO-MMRM-lab/cellpose?style=social)](https://github.com/ITMO-MMRM-lab/cellpose/) -->
<!-- [![GitHub forks](https://img.shields.io/github/forks/ITMO-MMRM-lab/cellpose?style=social)](https://github.com/ITMO-MMRM-lab/cellpose/) -->

<img src="https://gitlab.com/MeLlamoArroz/DropClustGUI/-/raw/master/logo.png" width="200" title="dropclust" alt="dropclust"/>

DropClust is an analytical tool that combines computer vision and machine learning algorithms to assess the morphology, geometry, and dynamics of frame videos of droplet clusters (or similar objects). \
Feature extraction capabilities were also added for further visual representation of the results.

Developed by the InfoChemistry scientific center, part of ITMO University.

### Installation

We suggest throught `conda` and `pip` (with `python>=3.9`).

1. Install [Anaconda](https://www.anaconda.com/download/).
2. Open an `anaconda` prompt / command prompt which has conda for python 3 in the path.
3. For a new environment for CPU only, run:\
 `conda create -n dropclust 'python==3.9'`
4. To activate the new environment, run `conda activate dropclust`
5. For NVIDIA GPUs, run:\
 `pip install torch torchvision` \
   We suggest to install CUDA 12.6
6. To install the latest PyPi release of Dropclust and its dependencies (see [setup.py](https://github.com/ITMO-MMRM-lab/cellpose/blob/main/setup.py)), run:\
  `pip install dropclust`.

### System requirements

Linux, Windows and Mac OS are supported for running the code. For running the graphical interface you will need a Mac OS later than Yosemite. At least 8GB of RAM is required to run the software. 16GB-32GB may be required for larger images. The software has been tested on Windows 10, Windows 11, Ubuntu 24.04, Manjaro and limitedly tested on Mac OS.

### Features
We calculate the following metrics / algorithms:

* Subject counting (amount of subjects).
* Area of subject (𝜇𝑚²).
* Roundness (0.0 - 1.0), having 1.0 for a perfect circle.
* Relative center coordinates.
* Voronoi diagram based on the centers.
* Voronoi entropy, a measure of order/chaos in the cells' positions.
* Convex hull.
* Continuous symmetry measure (CSM).
* Subjects segmentation and clustering.
* Color classification.
* Subject detection + tracking.

### General workflow

<img src="https://gitlab.com/MeLlamoArroz/DropClustGUI/-/raw/master/workflow.png" width="800" />

In order to obtain metrics from segmented cells, the initial stained images are merged into a
single image and organized into sub folders to be processed. A cell segmentation
procedure is performed using [Cellpose](https://github.com/MouseLand/cellpose), then we extract the metrics 
and finally we store the results in the form of images and CSV files.

### How to use

 Work in progress

### Citation

Work in progress

<!-- If you find our project helpful, use the following bibtex to reference our [paper](https://arxiv.org/abs/2410.18738).

~~~
@article{huaman2024cellpose+,
  title={Cellpose+, a morphological analysis tool for feature extraction of stained cell images},
  author={Huaman, Israel A and Ghorabe, Fares DE and Chumakova, Sofya S and Pisarenko, Alexandra A and Dudaev, Alexey E and Volova, Tatiana G and Ryltseva, Galina A and Ulasevich, Sviatlana A and Shishatskaya, Ekaterina I and Skorb, Ekaterina V and others},
  journal={arXiv preprint arXiv:2410.18738},
  year={2024}
}
~~~

As we work over Cellpose, we ask you to also cite the Cellpose [paper](https://t.co/kBMXmPp3Yn?amp=1). -->
