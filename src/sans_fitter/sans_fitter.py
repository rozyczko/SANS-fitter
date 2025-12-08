"""
SANS Model Fitter - A flexible template for fitting SANS data with SasModels

This module provides a unified interface for fitting SANS data using different
optimization engines (BUMPS, LMFit) with any model from the SasModels library.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Dict, Any, Literal
import warnings
import os

# SasModels and SasData imports
from sasmodels.core import load_model
from sasmodels.bumps_model import Model as BumpsModel, Experiment
from sasmodels.direct_model import DirectModel, call_kernel
from sasdata.dataloader.loader import Loader

# Fitting engine imports
from bumps.names import FitProblem
from bumps.fitters import fit as bumps_fit
from bumps.formatnum import format_uncertainty

try:
    from scipy.optimize import leastsq, least_squares, differential_evolution
    LMFIT_AVAILABLE = True
except ImportError:
    LMFIT_AVAILABLE = False
    warnings.warn("scipy not available. Only bumps engine will work.")


class SANSFitter:
    """
    A flexible SANS model fitter that works with any SasModels model.
    
    Features:
    - Loads data from various file formats (CSV, XML, HDF5)
    - Model-agnostic: works with any model from SasModels library
    - Supports multiple fitting engines (BUMPS, LMFit)
    - User-friendly parameter management
    
    Example:
        >>> fitter = SANSFitter()
        >>> fitter.load_data('my_sans_data.csv')
        >>> fitter.set_model('cylinder')
        >>> fitter.set_param('radius', value=20, min=1, max=100)
        >>> fitter.set_param('length', value=400, min=10, max=1000)
        >>> result = fitter.fit(engine='bumps')
        >>> fitter.plot_results()
    """
    
    def __init__(self):
        """Initialize the SANS fitter."""
        self.data = None
        self.kernel = None
        self.model_name = None
        self.params = {}
        self.fit_result = None
        self._fitted_model = None
        
    def load_data(self, filename: str) -> None:
        """
        Load SANS data from a file.
        
        Supports CSV, XML, and HDF5 formats through sasdata.
        
        Args:
            filename: Path to the data file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the data cannot be loaded or is invalid
        """
        loader = Loader()
        try:
            data_list = loader.load(filename)
            if not data_list:
                raise ValueError(f"No data loaded from {filename}")
            
            self.data = data_list[0]
            
            # Setup required fields for sasmodels
            self.data.qmin = getattr(self.data, 'qmin', None) or self.data.x.min()
            self.data.qmax = getattr(self.data, 'qmax', None) or self.data.x.max()
            self.data.mask = np.isnan(self.data.y)
            
            print(f"✓ Loaded data from {filename}")
            print(f"  Q range: {self.data.qmin:.4f} to {self.data.qmax:.4f} Å⁻¹")
            print(f"  Data points: {len(self.data.x)}")
            
        except Exception as e:
            raise ValueError(f"Failed to load data from {filename}: {str(e)}")
    
    def set_model(self, model_name: str, platform: str = 'cpu') -> None:
        """
        Set the SANS model to use for fitting.
        
        Args:
            model_name: Name of the model from SasModels (e.g., 'cylinder', 'sphere')
            platform: Computation platform ('cpu' or 'opencl')
            
        Raises:
            ValueError: If the model name is not valid
        """
        try:
            # Force CPU platform to avoid OpenCL issues
            self.kernel = load_model(model_name, dtype='single', platform='dll')
            self.model_name = model_name
            
            # Initialize parameters with default values from the model
            self.params = {}
            for param in self.kernel.info.parameters.kernel_parameters:
                self.params[param.name] = {
                    'value': param.default,
                    'min': param.limits[0] if param.limits[0] > -np.inf else 0,
                    'max': param.limits[1] if param.limits[1] < np.inf else param.default * 10,
                    'vary': False,  # By default, parameters are fixed
                    'description': param.description
                }
            
            # Add implicit scale and background parameters (present in all models)
            # These are not in kernel_parameters but are always available
            if 'scale' not in self.params:
                self.params['scale'] = {
                    'value': 1.0,
                    'min': 0.0,
                    'max': np.inf,
                    'vary': False,
                    'description': 'Scale factor for the model intensity'
                }
            
            if 'background' not in self.params:
                self.params['background'] = {
                    'value': 0.0,
                    'min': 0.0,
                    'max': np.inf,
                    'vary': False,
                    'description': 'Constant background level'
                }
            
            print(f"✓ Model '{model_name}' loaded successfully")
            print(f"  Available parameters: {len(self.params)}")
            
        except Exception as e:
            raise ValueError(f"Failed to load model '{model_name}': {str(e)}")
    
    def get_params(self) -> None:
        """Display current parameter values and settings in a readable format."""
        if not self.params:
            print("No model loaded. Use set_model() first.")
            return
        
        print(f"\n{'='*80}")
        print(f"Model: {self.model_name}")
        print(f"{'='*80}")
        print(f"{'Parameter':<20} {'Value':<12} {'Min':<12} {'Max':<12} {'Vary':<8}")
        print(f"{'-'*80}")
        
        for name, info in self.params.items():
            vary_str = "✓" if info['vary'] else "✗"
            print(f"{name:<20} {info['value']:<12.4g} {info['min']:<12.4g} "
                  f"{info['max']:<12.4g} {vary_str:<8}")
        print(f"{'='*80}\n")
    
    def set_param(self, name: str, value: Optional[float] = None, 
                  min: Optional[float] = None, max: Optional[float] = None, 
                  vary: Optional[bool] = None) -> None:
        """
        Configure a model parameter for fitting.
        
        Args:
            name: Parameter name
            value: Initial value (optional)
            min: Minimum bound (optional)
            max: Maximum bound (optional)
            vary: Whether to vary during fit (optional)
            
        Raises:
            KeyError: If parameter name doesn't exist for the current model
        """
        if name not in self.params:
            available = ', '.join(self.params.keys())
            raise KeyError(f"Parameter '{name}' not found. Available: {available}")
        
        if value is not None:
            self.params[name]['value'] = value
        if min is not None:
            self.params[name]['min'] = min
        if max is not None:
            self.params[name]['max'] = max
        if vary is not None:
            self.params[name]['vary'] = vary
    
    def fit(self, engine: Literal['bumps', 'lmfit'] = 'bumps', 
            method: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Perform the fit using the specified engine.
        
        Args:
            engine: Fitting engine ('bumps' or 'lmfit')
            method: Optimization method (engine-specific)
                   - BUMPS: 'amoeba', 'lm', 'newton', 'de' (default: 'amoeba')
                   - LMFit: 'leastsq', 'least_squares', 'differential_evolution', etc.
            **kwargs: Additional arguments passed to the fitting engine
            
        Returns:
            Dictionary with fit results including chi-squared and parameter values
            
        Raises:
            ValueError: If data or model not loaded, or invalid engine
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        if self.kernel is None:
            raise ValueError("No model loaded. Use set_model() first.")
        
        if engine == 'bumps':
            return self._fit_bumps(method or 'amoeba', **kwargs)
        elif engine == 'lmfit':
            if not LMFIT_AVAILABLE:
                raise ValueError("scipy is not installed. Use 'bumps' engine or install scipy.")
            return self._fit_lmfit(method or 'leastsq', **kwargs)
        else:
            raise ValueError(f"Unknown engine '{engine}'. Use 'bumps' or 'lmfit'.")
    
    def _fit_bumps(self, method: str = 'amoeba', **kwargs) -> Dict[str, Any]:
        """Fit using BUMPS engine."""
        # Prepare parameter dictionary for BumpsModel
        pars = {name: info['value'] for name, info in self.params.items()}
        
        # Create BUMPS model
        model = BumpsModel(self.kernel, **pars)
        
        # Set parameter ranges for fitting
        for name, info in self.params.items():
            if info['vary']:
                param_obj = getattr(model, name)
                param_obj.range(info['min'], info['max'])
        
        # Create experiment and fit problem
        experiment = Experiment(data=self.data, model=model)
        problem = FitProblem(experiment)
        
        print(f"\nInitial χ² = {problem.chisq():.4f}")
        print(f"Fitting with BUMPS (method: {method})...")
        
        # Perform fit
        result = bumps_fit(problem, method=method, **kwargs)
        
        # Store results
        self.fit_result = {
            'engine': 'bumps',
            'method': method,
            'chisq': problem.chisq(),
            'parameters': {},
            'problem': problem,
            'result': result
        }
        
        # Extract fitted parameters
        for k, v, dv in zip(problem.labels(), result.x, result.dx):
            self.fit_result['parameters'][k] = {
                'value': v,
                'stderr': dv,
                'formatted': format_uncertainty(v, dv)
            }
            # Update internal parameter values
            if k in self.params:
                self.params[k]['value'] = v
        
        self._fitted_model = problem
        
        # Print results
        print(f"\n✓ Fit completed!")
        print(f"Final χ² = {self.fit_result['chisq']:.4f}")
        print(f"\nFitted parameters:")
        for name, info in self.fit_result['parameters'].items():
            print(f"  {name}: {info['formatted']}")
        
        return self.fit_result
    
    def _fit_lmfit(self, method: str = 'leastsq', **kwargs) -> Dict[str, Any]:
        """Fit using scipy.optimize (leastsq/least_squares) engine."""
        # Get initial parameter values and build bounds
        param_names = [name for name, info in self.params.items() if info['vary']]
        x0 = np.array([self.params[name]['value'] for name in param_names])
        bounds_lower = np.array([self.params[name]['min'] for name in param_names])
        bounds_upper = np.array([self.params[name]['max'] for name in param_names])
        
        # Create direct model calculator (kernel already set to CPU in set_model)
        calculator = DirectModel(self.data, self.kernel)
        
        # Define residual function
        def residual(x):
            # Build full parameter dictionary
            par_dict = {name: info['value'] for name, info in self.params.items()}
            # Update with fitted parameters
            for i, name in enumerate(param_names):
                par_dict[name] = x[i]
            # Calculate model
            I_calc = calculator(**par_dict)
            # Return weighted residuals
            return (self.data.y - I_calc) / self.data.dy
        
        print(f"\nFitting with scipy.optimize (method: {method})...")
        
        # Perform fit based on method
        if method == 'leastsq':
            # Levenberg-Marquardt (no bounds support)
            result = leastsq(residual, x0, full_output=True, **kwargs)
            fitted_params = result[0]
            cov_matrix = result[1]
            info_dict = result[2]
            
            # Calculate parameter errors from covariance matrix
            if cov_matrix is not None:
                param_errors = np.sqrt(np.diag(cov_matrix))
            else:
                param_errors = np.zeros_like(fitted_params)
            
            # Calculate chi-squared
            final_residuals = residual(fitted_params)
            chisq = np.sum(final_residuals**2)
            
        elif method == 'least_squares':
            # Trust Region Reflective (supports bounds)
            bounds = (bounds_lower, bounds_upper)
            result = least_squares(residual, x0, bounds=bounds, **kwargs)
            fitted_params = result.x
            
            # Estimate parameter errors from Jacobian
            try:
                # Compute covariance from Jacobian
                J = result.jac
                cov_matrix = np.linalg.inv(J.T @ J)
                param_errors = np.sqrt(np.diag(cov_matrix))
            except:
                param_errors = np.zeros_like(fitted_params)
            
            chisq = np.sum(result.fun**2)
            
        elif method == 'differential_evolution':
            # Global optimizer (supports bounds)
            bounds_list = list(zip(bounds_lower, bounds_upper))
            
            def objective(x):
                return np.sum(residual(x)**2)
            
            result = differential_evolution(objective, bounds_list, **kwargs)
            fitted_params = result.x
            param_errors = np.zeros_like(fitted_params)  # DE doesn't provide errors
            chisq = result.fun
            
        else:
            raise ValueError(f"Unknown method '{method}'. Use 'leastsq', 'least_squares', or 'differential_evolution'.")
        
        # Store results
        self.fit_result = {
            'engine': 'lmfit',
            'method': method,
            'chisq': chisq,
            'parameters': {},
            'result': result
        }
        
        # Extract fitted parameters
        for i, name in enumerate(param_names):
            self.fit_result['parameters'][name] = {
                'value': fitted_params[i],
                'stderr': param_errors[i],
                'formatted': f"{fitted_params[i]:.6g} ± {param_errors[i]:.6g}" if param_errors[i] > 0 else f"{fitted_params[i]:.6g}"
            }
            # Update internal parameter values
            self.params[name]['value'] = fitted_params[i]
        
        # Add fixed parameters to results
        for name, info in self.params.items():
            if name not in param_names:
                self.fit_result['parameters'][name] = {
                    'value': info['value'],
                    'stderr': 0.0,
                    'formatted': f"{info['value']:.6g} (fixed)"
                }
        
        self._fitted_model = result
        
        # Print results
        print(f"\n✓ Fit completed!")
        print(f"Final χ² = {self.fit_result['chisq']:.4f}")
        print(f"\nFitted parameters:")
        for name, info in self.fit_result['parameters'].items():
            print(f"  {name}: {info['formatted']}")
        
        return self.fit_result
    
    def plot_results(self, show_residuals: bool = True, log_scale: bool = True) -> None:
        """
        Plot experimental data and fitted model.
        
        Args:
            show_residuals: If True, show residuals in a separate panel
            log_scale: If True, use log scale for both axes
        """
        if self.data is None:
            raise ValueError("No data to plot. Use load_data() first.")
        
        if self.fit_result is None:
            print("No fit results available. Plotting data only.")
            plt.figure(figsize=(10, 6))
            plt.errorbar(self.data.x, self.data.y, yerr=self.data.dy, 
                        fmt='o', label='Data', alpha=0.6)
            plt.xlabel('Q (Å⁻¹)')
            plt.ylabel('I(Q)')
            plt.title(f'SANS Data')
            if log_scale:
                plt.xscale('log')
                plt.yscale('log')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            return
        
        # Calculate fitted curve
        if self.fit_result['engine'] == 'bumps':
            problem = self._fitted_model
            q = self.data.x
            I_fit = problem.fitness.theory()
        else:  # lmfit
            calculator = DirectModel(self.data, self.kernel)
            par_dict = {name: info['value'] for name, info in self.fit_result['parameters'].items()}
            I_fit = calculator(**par_dict)
            q = self.data.x
        
        residuals = (self.data.y - I_fit) / self.data.dy
        
        # Create plot
        if show_residuals:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), 
                                          gridspec_kw={'height_ratios': [3, 1]})
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=(10, 6))
        
        # Main plot
        ax1.errorbar(self.data.x, self.data.y, yerr=self.data.dy, 
                    fmt='o', label='Experimental Data', alpha=0.6, markersize=4)
        ax1.plot(q, I_fit, 'r-', label='Fitted Model', linewidth=2)
        ax1.set_xlabel('Q (Å⁻¹)', fontsize=12)
        ax1.set_ylabel('I(Q)', fontsize=12)
        ax1.set_title(f'SANS Fit: {self.model_name} (χ² = {self.fit_result["chisq"]:.4f})', 
                     fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        if log_scale:
            ax1.set_xscale('log')
            ax1.set_yscale('log')
        
        # Residuals plot
        if show_residuals:
            ax2.axhline(0, color='gray', linestyle='--', linewidth=1)
            ax2.plot(self.data.x, residuals, 'o', markersize=4, alpha=0.6)
            ax2.set_xlabel('Q (Å⁻¹)', fontsize=12)
            ax2.set_ylabel('Residuals (σ)', fontsize=12)
            ax2.grid(True, alpha=0.3)
            if log_scale:
                ax2.set_xscale('log')
        
        plt.tight_layout()
        plt.show()
    
    def save_results(self, filename: str) -> None:
        """
        Save fit results to a file.
        
        Args:
            filename: Output file path (CSV format)
        """
        if self.fit_result is None:
            raise ValueError("No fit results to save. Run fit() first.")
        
        # Prepare data
        with open(filename, 'w') as f:
            f.write(f"# SANS Fit Results\n")
            f.write(f"# Model: {self.model_name}\n")
            f.write(f"# Engine: {self.fit_result['engine']}\n")
            f.write(f"# Method: {self.fit_result['method']}\n")
            f.write(f"# Chi-squared: {self.fit_result['chisq']:.6f}\n")
            f.write(f"#\n")
            f.write(f"# Fitted Parameters:\n")
            for name, info in self.fit_result['parameters'].items():
                f.write(f"# {name}: {info['formatted']}\n")
            f.write(f"#\n")
            f.write(f"Q,I_exp,dI_exp,I_fit,Residuals\n")
            
            # Get fitted curve
            if self.fit_result['engine'] == 'bumps':
                I_fit = self._fitted_model.fitness.theory()
            else:
                calculator = DirectModel(self.data, self.kernel)
                par_dict = {name: info['value'] for name, info in self.fit_result['parameters'].items()}
                I_fit = calculator(**par_dict)
            
            residuals = (self.data.y - I_fit) / self.data.dy
            
            for q, i_exp, di_exp, i_fit, res in zip(self.data.x, self.data.y, 
                                                      self.data.dy, I_fit, residuals):
                f.write(f"{q:.6e},{i_exp:.6e},{di_exp:.6e},{i_fit:.6e},{res:.6e}\n")
        
        print(f"✓ Results saved to {filename}")
