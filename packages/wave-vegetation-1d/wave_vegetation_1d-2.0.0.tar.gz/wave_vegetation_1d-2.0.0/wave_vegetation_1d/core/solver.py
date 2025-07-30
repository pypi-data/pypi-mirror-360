"""High-accuracy solver for wave-vegetation interactions."""

import logging
import numpy as np
import time
from pathlib import Path
from typing import Dict, Optional

from .spatial import StaggeredGrid1D, initialize_wave
from .integration import WaveIntegrator
from .io import save_results


class WaveVegetationSolver:
    """1D Wave-vegetation solver with 4th-order accuracy."""
    
    def __init__(self, config: Dict, config_name: Optional[str] = None):
        """Initialize solver with configuration."""
        self.config = config
        
        # Extract key parameters
        self.L = config['domain_length']
        self.h = config['water_depth']
        self.H = config['wave_height']
        self.T = config['wave_period']
        self.g = config['gravity']
        
        # Set experiment name
        self.experiment_name = config_name if config_name else "wave_veg_sim"
        
        # Output directory - save OUTSIDE the package directory
        current_dir = Path(__file__).parent.parent.parent  # wave-vegetation-1d/
        self.output_dir = current_dir.parent / 'wave_veg_outputs' / self.experiment_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Create computational grid
        self.grid = StaggeredGrid1D(self.L, config['nx'])
        
        # Create vegetation arrays
        self.cf_array, self.cd_array = self.grid.create_vegetation_arrays(
            config['vegetation_zones']
        )
        
        # Sponge layer
        if config['use_sponge_layer']:
            self.sponge_array = self.grid.create_sponge_layer(
                config.get('sponge_width', 0.1)
            )
        else:
            self.sponge_array = np.zeros(self.grid.nx)
        
        # Initialize time integrator
        self.integrator = WaveIntegrator(
            self.grid, config, self.cf_array, self.cd_array, self.sponge_array
        )
        
        self._log_setup()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_file = self.output_dir / 'simulation.log'
        
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        logging.basicConfig(
            level=logging.INFO if self.config.get('verbose', True) else logging.WARNING,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _log_setup(self):
        """Log simulation setup information."""
        self.logger.info("="*70)
        self.logger.info("HIGH-ACCURACY WAVE-VEGETATION SOLVER v2.0.0")
        self.logger.info("4th-order Runge-Kutta + TVD spatial discretization")
        self.logger.info("="*70)
        self.logger.info(f"Domain: L={self.L}m, nx={self.config['nx']}, dx={self.grid.dx:.3f}m")
        self.logger.info(f"Wave: H={self.H}m, T={self.T}s, λ={self.config['wavelength']:.1f}m")
        self.logger.info(f"Water: h={self.h}m, ρ={self.config['water_density']}kg/m³")
        self.logger.info(f"Time: dt={self.config['dt']:.4f}s, CFL={self.config['computed_cfl']:.3f}")
        self.logger.info(f"Output: {self.output_dir}")
        
        for i, (x_start, x_end, cf, cd) in enumerate(self.config['vegetation_zones']):
            self.logger.info(f"Vegetation {i+1}: x=[{x_start:.1f},{x_end:.1f}]m, Cf={cf}, Cd={cd}m²/s")
    
    def run(self):
        """Run the high-accuracy simulation."""
        start_time = time.time()
        
        try:
            # Initialize fields
            eta, u = initialize_wave(self.grid, self.config)
            
            # Time discretization
            dt = self.config['dt']
            t_end = self.config['t_end']
            t = np.arange(0, t_end + dt, dt)
            nt = len(t)
            
            self.logger.info(f"Time steps: {nt}, Simulation time: {t_end:.1f}s")
            self.logger.info("-"*70)
            
            # Storage for output
            if self.config['save_netcdf']:
                stride = max(1, nt // 500)  # Save ~500 snapshots
                t_save = t[::stride]
                eta_history = np.zeros((len(t_save), self.grid.nx))
                u_history = np.zeros((len(t_save), self.grid.nx + 1))
                save_idx = 0
            
            # Time integration loop
            last_progress = -1
            
            for n in range(nt):
                # Progress reporting
                progress = int(100 * n / (nt - 1))
                if progress > last_progress and progress % 10 == 0:
                    elapsed = time.time() - start_time
                    if progress > 0:
                        eta_remaining = elapsed * (100 - progress) / progress
                        eta_str = f"{eta_remaining:.1f}s"
                    else:
                        eta_str = "..."
                    
                    H_current = np.max(eta) - np.min(eta)
                    u_max = np.max(np.abs(u))
                    
                    self.logger.info(f"Progress: {progress:3d}% | t={t[n]:6.2f}s | "
                                   f"H={H_current:.3f}m | u_max={u_max:.2f}m/s | ETA: {eta_str}")
                    last_progress = progress
                
                # RK4 time step
                eta, u = self.integrator.step(eta, u, t[n])
                
                # Check stability
                if np.any(np.isnan(eta)) or np.any(np.isnan(u)):
                    self.logger.error(f"NaN detected at t={t[n]:.2f}s")
                    raise RuntimeError("Numerical instability")
                
                # Save snapshots
                if self.config['save_netcdf'] and n % stride == 0:
                    eta_history[save_idx] = eta
                    u_history[save_idx] = u
                    save_idx += 1
            
            # Compute final wave properties
            wave_props = self.integrator.compute_wave_properties(
                eta, self.config['vegetation_zones']
            )
            
            self.logger.info("-"*70)
            self.logger.info("SIMULATION RESULTS")
            self.logger.info("-"*70)
            self.logger.info(f"Incident wave height: {wave_props['H_incident']:.3f}m")
            self.logger.info(f"Transmitted wave height: {wave_props['H_transmitted']:.3f}m")
            self.logger.info(f"Transmission coefficient: Kt = {wave_props['Kt']:.3f}")
            self.logger.info(f"Wave height reduction: {100*(1-wave_props['Kt']):.1f}%")
            
            # Save results
            results = {
                'config': self.config,
                'grid': self.grid,
                'final_state': {'eta': eta, 'u': u, 't': t[-1]},
                'Kt': wave_props['Kt']
            }
            
            if self.config['save_netcdf']:
                results['history'] = {
                    't': t_save[:save_idx],
                    'eta': eta_history[:save_idx],
                    'u': u_history[:save_idx]
                }
            
            save_results(results, self.output_dir, self.logger)
            
            elapsed = time.time() - start_time
            self.logger.info("-"*70)
            self.logger.info(f"Total time: {elapsed:.1f}s")
            self.logger.info(f"Output saved to: {self.output_dir}")
            self.logger.info("="*70)
            
        except Exception as e:
            self.logger.error(f"\nError: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise
