"""Main solver class for wave-vegetation interactions."""

import os
import logging
import numpy as np
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from .spatial import StaggeredGrid1D, initialize_wave
from .integration import WaveIntegrator
from .io import save_results


class WaveVegetationSolver:
    """1D Wave-vegetation interaction solver with physics-based approach."""
    
    def __init__(self, config: Dict, config_name: Optional[str] = None):
        """Initialize solver with configuration.
        
        Parameters:
        -----------
        config : dict
            Configuration parameters
        config_name : str, optional
            Name for the experiment
        """
        self.config = config
        
        # Extract key parameters
        self.L = config['domain_length']
        self.h = config['water_depth']
        self.H = config['wave_height']
        self.T = config['wave_period']
        self.g = config['gravity']
        
        # Set experiment name
        self.experiment_name = config_name if config_name else "wave_vegetation_sim"
        
        # Output directory
        current_dir = Path(__file__).parent.parent.parent
        self.output_dir = current_dir.parent / 'outputs' / self.experiment_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Create computational grid
        self.grid = StaggeredGrid1D(self.L, config['nx'])
        
        # Create vegetation arrays
        self.cf_array, self.cd_array = self.grid.create_vegetation_arrays(
            config['vegetation_zones']
        )
        
        # Sponge layer for wave absorption
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
        
        # Log setup information
        self._log_setup()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_file = self.output_dir / 'simulation.log'
        
        # Clear existing handlers
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
        self.logger.info(f"Initialized WaveVegetationSolver: {self.experiment_name}")
        self.logger.info(f"Domain: L={self.L}m, nx={self.config['nx']}, dx={self.grid.dx:.3f}m")
        self.logger.info(f"Wave: H={self.H}m, T={self.T}s, λ={self.config['wavelength']:.1f}m")
        self.logger.info(f"Water: h={self.h}m, ρ={self.config['water_density']}kg/m³")
        self.logger.info(f"Time: dt={self.config['dt']:.4f}s, CFL={self.config['computed_cfl']:.3f}")
        
        # Log wave characteristics
        c = np.sqrt(self.g * self.h)
        self.logger.info(f"Wave physics: c={c:.2f}m/s, ω={self.config['wave_angular_frequency']:.2f}rad/s")
        
        # Log vegetation zones
        self.logger.info(f"Vegetation zones: {len(self.config['vegetation_zones'])}")
        for i, (x_start, x_end, cf, cd) in enumerate(self.config['vegetation_zones']):
            self.logger.info(f"  Zone {i+1}: x=[{x_start:.1f},{x_end:.1f}]m, Cf={cf}, Cd={cd}m²/s")
            # Estimate damping
            beta = cf * self.config['wave_angular_frequency'] / 2
            self.logger.info(f"    Estimated damping coefficient: β={beta:.3f}/s")
    
    def run(self):
        """Run the wave-vegetation simulation."""
        self.logger.info("="*70)
        self.logger.info("WAVE-VEGETATION 1D SIMULATION v1.0.0")
        self.logger.info("="*70)
        
        start_time = time.time()
        
        try:
            # Phase 1: Initialization
            self.logger.info("\nPhase 1: Initialization")
            self.logger.info("-"*50)
            
            eta, u = initialize_wave(self.grid, self.config)
            self.logger.info("✓ Initialized fields (at rest)")
            self.logger.info(f"✓ Wave ramp period: {self.config.get('n_ramp_periods', 3)} periods")
            
            # Time discretization
            dt = self.config['dt']
            t_end = self.config['t_end']
            t = np.arange(0, t_end + dt, dt)
            nt = len(t)
            self.logger.info(f"✓ Time steps: {nt}, dt={dt:.4f}s, total time={t_end:.1f}s")
            
            # Storage arrays
            if self.config['save_netcdf']:
                stride = max(1, nt // 1000)  # Limit to ~1000 snapshots
                t_save = t[::stride]
                eta_history = np.zeros((len(t_save), self.grid.nx))
                u_history = np.zeros((len(t_save), self.grid.nx + 1))
                save_idx = 0
            
            # Energy tracking
            energy_history = {
                'time': [],
                'E_total': [],
                'E_potential': [],
                'E_kinetic': [],
                'D_friction': [],
                'D_viscous': [],
                'D_total': [],
                'Kt': [],
                'E_cumulative_dissipated': []
            }
            
            # Phase 2: Time Integration
            self.logger.info("\nPhase 2: Time Integration")
            self.logger.info("-"*50)
            
            last_progress = -1
            E_cumulative_dissipated = 0
            max_u_observed = 0
            
            for n in range(nt):
                # Progress reporting
                progress = int(100 * n / (nt - 1))
                if progress > last_progress and progress % 10 == 0:
                    elapsed = time.time() - start_time
                    if progress > 0:
                        eta_remaining = elapsed * (100 - progress) / progress
                        eta_str = self._format_time(eta_remaining)
                    else:
                        eta_str = "..."
                    
                    # Current wave height
                    H_current = np.max(eta) - np.min(eta)
                    u_max_current = np.max(np.abs(u))
                    max_u_observed = max(max_u_observed, u_max_current)
                    
                    self.logger.info(f"  {progress:3d}% | t={t[n]:6.2f}s | "
                                   f"H={H_current:.3f}m | |u|_max={u_max_current:.2f}m/s | "
                                   f"ETA: {eta_str}")
                    last_progress = progress
                
                # Time step
                eta, u = self.integrator.step(eta, u, t[n])
                
                # Check for numerical instability
                if np.any(np.isnan(eta)) or np.any(np.isnan(u)):
                    self.logger.error(f"NaN detected at t={t[n]:.2f}s")
                    self.logger.error(f"Max |u| before NaN: {max_u_observed:.2f}m/s")
                    raise RuntimeError("Numerical instability detected")
                
                # Save snapshots
                if self.config['save_netcdf'] and n % stride == 0:
                    eta_history[save_idx] = eta
                    u_history[save_idx] = u
                    save_idx += 1
                
                # Energy analysis
                if self.config['track_energy'] and n % 10 == 0:
                    energy = self.integrator.compute_energy(eta, u, t[n])
                    
                    if energy['E_reference'] is not None:
                        energy_history['time'].append(t[n])
                        energy_history['E_total'].append(energy['E_total'])
                        
                        # Separate potential and kinetic energy
                        E_pot = np.sum(0.5 * self.config['water_density'] * 
                                     self.g * np.clip(eta, -10, 10)**2) * self.grid.dx
                        E_kin = energy['E_total'] - E_pot
                        energy_history['E_potential'].append(E_pot)
                        energy_history['E_kinetic'].append(E_kin)
                        
                        # Dissipation rates
                        energy_history['D_friction'].append(
                            np.sum(energy['D_friction']) * self.grid.dx
                        )
                        energy_history['D_viscous'].append(
                            np.sum(energy['D_viscous']) * self.grid.dx
                        )
                        energy_history['D_total'].append(energy['D_total'])
                        
                        # Cumulative dissipation
                        if len(energy_history['time']) > 1:
                            dt_energy = energy_history['time'][-1] - energy_history['time'][-2]
                            E_cumulative_dissipated += energy['D_total'] * dt_energy
                        energy_history['E_cumulative_dissipated'].append(E_cumulative_dissipated)
                        
                        # Transmission coefficient
                        Kt = self.integrator.compute_transmission_coefficient(
                            eta, self.config['vegetation_zones'], t[n]
                        )
                        energy_history['Kt'].append(Kt)
            
            self.logger.info("✓ Integration completed successfully")
            self.logger.info(f"  Maximum velocity observed: {max_u_observed:.2f} m/s")
            
            # Phase 3: Analysis
            self.logger.info("\nPhase 3: Wave Analysis")
            self.logger.info("-"*50)
            
            # Final wave properties
            H_final = np.max(eta) - np.min(eta)
            Kt_final = self.integrator.compute_transmission_coefficient(
                eta, self.config['vegetation_zones'], t[-1]
            )
            
            self.logger.info(f"Incident wave height: {self.H:.3f}m")
            self.logger.info(f"Transmitted wave height: {H_final:.3f}m")
            self.logger.info(f"Transmission coefficient: Kt = {Kt_final:.3f}")
            self.logger.info(f"Wave height reduction: {100*(1-Kt_final):.1f}%")
            
            # Energy analysis
            if self.config['track_energy'] and len(energy_history['time']) > 0:
                E_initial = self.integrator.E_reference
                E_final = energy_history['E_total'][-1]
                E_dissipated = energy_history['E_cumulative_dissipated'][-1]
                
                self.logger.info(f"\nEnergy Balance:")
                self.logger.info(f"  Reference energy: {E_initial:.1f} J/m")
                self.logger.info(f"  Final energy: {E_final:.1f} J/m")
                self.logger.info(f"  Dissipated energy: {E_dissipated:.1f} J/m")
                
                # Energy conservation check
                balance_error = abs(E_initial - E_final - E_dissipated) / E_initial * 100
                self.logger.info(f"  Conservation error: {balance_error:.1f}%")
                
                # Dissipation breakdown
                total_friction = np.sum(energy_history['D_friction']) * dt
                total_viscous = np.sum(energy_history['D_viscous']) * dt
                self.logger.info(f"\nDissipation breakdown:")
                self.logger.info(f"  Friction (Cf): {100*total_friction/E_dissipated:.1f}%")
                self.logger.info(f"  Viscous (Cd): {100*total_viscous/E_dissipated:.1f}%")
            
            # Phase 4: Save Results
            self.logger.info("\nPhase 4: Saving Results")
            self.logger.info("-"*50)
            
            results = {
                'config': self.config,
                'grid': self.grid,
                'final_state': {'eta': eta, 'u': u, 't': t[-1]},
                'Kt': Kt_final
            }
            
            if self.config['save_netcdf']:
                results['history'] = {
                    't': t_save[:save_idx],
                    'eta': eta_history[:save_idx],
                    'u': u_history[:save_idx]
                }
            
            if self.config['track_energy']:
                results['energy'] = energy_history
            
            save_results(results, self.output_dir, self.logger)
            
            # Summary
            elapsed = time.time() - start_time
            self.logger.info("\n" + "="*70)
            self.logger.info("SIMULATION COMPLETE")
            self.logger.info("="*70)
            self.logger.info(f"Total time: {self._format_time(elapsed)}")
            self.logger.info(f"Output: {self.output_dir}")
            self.logger.info(f"Wave transmission: Kt = {Kt_final:.3f}")
            self.logger.info("="*70)
            
        except Exception as e:
            self.logger.error(f"\nError: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise
    
    def _format_time(self, seconds):
        """Format time in human-readable form."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}min"
        else:
            return f"{seconds/3600:.1f}hr"
