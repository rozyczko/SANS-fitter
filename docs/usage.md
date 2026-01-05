# User Guide

This guide provides detailed instructions on how to use SANS Fitter for your data analysis.

## Basic Workflow

The typical workflow involves:
1.  Loading data
2.  Selecting a model
3.  Configuring parameters
4.  Fitting
5.  Visualizing and saving results

### 1. Loading Data

Use `load_data` to import your SANS data. The fitter supports various formats including CSV, XML (CanSAS), and HDF5 (NXcanSAS) via the `sasdata` library.

```python
from sans_fitter import SANSFitter

fitter = SANSFitter()
fitter.load_data('path/to/data.csv')
```

### 2. Selecting a Model

You can use any model available in the [SasModels library](https://www.sasview.org/docs/user/models/index.html).

```python
# Load a cylinder model
fitter.set_model('cylinder')

# Or a sphere model
fitter.set_model('sphere')
```

### 3. Configuring Parameters

Once a model is loaded, you can inspect and modify its parameters.

```python
# View all parameters
fitter.get_params()

# Set parameter values and bounds
fitter.set_param('radius', value=20, min=10, max=50, vary=True)
fitter.set_param('length', value=400, vary=False)  # Fix this parameter
```

-   `value`: The initial guess for the parameter.
-   `min` / `max`: The lower and upper bounds for the fit.
-   `vary`: Set to `True` to fit this parameter, `False` to keep it fixed.

### 4. Fitting

SANS Fitter supports two fitting engines: **BUMPS** and **LMFit**.

#### Using BUMPS (Default)

BUMPS is robust and offers several optimization methods.

```python
# Default method (Nelder-Mead simplex)
result = fitter.fit(engine='bumps', method='amoeba')

# Differential Evolution
result = fitter.fit(engine='bumps', method='de')
```

#### Using LMFit

LMFit provides access to SciPy's optimization algorithms.

```python
# Levenberg-Marquardt
result = fitter.fit(engine='lmfit', method='leastsq')
```

### 5. Visualization and Export

After fitting, you can plot the results and save them.

```python
# Plot data, fit, and residuals
fitter.plot_results(show_residuals=True, log_scale=True)

# Save results to CSV
fitter.save_results('fit_results.csv')
```

## Advanced Usage

### Structure Factors

You can combine a form factor with a structure factor to model interacting systems.

```python
fitter.set_model('sphere')
fitter.set_structure_factor('hardsphere')
```

Supported structure factors include:
-   `hardsphere`
-   `hayter_msa`
-   `squarewell`
-   `stickyhardsphere`

### Effective Radius

When using a structure factor, you often need to define an effective radius. You can link this to the form factor's radius.

```python
# Link effective radius to the sphere radius
fitter.set_structure_factor('hardsphere', radius_effective_mode='link_radius')
```
