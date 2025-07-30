# pbhstat

A Python package for calculating the primordial black hole (PBH) mass function from a given primordial power spectrum with multiple statistical formalisms.

## 📦 Installation

We recommend installing pbhstat inside a Python virtual environment or conda environment.

```bash
pip install pbhstat
```

Alternatively, you can clone the repository directly from GitHub for development purposes:

```bash
git clone https://github.com/pipcole/pbhstat.git
```

and then run 
```bash
pip install -e .
```

## 🖥️ Compatibility

The code has been tested with:
- Python 3.9.15 on macOS Sonoma 14.1 (Apple M3 Pro)
- Python 3.12.3 on Ubuntu 24.04 LTS (Lenovo Yoga 7)
- Python 3.11 in Google Colab

## 📓 Quick Start

Two example Jupyter notebooks are provided:
1. Custom power spectrum input
2. Pre-defined piecewise power spectrum

### 1. Import Modules

```python
import numpy as np
import pickle
import pbhstat
from pbhstat.power_spectrum import PowerSpectrum
from pbhstat.mass_variance import MassVariance
from pbhstat.collapse_stats import PressSchechterModel, PeaksTheoryModel, BroadPeakModel
from pbhstat.mass_function import MassFunction
from pbhstat.plot_utils import plot_power_spectrum, plot_mass_variance, plot_mass_function
```

### 2. Define Power Spectrum

**Custom log-normal example:**

```python
k_values = np.logspace(3, 7, 3000)
Ak = 0.008
Deltak = 1
kpeak = 1e5

P_k_custom = Ak * np.exp(-0.5 * (1/(np.sqrt(2 * np.pi) * Deltak)) * (np.log(k_values / kpeak) / Deltak)**2)

ps_custom = PowerSpectrum(
    shape='custom',
    k_values=k_values,
    P_k_values=P_k_custom
)
```

**Or load from file:**

```python
with open("path_to_k_array.pickle", "rb") as f:
    k_values = pickle.load(f)

with open("path_to_P_k_array.pickle", "rb") as f:
    P_k_custom = pickle.load(f)

ps_custom = PowerSpectrum(
    shape='custom',
    k_values=k_values,
    P_k_values=P_k_custom
)
```

**Alternatively, use a built-in piecewise spectrum, choose from 'piecewise', 'flat', 'lognormal' or 'delta':**

```python
k_values = np.logspace(3, 7, 3000)

ps_piecewise = PowerSpectrum(
    shape='piecewise',
    amplitude=0.008,
    k_star=1e5,
    ng=4,
    nd=2,
    k_values=k_values
)
```

### 3. Instantiate Mass Variance

**choose a window function from 'realtophat' or 'gaussian' and statistical method from 'press', 'peaks' or 'nonlinear':**

```python
mv_piecewise = MassVariance(
    window='realtophat',
    power_spectrum=ps_piecewise,
    statistics='nonlinear',
    cutoff=False
)
```

### 4. Evaluate Mass Function

**choose same statistical method as above and specify optional numerical coefficients:**

```python
mass_function = MassFunction(
    mass_variance=mv_piecewise,
    statistics='nonlinear',
    K=4,
    vcorr=True,
    gamma=0.36
)

mpbh, f_mpbh = mass_function.evaluate(k_values, mpbh_vals=50)
fpbh = mass_function.fpbh(f_mpbh, mpbh)
```

### 5. Plot Results

```python
plot_power_spectrum(k_values, ps_piecewise(k_values))

R_values = 1 / k_values
sigma0sq_piecewise = mv_piecewise.evaluate(k_values)
plot_mass_variance(R_values, sigma0sq_piecewise)

plot_mass_function(mpbh, f_mpbh, fpbh_val=fpbh)
```

## 📈 Plotting Constraints with PBHbounds

To overlay your calculated mass function with observational constraints, use the [PBHbounds](https://github.com/bradkav/PBHbounds/tree/master) repository.

**Save your mass function to the location of your PBHbounds directory:**

```python
from pbhstat.plot_utils import bounds_utility
bounds_utility(mpbh, f_mpbh, 'path_to_PBHbounds_directory')
```

Then run the modified script `PlotPBHbounds.py` from within that directory (available [here](https://github.com/pipcole/pbhstat)).

**Note:** Overlaying extended mass functions on monochromatic constraints is not consistent and should only be used as a guide for narrow mass functions. For consistent constraint conversion, see e.g. Bellomo et al. [arXiv:1709.07467](https://arxiv.org/abs/1709.07467).

## 📚 Reference

If you use this package, please cite the accompanying paper (reference to be added).