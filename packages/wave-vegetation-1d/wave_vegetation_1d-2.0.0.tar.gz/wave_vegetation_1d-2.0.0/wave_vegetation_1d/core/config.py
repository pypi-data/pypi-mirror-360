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
                    
                    if key.startswith('vegetation_zone'):
                        parts = [float(x.strip()) for x in value.split(',')]
                        if len(parts) == 4:
                            config['vegetation_zones'].append(tuple(parts))
                        continue
                    
                    if key in ['nx', 'nt_per_period', 'n_periods', 'n_ramp_periods']:
                        config[key] = int(value)
                    elif key in ['domain_length', 'water_depth', 'dx', 'dt', 
                               'wave_height', 'wave_period', 'gravity',
                               'rtol', 'atol', 't_end', 'sponge_width',
                               'cfl_safety', 'max_velocity', 'water_density']:
                        config[key] = float(value)
                    elif key in ['save_netcdf', 'verbose', 'use_sponge_layer']:
                        config[key] = value.lower() in ['true', '1', 'yes', 'on']
                    else:
                        config[key] = value
                        
                except ValueError:
                    print(f"Warning: Error parsing line {line_num}: {line}")
                    continue
    
    defaults = {
        'gravity': 9.81,
        'water_density': 1025.0,
        'verbose': True,
        'save_netcdf': True,
        'use_sponge_layer': True,
        'sponge_width': 0.1,
        'cfl_safety': 0.25,  # Conservative for RK4
        'n_ramp_periods': 3,
        'max_velocity': 5.0,
    }
    
    for key, value in defaults.items():
        if key not in config:
            config[key] = value
    
    # Calculate derived parameters
    if 'dx' not in config and 'domain_length' in config and 'nx' in config:
        config['dx'] = config['domain_length'] / config['nx']
    
    if 'water_depth' in config and 'dx' in config:
        c_wave = np.sqrt(config['gravity'] * config['water_depth'])
        dt_cfl = config['cfl_safety'] * config['dx'] / c_wave
        
        if 'dt' in config:
            if config['dt'] > dt_cfl:
                print(f"Warning: Using CFL-limited dt={dt_cfl:.4f}s")
                config['dt'] = dt_cfl
        else:
            config['dt'] = dt_cfl
        
        config['computed_cfl'] = c_wave * config['dt'] / config['dx']
        
        if 'wave_period' in config:
            config['wave_angular_frequency'] = 2 * np.pi / config['wave_period']
            config['wavelength'] = c_wave * config['wave_period']
            config['wave_number'] = 2 * np.pi / config['wavelength']
    
    if 't_end' not in config and 'wave_period' in config and 'n_periods' in config:
        config['t_end'] = config['wave_period'] * config['n_periods']
    
    required = ['domain_length', 'water_depth', 'wave_height', 'wave_period', 'nx']
    missing = [p for p in required if p not in config]
    if missing:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")
    
    config['vegetation_zones'].sort(key=lambda x: x[0])
    
    return config
