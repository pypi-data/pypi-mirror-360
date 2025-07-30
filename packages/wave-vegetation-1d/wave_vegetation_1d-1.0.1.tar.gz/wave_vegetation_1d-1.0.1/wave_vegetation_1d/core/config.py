"""Configuration parser with physics-based validation."""

import os
from typing import Dict, Any
import numpy as np


def parse_config(config_file: str) -> Dict[str, Any]:
    """Parse configuration file with stability validation."""
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    config = {
        'vegetation_zones': []
    }
    
    with open(config_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                if '#' in line:
                    line = line.split('#')[0].strip()
                
                try:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Handle vegetation zones
                    if key.startswith('vegetation_zone'):
                        parts = [float(x.strip()) for x in value.split(',')]
                        if len(parts) == 4:
                            config['vegetation_zones'].append(tuple(parts))
                        continue
                    
                    # Type conversion
                    if key in ['nx', 'nt_per_period', 'n_periods', 'n_ramp_periods']:
                        config[key] = int(value)
                    elif key in ['domain_length', 'water_depth', 'dx', 'dt', 
                               'wave_height', 'wave_period', 'gravity',
                               'rtol', 'atol', 't_end', 'sponge_width',
                               'cfl_safety', 'max_velocity', 'water_density']:
                        config[key] = float(value)
                    elif key in ['save_netcdf', 'verbose', 'track_energy', 
                               'use_sponge_layer', 'use_velocity_limiter']:
                        config[key] = value.lower() in ['true', '1', 'yes', 'on']
                    else:
                        config[key] = value
                        
                except ValueError as e:
                    print(f"Warning: Error parsing line {line_num}: {line}")
                    continue
    
    # Set physics-based defaults
    defaults = {
        'gravity': 9.81,              # g [m/s²]
        'water_density': 1025.0,      # ρ for seawater [kg/m³]
        'rtol': 1e-6,
        'atol': 1e-8,
        'verbose': True,
        'save_netcdf': True,
        'track_energy': True,
        'use_sponge_layer': True,
        'sponge_width': 0.1,
        'cfl_safety': 0.5,
        'n_ramp_periods': 3,
        'use_velocity_limiter': True,
        'max_velocity': 5.0,
    }
    
    for key, value in defaults.items():
        if key not in config:
            config[key] = value
    
    # Calculate derived parameters - FIXED ORDER
    # First calculate dx if not provided
    if 'dx' not in config and 'domain_length' in config and 'nx' in config:
        config['dx'] = config['domain_length'] / config['nx']
    
    # Then calculate stable time step using dx
    if 'water_depth' in config and 'dx' in config:
        # Wave celerity (phase speed) for shallow water
        c_wave = np.sqrt(config['gravity'] * config['water_depth'])
        # CFL-limited time step
        dt_cfl = config['cfl_safety'] * config['dx'] / c_wave
        
        if 'dt' in config:
            if config['dt'] > dt_cfl:
                print(f"Warning: Requested dt={config['dt']:.4f}s exceeds CFL limit {dt_cfl:.4f}s")
                print(f"Using CFL-limited dt={dt_cfl:.4f}s for stability")
                config['dt'] = dt_cfl
        else:
            config['dt'] = dt_cfl
        
        # Store computed CFL number
        config['computed_cfl'] = c_wave * config['dt'] / config['dx']
        
        # Wave parameters
        if 'wave_period' in config:
            config['wave_angular_frequency'] = 2 * np.pi / config['wave_period']
            # Linear dispersion relation for shallow water
            config['wavelength'] = c_wave * config['wave_period']
            config['wave_number'] = 2 * np.pi / config['wavelength']
    
    # Compute simulation time
    if 't_end' not in config and 'wave_period' in config and 'n_periods' in config:
        config['t_end'] = config['wave_period'] * config['n_periods']
    
    # Validate required parameters
    required = ['domain_length', 'water_depth', 'wave_height', 'wave_period', 'nx']
    missing = [p for p in required if p not in config]
    if missing:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")
    
    # Stability and physics checks
    _validate_physics(config)
    
    # Sort vegetation zones by position
    config['vegetation_zones'].sort(key=lambda x: x[0])
    
    return config


def _validate_physics(config: dict):
    """Validate parameters for physical and numerical stability."""
    
    # Check CFL condition
    if 'computed_cfl' in config and config['computed_cfl'] > 0.8:
        print(f"Warning: CFL number {config['computed_cfl']:.3f} is high. Consider smaller dt.")
    
    # Check wavelength resolution
    if 'wavelength' in config and 'dx' in config:
        points_per_wavelength = config['wavelength'] / config['dx']
        if points_per_wavelength < 20:
            print(f"Warning: Only {points_per_wavelength:.1f} points per wavelength.")
            print("Consider finer spatial resolution (smaller dx).")
    
    # Check shallow water assumption
    if 'wavelength' in config and 'water_depth' in config:
        depth_to_wavelength = config['water_depth'] / config['wavelength']
        if depth_to_wavelength > 0.5:
            print(f"Note: h/λ = {depth_to_wavelength:.2f}. Deep water effects may be important.")
    
    # Check vegetation parameters
    for i, (x_start, x_end, cf, cd) in enumerate(config['vegetation_zones']):
        # Typical ranges for coastal vegetation
        if cf > 1.0:
            print(f"Warning: Zone {i+1} has high friction Cf={cf}.")
            print("Typical values: mangroves (0.1-0.5), marshes (0.2-0.8)")
        if cd > 0.5:
            print(f"Warning: Zone {i+1} has high eddy viscosity Cd={cd} m²/s.")
            print("Typical values: 0.01-0.3 m²/s for coastal vegetation")
