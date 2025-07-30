# Wave-Vegetation-1D v2.0: High-Accuracy Numerical Solver

A numerically stable Python package for simulating 1D wave propagation through vegetated coastal areas using 4th-order Runge-Kutta time integration and high-order spatial discretization.

## Features

- **4th-order Runge-Kutta** time integration for temporal accuracy
- **4th-order spatial discretization** with TVD flux limiters
- **Optimized for accuracy** in coastal wave modeling
- **Robust numerical stability** with adaptive CFL control

## Installation

```bash
pip install -e .
```

## Usage

```bash
wave-veg-1d configs/mangrove_forest.txt
```

Results are saved to `../wave_veg_outputs/` (outside the package directory).

## Configuration

Create a configuration file with wave conditions, water properties, domain settings, and vegetation zones:

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

## Authors

- **Sandy Herho** - University of California, Riverside
- **Iwan Anwar** - Institut Teknologi Bandung

## License

MIT License - see LICENSE.txt for details.
