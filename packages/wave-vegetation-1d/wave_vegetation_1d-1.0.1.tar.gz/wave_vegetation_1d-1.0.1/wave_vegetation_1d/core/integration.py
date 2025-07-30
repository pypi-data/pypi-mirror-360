"""Time integration for shallow water equations with vegetation."""

import numpy as np
from typing import Dict, Tuple
import logging


class WaveIntegrator:
    """Time integrator for 1D shallow water equations with vegetation effects."""
    
    def __init__(self, grid, config, cf_array, cd_array, sponge_array):
        """Initialize integrator with physics parameters.
        
        Parameters:
        -----------
        grid : StaggeredGrid1D
            Spatial grid
        config : dict
            Configuration parameters
        cf_array : ndarray
            Vegetation friction coefficients
        cd_array : ndarray
            Vegetation eddy viscosity
        sponge_array : ndarray
            Sponge layer damping
        """
        self.grid = grid
        self.config = config
        self.cf = cf_array
        self.cd = cd_array
        self.sponge = sponge_array
        
        # Physical parameters
        self.g = config['gravity']
        self.h0 = config['water_depth']
        self.rho = config['water_density']
        self.omega = config['wave_angular_frequency']
        
        # Wave parameters
        self.H = config['wave_height']
        self.T = config['wave_period']
        self.A = self.H / 2  # Wave amplitude
        
        # Time parameters
        self.dt = config['dt']
        self.n_ramp = int(config.get('n_ramp_periods', 3) * self.T / self.dt)
        
        # Velocity limiter for stability
        self.use_limiter = config.get('use_velocity_limiter', True)
        self.u_max = config.get('max_velocity', 5.0)
        
        # Mean water depth array
        self.h = np.full(grid.nx, self.h0)
        
        # Energy tracking arrays
        self.E_density = np.zeros(grid.nx)
        self.E_flux = np.zeros(grid.nx + 1)
        self.D_friction = np.zeros(grid.nx + 1)
        self.D_viscous = np.zeros(grid.nx + 1)
        
        # Reference energy (set after ramp period)
        self.E_reference = None
        self.E_reference_time = config.get('n_ramp_periods', 3) * self.T
        
        self.logger = logging.getLogger(__name__)
    
    def ramp_function(self, t: float) -> float:
        """Smooth ramp function for wave generation.
        
        Uses sin² envelope to avoid impulse start.
        
        Parameters:
        -----------
        t : float
            Current time [s]
            
        Returns:
        --------
        ramp : float
            Ramp value (0 to 1)
        """
        if t < self.n_ramp * self.dt:
            tau = t / (self.n_ramp * self.dt)
            return np.sin(0.5 * np.pi * tau)**2
        return 1.0
    
    def limit_velocity(self, u: np.ndarray) -> np.ndarray:
        """Apply velocity limiter to prevent numerical overflow.
        
        Uses smooth tanh limiting.
        
        Parameters:
        -----------
        u : ndarray
            Velocity field [m/s]
            
        Returns:
        --------
        u_limited : ndarray
            Limited velocity field
        """
        if self.use_limiter:
            u_limited = self.u_max * np.tanh(u / self.u_max)
            
            if np.any(np.abs(u) > 0.8 * self.u_max):
                max_u = np.max(np.abs(u))
                self.logger.debug(f"Velocity limited: max |u| = {max_u:.2f} m/s")
            
            return u_limited
        return u
    
    def step(self, eta: np.ndarray, u: np.ndarray, t: float) -> Tuple[np.ndarray, np.ndarray]:
        """Advance solution by one time step.
        
        Uses finite volume method with upwind flux.
        
        Parameters:
        -----------
        eta : ndarray
            Water surface elevation [m]
        u : ndarray
            Velocity [m/s]
        t : float
            Current time [s]
            
        Returns:
        --------
        eta_new : ndarray
            Updated elevation
        u_new : ndarray
            Updated velocity
        """
        dx = self.grid.dx
        dt = self.dt
        nx = self.grid.nx
        
        # Apply velocity limiter
        u = self.limit_velocity(u)
        
        # Step 1: Update water elevation (continuity equation)
        eta_new = np.copy(eta)
        
        # Total water depth (prevent negative depths)
        h_total = np.maximum(self.h + eta, 0.1)
        
        # Compute volume flux with upwind scheme
        q = np.zeros(nx + 1)
        for j in range(1, nx):
            if u[j] >= 0:
                h_face = h_total[j-1] if j > 0 else self.h0
            else:
                h_face = h_total[j] if j < nx else self.h0
            q[j] = h_face * u[j]
        
        # Update elevation (conservative form)
        for j in range(1, nx-1):
            flux_diff = q[j+1] - q[j]
            # Limit flux gradient for stability
            max_flux_diff = 0.5 * h_total[j] / dt
            flux_diff = np.clip(flux_diff, -max_flux_diff, max_flux_diff)
            eta_new[j] = eta[j] - dt/dx * flux_diff
        
        # Boundary conditions
        # Wave maker at x=0 (Dirichlet)
        ramp = self.ramp_function(t + dt)
        eta_new[0] = ramp * self.A * np.sin(self.omega * (t + dt))
        # Open boundary at x=L (Neumann)
        eta_new[-1] = eta_new[-2]
        
        # Apply sponge layer damping
        if self.config['use_sponge_layer']:
            damping = 1 / (1 + dt * self.sponge)
            eta_new = eta_new * damping
        
        # Step 2: Update velocity (momentum equation)
        u_new = np.copy(u)
        
        for j in range(1, nx):
            # Pressure gradient (barotropic)
            grad_eta = self.g * (eta_new[j] - eta_new[j-1]) / dx
            
            # Vegetation-induced eddy viscosity term
            if 1 < j < nx-1:
                u_laplacian = (u[j+1] - 2*u[j] + u[j-1]) / (dx**2)
                # Limit for stability
                u_laplacian = np.clip(u_laplacian, -1/dx, 1/dx)
                viscous = self.cd[j] * u_laplacian
            else:
                viscous = 0
            
            # Semi-implicit friction (stable for large Cf)
            friction_factor = 1 + self.cf[j] * self.omega * dt
            u_new[j] = (u[j] - dt * grad_eta + dt * viscous) / friction_factor
        
        # Boundary conditions
        u_new[0] = 0   # No flow through wave maker
        u_new[nx] = 0  # No flow at end
        
        # Apply velocity limiter again
        u_new = self.limit_velocity(u_new)
        
        return eta_new, u_new
    
    def compute_energy(self, eta: np.ndarray, u: np.ndarray, t: float) -> Dict[str, np.ndarray]:
        """Compute wave energy and dissipation rates.
        
        Parameters:
        -----------
        eta : ndarray
            Water surface elevation [m]
        u : ndarray
            Velocity [m/s]
        t : float
            Current time [s]
            
        Returns:
        --------
        energy_dict : dict
            Dictionary with energy components
        """
        g = self.g
        rho = self.rho
        
        # Limit values to prevent overflow
        eta_safe = np.clip(eta, -10, 10)
        u_safe = np.clip(u, -self.u_max, self.u_max)
        
        # Total water depth
        h_total = np.maximum(self.h0 + eta_safe, 0.1)
        
        # Potential energy density [J/m²]
        E_pot = 0.5 * rho * g * eta_safe**2
        
        # Kinetic energy density (interpolate u to cell centers)
        u_center = np.zeros(self.grid.nx)
        for j in range(self.grid.nx):
            u_center[j] = 0.5 * (u_safe[j] + u_safe[j+1])
        
        E_kin = 0.5 * rho * h_total * u_center**2
        self.E_density = E_pot + E_kin
        
        # Energy flux [W/m]
        for j in range(len(u_safe)):
            if j == 0:
                h_face = self.h0 + eta_safe[0]
            elif j == len(u_safe)-1:
                h_face = self.h0 + eta_safe[-1]
            else:
                h_face = self.h0 + 0.5 * (eta_safe[j-1] + eta_safe[j])
            
            h_face = np.maximum(h_face, 0.1)
            
            # Wave energy flux (simplified)
            self.E_flux[j] = u_safe[j] * rho * g * h_face * np.abs(eta_safe[min(j, len(eta_safe)-1)])
        
        # Dissipation rates
        for j in range(len(u_safe)):
            h_face = np.maximum(self.h0, 0.1)
            
            # Friction dissipation rate [W/m²]
            u_mag = np.minimum(np.abs(u_safe[j]), self.u_max)
            self.D_friction[j] = rho * h_face * self.cf[j] * self.omega * u_mag**3
        
        # Viscous dissipation rate
        for j in range(1, len(u_safe)-1):
            h_face = np.maximum(self.h0, 0.1)
            dudx = (u_safe[j+1] - u_safe[j-1]) / (2 * self.grid.dx)
            dudx = np.clip(dudx, -10, 10)
            self.D_viscous[j] = rho * h_face * self.cd[j] * dudx**2
        
        # Integrated quantities
        E_total = np.sum(self.E_density) * self.grid.dx
        D_total = np.sum(self.D_friction + self.D_viscous) * self.grid.dx
        
        # Set reference energy after ramp period
        if self.E_reference is None and t >= self.E_reference_time:
            self.E_reference = E_total
            self.logger.info(f"Set reference energy at t={t:.2f}s: {self.E_reference:.1f} J/m")
        
        return {
            'E_density': self.E_density.copy(),
            'E_flux': self.E_flux.copy(),
            'D_friction': self.D_friction.copy(),
            'D_viscous': self.D_viscous.copy(),
            'E_total': E_total,
            'D_total': D_total,
            'E_reference': self.E_reference if self.E_reference else E_total
        }
    
    def compute_transmission_coefficient(self, eta: np.ndarray, 
                                       vegetation_zones: list, t: float) -> float:
        """Compute wave transmission coefficient through vegetation.
        
        Kt = H_transmitted / H_incident
        
        Parameters:
        -----------
        eta : ndarray
            Water surface elevation [m]
        vegetation_zones : list
            List of vegetation zones
        t : float
            Current time [s]
            
        Returns:
        --------
        Kt : float
            Transmission coefficient (0-1)
        """
        if t < self.E_reference_time or not vegetation_zones:
            return 1.0
        
        # Find measurement locations
        first_veg_start = vegetation_zones[0][0]
        last_veg_end = vegetation_zones[-1][1]
        
        # Use one wavelength away from vegetation
        L_wave = self.config['wavelength']
        
        # Incident wave measurement region
        idx_before = (self.grid.x_eta > L_wave) & (self.grid.x_eta < first_veg_start - L_wave)
        if np.any(idx_before):
            # Wave height from surface elevation variance
            H_incident = 2 * np.sqrt(2) * np.std(eta[idx_before])
        else:
            H_incident = self.H
        
        # Transmitted wave measurement region
        idx_after = (self.grid.x_eta > last_veg_end + L_wave) & (self.grid.x_eta < self.grid.L - L_wave)
        if np.any(idx_after):
            H_transmitted = 2 * np.sqrt(2) * np.std(eta[idx_after])
        else:
            return 1.0
        
        Kt = H_transmitted / (H_incident + 1e-10)
        return np.clip(Kt, 0, 1)
