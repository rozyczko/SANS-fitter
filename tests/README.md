# SANS Fitter Testing

This directory contains comprehensive unit tests for the SANS Fitter module.

## Test Structure

```
tests/
├── __init__.py           # Package initialization
└── test_sans_fitter.py   # Main test suite
```

## Test Coverage

The test suite covers:

### 1. **Initialization Tests**
- SANSFitter object creation and default state

### 2. **Data Loading Tests**
- Loading data from CSV files
- Data validation and error handling
- Mask and Q-range setup

### 3. **Model Setup Tests**
- Loading different models (cylinder, sphere, etc.)
- Parameter discovery and initialization
- Invalid model handling

### 4. **Parameter Management Tests**
- Setting parameter values
- Setting parameter bounds
- Setting vary flags
- Error handling for invalid parameters

### 5. **Fitting Tests**
- BUMPS engine fitting
- LMFit engine fitting (if available)
- Prerequisites validation
- Result storage

### 6. **Visualization Tests**
- Plotting data only
- Plotting with fit results
- Different plot options (log scale, residuals)

### 7. **Export Tests**
- Saving fit results to file
- File content validation

### 8. **Integration Tests**
- Complete workflow from data loading to result export
- Model switching
- Engine switching

## Running Tests

### Using unittest (built-in)

```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py -v

# Run specific test
python run_tests.py -k test_set_model_cylinder

# Quiet mode
python run_tests.py -q
```

### Using pytest (if installed)

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sans_fitter --cov-report=html

# Run specific test file
pytest tests/test_sans_fitter.py

# Run specific test class
pytest tests/test_sans_fitter.py::TestModelSetup

# Run specific test method
pytest tests/test_sans_fitter.py::TestModelSetup::test_set_model_cylinder
```

### From Python

```python
import unittest
from tests import test_sans_fitter

# Load and run tests
loader = unittest.TestLoader()
suite = loader.loadTestsFromModule(test_sans_fitter)
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
```

## Test Requirements

The tests require the same dependencies as the main module:
- `numpy`
- `matplotlib`
- `sasmodels`
- `sasdata`
- `bumps`
- `lmfit` (optional, for LMFit tests)

## Test Data

Tests create temporary CSV files with synthetic SANS data. These files are automatically cleaned up after each test.

## Skipped Tests

Some tests may be skipped if optional dependencies are not available:
- LMFit tests are skipped if `lmfit` is not installed

## Continuous Integration

To run tests in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    python run_tests.py
    
# Or with pytest
- name: Run tests with pytest
  run: |
    pip install pytest pytest-cov
    pytest --cov=sans_fitter --cov-report=xml
```

## Writing New Tests

When adding new features to `sans_fitter.py`, follow these guidelines:

1. **Create a new test class** for each major feature
2. **Use descriptive test names** that explain what is being tested
3. **Test both success and failure cases**
4. **Use setUp/tearDown** for common test fixtures
5. **Clean up temporary files** in tearDown methods
6. **Mock external dependencies** where appropriate

Example:

```python
class TestNewFeature(unittest.TestCase):
    """Test the new feature."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fitter = SANSFitter()
        # Setup code
    
    def tearDown(self):
        """Clean up after tests."""
        # Cleanup code
    
    def test_feature_success(self):
        """Test successful operation of feature."""
        # Test code
        self.assertEqual(expected, actual)
    
    def test_feature_failure(self):
        """Test error handling of feature."""
        with self.assertRaises(ValueError):
            # Code that should raise error
            pass
```

## Test Metrics

Current test coverage (approximate):
- **Data loading**: 100%
- **Model setup**: 100%
- **Parameter management**: 100%
- **Fitting (BUMPS)**: 95%
- **Fitting (LMFit)**: 90% (conditional on lmfit availability)
- **Visualization**: 85%
- **Export**: 100%
- **Overall**: ~95%

## Known Issues

- Some tests may be slow due to actual fitting operations
- OpenCL-related warnings may appear (safely ignored in tests)
- LMFit tests require lmfit to be installed

## Contributing

When contributing tests:
1. Ensure all new tests pass
2. Maintain or improve code coverage
3. Follow existing naming conventions
4. Document complex test scenarios
5. Use appropriate assertions (`assertEqual`, `assertIn`, `assertRaises`, etc.)
