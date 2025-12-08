"""
Example: Using SANSFitter with Structure Factors

This script demonstrates how to:
1. Load SANS data
2. Set up a form factor model (sphere)
3. Apply a structure factor (hardsphere) for inter-particle interactions
4. Configure both form factor and structure factor parameters
5. Perform fitting with different radius_effective modes
6. Compare results with and without structure factors

Structure factors are essential for concentrated systems where inter-particle
interactions affect the scattering pattern.
"""

from sans_fitter import SANSFitter

# ============================================================================
# Part 1: Basic Structure Factor Usage
# ============================================================================

print("="*80)
print("Part 1: Basic Structure Factor Usage")
print("="*80)

# Initialize the fitter
fitter = SANSFitter()

# Load SANS data
fitter.load_data('simulated_sans_data.csv')

# Set up a sphere model (form factor)
fitter.set_model('sphere')

# Configure form factor parameters
fitter.set_param('radius', value=50, min=10, max=100, vary=True)
fitter.set_param('sld', value=4.0, vary=False)
fitter.set_param('sld_solvent', value=1.0, vary=False)
fitter.set_param('scale', value=0.01, min=0.001, max=1, vary=True)
fitter.set_param('background', value=0.001, min=0, max=0.1, vary=True)

# Display parameters before adding structure factor
print("\nParameters before structure factor:")
fitter.get_params()

# Apply hardsphere structure factor
fitter.set_structure_factor('hardsphere')

# Configure structure factor parameters
fitter.set_param('volfraction', value=0.2, min=0.0, max=0.6, vary=True)
fitter.set_param('radius_effective', value=50, min=10, max=100, vary=True)

# Display all parameters (form factor + structure factor)
print("\nParameters after adding hardsphere structure factor:")
fitter.get_params()

# Perform fit
print("\nFitting with hardsphere structure factor...")
result = fitter.fit(engine='bumps', method='amoeba')

# ============================================================================
# Part 2: Using link_radius Mode
# ============================================================================

print("\n" + "="*80)
print("Part 2: Using link_radius Mode")
print("="*80)

# Create a new fitter
fitter2 = SANSFitter()
fitter2.load_data('simulated_sans_data.csv')
fitter2.set_model('sphere')

# Set up form factor parameters
fitter2.set_param('radius', value=50, min=10, max=100, vary=True)
fitter2.set_param('sld', value=4.0, vary=False)
fitter2.set_param('sld_solvent', value=1.0, vary=False)
fitter2.set_param('scale', value=0.01, min=0.001, max=1, vary=True)
fitter2.set_param('background', value=0.001, min=0, max=0.1, vary=True)

# Apply hardsphere with linked radius
# In this mode, radius_effective is constrained to equal the form factor radius
fitter2.set_structure_factor('hardsphere', radius_effective_mode='link_radius')

# Configure structure factor parameters (note: radius_effective is linked)
fitter2.set_param('volfraction', value=0.2, min=0.0, max=0.6, vary=True)

# Display parameters - note radius_effective shows →radius
print("\nParameters with link_radius mode:")
fitter2.get_params()

# Demonstrate that changing radius updates radius_effective
print("\nChanging radius to 60.0...")
fitter2.set_param('radius', value=60.0)
print(f"radius_effective is now: {fitter2.params['radius_effective']['value']}")

# Perform fit
print("\nFitting with linked radius_effective...")
result2 = fitter2.fit(engine='bumps', method='amoeba')

# ============================================================================
# Part 3: Comparing Different Structure Factors
# ============================================================================

print("\n" + "="*80)
print("Part 3: Comparing Different Structure Factors")
print("="*80)

# Available structure factors:
# - hardsphere: Hard sphere structure factor (Percus-Yevick closure)
# - hayter_msa: Hayter-Penfold rescaled MSA for charged spheres
# - squarewell: Square well potential
# - stickyhardsphere: Sticky hard sphere (Baxter model)

# Example with hayter_msa (for charged particles)
fitter3 = SANSFitter()
fitter3.load_data('simulated_sans_data.csv')
fitter3.set_model('sphere')
fitter3.set_param('radius', value=50, min=10, max=100, vary=True)
fitter3.set_param('scale', value=0.01, min=0.001, max=1, vary=True)

# Apply hayter_msa structure factor
fitter3.set_structure_factor('hayter_msa')

# Configure structure factor parameters specific to hayter_msa
fitter3.set_param('volfraction', value=0.2, min=0.0, max=0.6, vary=True)
fitter3.set_param('radius_effective', value=50, min=10, max=100, vary=True)
fitter3.set_param('charge', value=10, min=0, max=100, vary=True)

print("\nParameters with hayter_msa structure factor:")
fitter3.get_params()

# ============================================================================
# Part 4: Removing a Structure Factor
# ============================================================================

print("\n" + "="*80)
print("Part 4: Removing a Structure Factor")
print("="*80)

# Check current structure factor
print(f"Current structure factor: {fitter3.get_structure_factor()}")

# Remove the structure factor
fitter3.remove_structure_factor()

# Verify it's removed
print(f"Structure factor after removal: {fitter3.get_structure_factor()}")

# Parameters are restored to form factor only
print("\nParameters after removing structure factor:")
fitter3.get_params()

# ============================================================================
# Part 5: Complete Workflow with Plotting
# ============================================================================

print("\n" + "="*80)
print("Part 5: Complete Workflow with Plotting")
print("="*80)

# Full workflow example
fitter_full = SANSFitter()
fitter_full.load_data('simulated_sans_data.csv')

# Set form factor
fitter_full.set_model('sphere')
fitter_full.set_param('radius', value=50, min=10, max=100, vary=True)
fitter_full.set_param('sld', value=4.0, vary=False)
fitter_full.set_param('sld_solvent', value=1.0, vary=False)
fitter_full.set_param('scale', value=0.01, min=0.001, max=1, vary=True)
fitter_full.set_param('background', value=0.001, min=0, max=0.1, vary=True)

# Apply structure factor
fitter_full.set_structure_factor('hardsphere')
fitter_full.set_param('volfraction', value=0.2, min=0.0, max=0.6, vary=True)
fitter_full.set_param('radius_effective', value=50, min=10, max=100, vary=True)

# Fit
result_full = fitter_full.fit(engine='bumps', method='amoeba')

# Plot results
print("\nGenerating plot...")
fitter_full.plot_results(show_residuals=True, log_scale=True)

# Save results
fitter_full.save_results('sphere_hardsphere_fit_results.csv')

print("\n✓ Structure factor example completed successfully!")
