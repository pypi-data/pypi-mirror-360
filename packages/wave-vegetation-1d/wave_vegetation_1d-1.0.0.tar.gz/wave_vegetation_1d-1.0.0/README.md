# Wave-Vegetation-1D: Physics-Based Wave Attenuation Model

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/sandyherho/wave-veg-1d)

A numerically stable Python package for simulating 1D wave propagation through vegetated coastal areas with physics-based energy dissipation.

## Features

- **Coastal engineering focus** with vegetation effects on waves
- **Physics-based approach** using shallow water equations
- **Energy conservation** with dissipation tracking
- **Stable numerical scheme** with automatic CFL control
- **Oceanographic applications** for coastal protection studies

## Physical Model

The solver implements the 1D shallow water equations with vegetation-induced dissipation:

- Continuity Equation

$\frac{\partial \eta}{\partial t}  + \frac{\partial (hu)}{\partial x}= 0$

- Momentum Equation

$\frac{\partial u}{ \partial t} + g \frac{\partial \eta}{\partial x} + C_f \omega u - C_d \frac{\partial^2 u}{\partial x^2}$


Where:
- $\eta$: water surface elevation [m]
- $u$: depth-averaged velocity [m/s]
- $h$: water depth [m]
- $g$: gravitational acceleration (9.81 m/s $^2$)
- $C_f$: vegetation friction coefficient [-]
- $C_d$: vegetation-induced eddy viscosity [m $^2$ /s]
- $\omega$: wave angular frequency ($\frac{2\pi}{T}$) [rad/s]

Energy dissipation mechanisms:
- Friction dissipation rate [W/m $^2$ ]: 

$D_f = \rho C_f h \omega |u|^3$

- Viscous dissipation rate [W/m $^2$ ]: 

$D_d = \rho h C_d (\partial u/ \partial x)^2$


## Oceanographic Context

This model simulates wave attenuation in:
- **Mangrove forests**: $C_f = 0.1-0.5$, $C_d = 0.05-0.2$
- **Salt marshes**: $C_f = 0.2-0.8$, $C_d = 0.1-0.3$
- **Seagrass beds**: $C_f = 0.05-0.3$, $C_d = 0.01-0.1$
- **Kelp forests**: $C_f = 0.1-0.4$, $C_d = 0.05-0.15$

## Installation

### From PyPI (coming soon)
```bash
pip install wave-vegetation-1d
```

### From source
```bash
git clone https://github.com/sandyherho/wave-vegetation-1d.git
cd wave-vegetation-1d
pip install -e .
```

### Dependencies

- Python $\geq$ 3.8
- NumPy $\geq$ 1.20
- SciPy $\geq$ 1.7
- pandas $\geq$ 1.3
- xarray $\geq$ 0.19
- netCDF4 $\geq$ 1.5

## Usage

### Command Line

```bash
# Run test cases
wave-veg-1d configs/mangrove_forest.txt
wave-veg-1d configs/salt_marsh.txt
wave-veg-1d configs/multiple_vegetation.txt
```

### Python API

```python
from wave_vegetation_1d import WaveVegetationSolver, parse_config

config = parse_config('configs/mangrove_forest.txt')
solver = WaveVegetationSolver(config)
solver.run()
```

## Output

Results saved to `../outputs/experiment_name/`:
- `simulation.nc` - Complete simulation data (NetCDF format)
- `simulation.log` - Detailed run log with physics analysis

Key outputs:
- Wave height reduction through vegetation
- Transmission coefficient $(K_t)$
- Energy dissipation rates
- Phase lag and wave setup

## Physics Parameters

- **Wave height $(H)$**: Typical 0.1-2.0 m for coastal areas
- **Wave period $(T)$**: 2-10 s for wind waves
- **Water depth $(h)$**: 0.5-5.0 m (shallow water)
- **Vegetation density**: Represented by $C_f$ and $C_d$ values

## Authors

- Sandy Herho \<sandy.herho@email.ucr.edu\>
- Iwan Anwar \<iwanpanwar@itb.ac.id\>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

```bibtex
@software{wave_vegetation_1d_2025,
  title = {Wave-Vegetation-1D: Physics-Based Wave Attenuation Model},
  author = {Herho, Sandy and Anwar, Iwan},
  year = {2025},
  version = {1.0.0},
  url = {https://github.com/sandyherho/wave-vegetation-1d}
}
```
