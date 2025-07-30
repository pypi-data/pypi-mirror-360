"""I/O functions for saving simulation results."""

import numpy as np
import xarray as xr
from datetime import datetime
import logging
from pathlib import Path


def save_results(results: dict, output_dir: Path, logger: logging.Logger):
    """Save simulation results to NetCDF format.
    
    Parameters:
    -----------
    results : dict
        Dictionary containing all results
    output_dir : Path
        Output directory
    logger : Logger
        Logger instance
    """
    
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
            'title': 'Wave-Vegetation 1D Simulation',
            'institution': 'University of California, Riverside & ITB',
            'source': 'wave-vegetation-1d v1.0.0',
            'history': f'Created {datetime.now().isoformat()}',
            'references': 'https://github.com/sandyherho/wave-vegetation-1d',
            'comment': 'Physics-based simulation of wave attenuation through coastal vegetation',
            'authors': 'Sandy Herho and Iwan Anwar',
            'contact': 'sandy.herho@email.ucr.edu',
            'license': 'WTFPL',
            
            # Physical parameters
            'gravity': float(results['config']['gravity']),
            'water_density': float(results['config']['water_density']),
            'water_depth': float(results['config']['water_depth']),
            
            # Wave parameters
            'wave_height': float(results['config']['wave_height']),
            'wave_period': float(results['config']['wave_period']),
            'wavelength': float(results['config']['wavelength']),
            'wave_angular_frequency': float(results['config']['wave_angular_frequency']),
            
            # Domain parameters
            'domain_length': float(results['config']['domain_length']),
            'dx': float(results['grid'].dx),
            'dt': float(results['config']['dt']),
            'cfl_number': float(results['config']['computed_cfl']),
            
            # Results
            'transmission_coefficient': float(results['Kt']),
            'wave_height_reduction_percent': float(100 * (1 - results['Kt'])),
        })
        
        # Vegetation zone information
        for i, (x_start, x_end, cf, cd) in enumerate(results['config']['vegetation_zones']):
            ds.attrs[f'vegetation_zone_{i+1}'] = (
                f"x=[{x_start:.1f},{x_end:.1f}]m, Cf={cf}, Cd={cd}m²/s"
            )
            # Add estimated damping
            beta = cf * results['config']['wave_angular_frequency'] / 2
            ds.attrs[f'vegetation_zone_{i+1}_damping'] = f"β={beta:.3f}/s"
        
        # Energy data if available
        if 'energy' in results and results['energy']['time']:
            energy = results['energy']
            
            # Add energy variables
            ds_energy = xr.Dataset(
                {
                    'E_total': ('energy_time', np.array(energy['E_total']),
                               {'units': 'J/m', 'long_name': 'Total wave energy'}),
                    'E_potential': ('energy_time', np.array(energy['E_potential']),
                                   {'units': 'J/m', 'long_name': 'Potential energy'}),
                    'E_kinetic': ('energy_time', np.array(energy['E_kinetic']),
                                 {'units': 'J/m', 'long_name': 'Kinetic energy'}),
                    'D_friction': ('energy_time', np.array(energy['D_friction']),
                                  {'units': 'W/m', 'long_name': 'Friction dissipation rate'}),
                    'D_viscous': ('energy_time', np.array(energy['D_viscous']),
                                 {'units': 'W/m', 'long_name': 'Viscous dissipation rate'}),
                    'Kt': ('energy_time', np.array(energy['Kt']),
                          {'units': '-', 'long_name': 'Transmission coefficient'})
                },
                coords={
                    'energy_time': ('energy_time', np.array(energy['time']),
                                   {'units': 's', 'long_name': 'Time for energy data'})
                }
            )
            
            # Merge datasets
            ds = xr.merge([ds, ds_energy])
            
            # Add energy summary to attributes
            if len(energy['E_total']) > 0 and hasattr(results.get('integrator'), 'E_reference'):
                E_ref = results['integrator'].E_reference
                E_final = energy['E_total'][-1]
                E_diss = energy['E_cumulative_dissipated'][-1]
                
                ds.attrs['reference_energy_J_per_m'] = float(E_ref) if E_ref else 0
                ds.attrs['final_energy_J_per_m'] = float(E_final)
                ds.attrs['dissipated_energy_J_per_m'] = float(E_diss)
                ds.attrs['energy_conservation_error_percent'] = float(
                    100 * abs(E_ref - E_final - E_diss) / E_ref if E_ref else 0
                )
        
        # Add final state
        ds['eta_final'] = (['x'], results['final_state']['eta'],
                          {'units': 'm', 'long_name': 'Final water surface elevation'})
        ds['u_final'] = (['x_u'], results['final_state']['u'],
                        {'units': 'm/s', 'long_name': 'Final velocity'})
        
        # Save with compression
        encoding = {var: {'zlib': True, 'complevel': 4} for var in ds.data_vars}
        nc_file = output_dir / 'simulation.nc'
        ds.to_netcdf(nc_file, encoding=encoding)
        logger.info(f"✓ Saved: simulation.nc ({nc_file.stat().st_size/1024:.1f} KB)")
