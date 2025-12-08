# SANS Model Fitter

A flexible, model-agnostic Python template for fitting Small-Angle Neutron Scattering (SANS) data using the SasModels library.

## Features

- **Model-Agnostic Design**: Works with any model from the SasModels library (cylinder, sphere, core_shell, etc.)
- **Multiple Fitting Engines**: Supports both BUMPS (default) and LMFit optimization engines
- **Flexible Data Loading**: Reads CSV, XML, and HDF5 formats via sasdata
- **User-Friendly Parameter Management**: Easy-to-use interface for setting parameter values, bounds, and fitting flags
- **Comprehensive Visualization**: Automatic plotting of data, fitted model, and residuals
- **Result Export**: Save fitted parameters and curves to CSV files

## Installation

### Option 1: Using pip (recommended for users)

```bash
# Clone the repository
git clone https://github.com/rozyczko/SANS-fitter.git
cd SANS-fitter

# Install the package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Option 2: Using Pixi (recommended for development)

```bash
# Clone the repository
git clone https://github.com/rozyczko/SANS-fitter.git
cd SANS-fitter

# Install dependencies with Pixi
pixi install

# Run tests
pixi run test

# Run demo notebook
pixi run run-demo
```

## Quick Start

```python
from sans_fitter import SANSFitter

# Create fitter instance
fitter = SANSFitter()

# Load your data
fitter.load_data('my_sans_data.csv')

# Set the model (any model from SasModels!)
fitter.set_model('cylinder')

# View initial parameter values
fitter.get_params()

# Configure parameters for fitting
fitter.set_param('radius', value=20, min=1, max=100, vary=True)
fitter.set_param('length', value=400, min=10, max=1000, vary=True)
fitter.set_param('scale', value=0.1, min=0, max=1, vary=True)
fitter.set_param('background', value=0.01, min=0, max=1, vary=True)

# View current parameters
fitter.get_params()

# Perform the fit (using BUMPS by default)
result = fitter.fit(engine='bumps', method='amoeba')

# Visualize results
fitter.plot_results(show_residuals=True)

# Save results
fitter.save_results('fit_results.csv')
```

## Switching Models

The fitter is completely model-agnostic. Simply load a different model:

```python
# Try with a sphere model instead
fitter.set_model('sphere')
fitter.get_params()  # See different parameters!

fitter.set_param('radius', value=25, min=5, max=100, vary=True)
result = fitter.fit()
```

## Switching Fitting Engines

```python
# Use BUMPS (default)
result = fitter.fit(engine='bumps', method='amoeba')

# Or use LMFit
result = fitter.fit(engine='lmfit', method='leastsq')
```

### Available Methods

**BUMPS methods:**
- `'amoeba'` - Nelder-Mead simplex (default, robust)
- `'lm'` - Levenberg-Marquardt
- `'newton'` - Newton's method
- `'de'` - Differential evolution

**LMFit methods:**
- `'leastsq'` - Levenberg-Marquardt (default)
- `'least_squares'` - Trust Region Reflective
- `'differential_evolution'` - Global optimizer
- `'powell'`, `'nelder'`, etc.

## Class Reference

### `SANSFitter`

#### Methods

**`load_data(filename: str)`**
- Load SANS data from file (CSV, XML, HDF5)

**`set_model(model_name: str, platform: str = 'cpu')`**
- Load a model from SasModels library
- Examples: 'cylinder', 'sphere', 'core_shell_sphere', 'ellipsoid'

**`get_params()`**
- Display current parameter values and settings

**`set_param(name, value=None, min=None, max=None, vary=None)`**
- Configure a model parameter
- `name`: Parameter name
- `value`: Initial value
- `min`, `max`: Bounds for fitting
- `vary`: Boolean, whether to fit this parameter

**`fit(engine='bumps', method=None, **kwargs)`**
- Perform the fit
- Returns dictionary with chi-squared and fitted parameters

**`plot_results(show_residuals=True, log_scale=True)`**
- Visualize experimental data vs fitted model

**`save_results(filename: str)`**
- Export fit results to CSV file

## Demo Notebook

See [sans_fitter_demo.ipynb](sans_fitter_demo.ipynb) for a comprehensive demonstration with examples.

## File Structure

```
.
├── sans_fitter.py           # Main SANSFitter class
├── sans_fitter_demo.ipynb   # Demonstration notebook
├── sasmodels-basic.ipynb    # Original experimental notebook
├── simulated_sans_data.csv  # Example data file
└── README.md                # This file
```

## Design Philosophy

This implementation follows a **template pattern** where:

1. The core fitting logic is abstracted into a reusable class
2. Models are loaded dynamically from SasModels - no hardcoded model assumptions
3. Parameters are discovered automatically from the model definition
4. Multiple optimization engines are supported through a unified interface
5. The user maintains full control over parameter initialization and bounds

## Implementation Details

### Engine Adapters

The fitter implements adapter patterns for both BUMPS and LMFit:

- **BUMPS**: Uses native `sasmodels.bumps_model` integration
- **LMFit**: Uses `sasmodels.direct_model.DirectModel` with a custom residual function

### Parameter Management

Parameters are stored internally with:
- `value`: Current/initial value
- `min`, `max`: Bounds
- `vary`: Fitting flag
- `description`: From model metadata

This allows the fitter to work with any model without prior knowledge of its parameters.

## License

BSD 3-Clause License

Copyright (c) 2025, SANS-fitter contributors
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## References

- SasModels: https://github.com/SasView/sasmodels
- BUMPS: https://github.com/bumps/bumps
- LMFit: https://lmfit.github.io/lmfit-py/
