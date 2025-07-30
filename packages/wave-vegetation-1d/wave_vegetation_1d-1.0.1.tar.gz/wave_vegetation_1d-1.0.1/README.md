# Wave-Vegetation-1D: Physics-Based Wave Attenuation Model

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/wave-vegetation-1d.svg)](https://badge.fury.io/py/wave-vegetation-1d)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A numerically stable Python package for simulating 1D wave propagation through vegetated coastal areas with physics-based energy dissipation.

## Features

- **Coastal engineering focus** with vegetation effects on waves
- **Physics-based approach** using shallow water equations
- **Energy conservation** with dissipation tracking
- **Stable numerical scheme** with automatic CFL control
- **Oceanographic applications** for coastal protection studies

## Installation

```bash
pip install wave-vegetation-1d
```

## Quick Start

### Command Line Usage

```bash
# Run a simulation with provided configuration
wave-veg-1d configs/mangrove_forest.txt
```

### Python API

```python
from wave_vegetation_1d import WaveVegetationSolver, parse_config

# Load configuration
config = parse_config('configs/mangrove_forest.txt')

# Run simulation
solver = WaveVegetationSolver(config)
solver.run()
```

## Physical Model

The solver implements the 1D shallow water equations with vegetation-induced dissipation:

**Continuity Equation:**
∂η/∂t + ∂(hu)/∂x = 0

**Momentum Equation:**
∂u/∂t + g∂η/∂x + C_f·ω·u - C_d·∂²u/∂x² = 0

Where:
- η: water surface elevation [m]
- u: depth-averaged velocity [m/s]
- h: water depth [m]
- g: gravitational acceleration (9.81 m/s²)
- C_f: vegetation friction coefficient [-]
- C_d: vegetation-induced eddy viscosity [m²/s]
- ω: wave angular frequency (2π/T) [rad/s]

## Oceanographic Applications

This model simulates wave attenuation in various coastal vegetation types:

| Vegetation Type | C_f Range | C_d Range [m²/s] | Typical Attenuation |
|----------------|-----------|------------------|-------------------|
| Mangrove forests | 0.1-0.5 | 0.05-0.2 | 30-60% |
| Salt marshes | 0.2-0.8 | 0.1-0.3 | 40-70% |
| Seagrass beds | 0.05-0.3 | 0.01-0.1 | 10-40% |
| Kelp forests | 0.1-0.4 | 0.05-0.15 | 20-50% |

## Configuration

Create a configuration file (e.g., `my_simulation.txt`):

```ini
# Wave Conditions
wave_height = 0.1          # Wave height [m]
wave_period = 2.5          # Wave period [s]

# Water Properties
water_depth = 1.5          # Water depth [m]
water_density = 1025.0     # Seawater density [kg/m³]

# Domain
domain_length = 60.0       # Domain length [m]
nx = 600                   # Number of grid points

# Time Integration
n_periods = 30             # Number of wave periods to simulate

# Vegetation Zone (x_start, x_end, Cf, Cd)
vegetation_zone1 = 20.0, 35.0, 0.3, 0.1
```

## Output

Results are saved to `outputs/experiment_name/`:
- `simulation.nc` - Complete spacetime data in NetCDF format
- `simulation.log` - Detailed simulation log with energy analysis

Key outputs include:
- Wave height reduction through vegetation
- Transmission coefficient (Kt)
- Energy dissipation rates
- Phase lag and wave setup

## Example Results

For a typical mangrove forest (Cf=0.3, Cd=0.1):
- Input wave height: 0.1 m
- Transmitted wave height: ~0.06 m
- Transmission coefficient: Kt ≈ 0.6
- Wave height reduction: ~40%

## Citation

If you use this package in your research, please cite:

```bibtex
@software{wave_vegetation_1d_2025,
  title = {Wave-Vegetation-1D: Physics-Based Wave Attenuation Model},
  author = {Herho, S and Anwar, I},
  year = {2025},
  version = {1.0.1},
  url = {https://github.com/sandyherho/wave-veg-1d}
}
```

## Authors

- **Sandy Herho** - University of California, Riverside (sandy.herho@email.ucr.edu)
- **Iwan Anwar** - Institut Teknologi Bandung (iwanpanwar@itb.ac.id)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Links

- [GitHub Repository](https://github.com/sandyherho/wave-veg-1d)
- [Issue Tracker](https://github.com/sandyherho/wave-veg-1d/issues)
- [PyPI Package](https://pypi.org/project/wave-veg-1d/)
