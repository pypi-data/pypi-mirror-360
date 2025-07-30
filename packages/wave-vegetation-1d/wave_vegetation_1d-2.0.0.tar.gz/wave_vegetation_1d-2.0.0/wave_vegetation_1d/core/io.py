"""Simplified I/O for eta and u fields only."""

import numpy as np
import xarray as xr
from datetime import datetime
import logging
from pathlib import Path


def save_results(results: dict, output_dir: Path, logger: logging.Logger):
    """Save only eta and u fields to NetCDF."""
    
    if 'history' in results and results['config']['save_netcdf']:
        # Create xarray dataset
        ds = xr.Dataset(
            {
                'eta': (['time', 'x'], results['history']['eta'],
                       {'units': 'm', 'long_name': 'Water surface elevation'}),
                'u': (['time', 'x_u'], results['history']['u'],
                     {'units': 'm/s', 'long_name': 'Depth-averaged velocity'})
            },
            coords={
                'time': ('time', results['history']['t'], 
                        {'units': 's', 'long_name': 'Time'}),
                'x': ('x', results['grid'].x_eta,
                     {'units': 'm', 'long_name': 'Position (eta points)'}),
                'x_u': ('x_u', results['grid'].x_u,
                        {'units': 'm', 'long_name': 'Position (u points)'})
            }
        )
        
        # Global attributes
        ds.attrs.update({
            'title': 'Wave-Vegetation 1D High-Accuracy Simulation',
            'solver': '4th-order Runge-Kutta with TVD spatial discretization',
            'version': '2.0.0',
            'created': datetime.now().isoformat(),
            
            # Physical parameters
            'gravity': float(results['config']['gravity']),
            'water_density': float(results['config']['water_density']),
            'water_depth': float(results['config']['water_depth']),
            
            # Wave parameters
            'wave_height': float(results['config']['wave_height']),
            'wave_period': float(results['config']['wave_period']),
            'wavelength': float(results['config']['wavelength']),
            
            # Domain parameters
            'domain_length': float(results['config']['domain_length']),
            'dx': float(results['grid'].dx),
            'dt': float(results['config']['dt']),
            'cfl_number': float(results['config']['computed_cfl']),
            
            # Results
            'transmission_coefficient': float(results['Kt']),
            'wave_height_reduction_percent': float(100 * (1 - results['Kt'])),
        })
        
        # Vegetation zones
        for i, (x_start, x_end, cf, cd) in enumerate(results['config']['vegetation_zones']):
            ds.attrs[f'vegetation_zone_{i+1}'] = f"x=[{x_start:.1f},{x_end:.1f}]m, Cf={cf}, Cd={cd}m²/s"
        
        # Save with compression
        encoding = {var: {'zlib': True, 'complevel': 4} for var in ds.data_vars}
        nc_file = output_dir / 'simulation.nc'
        ds.to_netcdf(nc_file, encoding=encoding)
        logger.info(f"✓ Saved: simulation.nc ({nc_file.stat().st_size/1024:.1f} KB)")
