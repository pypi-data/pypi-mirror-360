"""4th-order Runge-Kutta time integration with high-order spatial discretization."""

import numpy as np
from typing import Dict, Tuple
import logging


class WaveIntegrator:
    """High-accuracy time integrator for shallow water equations."""
    
    def __init__(self, grid, config, cf_array, cd_array, sponge_array):
        """Initialize integrator with physics parameters."""
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
        self.A = self.H / 2
        
        # Time parameters
        self.dt = config['dt']
        self.n_ramp = int(config.get('n_ramp_periods', 3) * self.T / self.dt)
        
        # Maximum velocity for limiting
        self.u_max = config.get('max_velocity', 5.0)
        
        # Precompute coefficients
        self.dx = grid.dx
        self.nx = grid.nx
        
        # RK4 coefficients
        self.rk4_c = [0.0, 0.5, 0.5, 1.0]
        self.rk4_b = [1.0/6.0, 1.0/3.0, 1.0/3.0, 1.0/6.0]
        
        self.logger = logging.getLogger(__name__)
    
    def ramp_function(self, t: float) -> float:
        """Smooth ramp function using tanh for C∞ smoothness."""
        if t < self.n_ramp * self.dt:
            tau = t / (self.n_ramp * self.dt)
            return 0.5 * (1 + np.tanh(5 * (tau - 0.5)))
        return 1.0
    
    def minmod(self, a: float, b: float) -> float:
        """Minmod limiter for TVD scheme."""
        if a * b <= 0:
            return 0.0
        return a if abs(a) < abs(b) else b
    
    def compute_limited_gradient(self, phi: np.ndarray, i: int) -> float:
        """Compute slope-limited gradient using minmod limiter."""
        if 0 < i < len(phi) - 1:
            dphi_minus = phi[i] - phi[i-1]
            dphi_plus = phi[i+1] - phi[i]
            return self.minmod(dphi_minus, dphi_plus) / self.dx
        return 0.0
    
    def compute_flux(self, eta: np.ndarray, u: np.ndarray) -> np.ndarray:
        """Compute high-order numerical flux with MUSCL reconstruction."""
        nx = self.nx
        flux = np.zeros(nx + 1)
        h_total = np.maximum(self.h0 + eta, 0.01)
        
        # Interior fluxes with MUSCL-TVD scheme
        for j in range(1, nx):
            # Left and right states with limited reconstruction
            if j > 1:
                h_L = h_total[j-1] + 0.5 * self.compute_limited_gradient(h_total, j-1)
            else:
                h_L = h_total[j-1]
                
            if j < nx - 1:
                h_R = h_total[j] - 0.5 * self.compute_limited_gradient(h_total, j)
            else:
                h_R = h_total[j]
            
            # Upwind flux
            if u[j] >= 0:
                flux[j] = h_L * u[j]
            else:
                flux[j] = h_R * u[j]
        
        return flux
    
    def compute_derivatives(self, eta: np.ndarray, u: np.ndarray, t: float) -> Tuple[np.ndarray, np.ndarray]:
        """Compute spatial derivatives for RK4 stage."""
        nx = self.nx
        dx = self.dx
        
        # Initialize derivatives
        deta_dt = np.zeros(nx)
        du_dt = np.zeros(nx + 1)
        
        # Compute volume flux
        flux = self.compute_flux(eta, u)
        
        # Update elevation (continuity equation)
        for j in range(1, nx-1):
            deta_dt[j] = -(flux[j+1] - flux[j]) / dx
        
        # Boundary conditions for eta
        deta_dt[0] = 0  # Will be set by BC
        deta_dt[-1] = 0  # Neumann BC
        
        # Update velocity (momentum equation)
        for j in range(1, nx):
            # 4th-order pressure gradient (when possible)
            if 1 < j < nx - 1:
                grad_eta = self.g * (-eta[j-2] + 8*eta[j-1] - 8*eta[j] + eta[j+1]) / (12*dx)
            else:
                grad_eta = self.g * (eta[j] - eta[j-1]) / dx
            
            # 4th-order viscous term
            if 2 < j < nx - 2:
                u_xx = (-u[j-2] + 16*u[j-1] - 30*u[j] + 16*u[j+1] - u[j+2]) / (12*dx**2)
            elif 1 < j < nx - 1:
                u_xx = (u[j+1] - 2*u[j] + u[j-1]) / dx**2
            else:
                u_xx = 0
            
            viscous = self.cd[j] * u_xx
            
            # Friction term
            friction = -self.cf[j] * self.omega * u[j]
            
            du_dt[j] = -grad_eta + viscous + friction
        
        # Apply sponge damping
        if self.config['use_sponge_layer']:
            for j in range(nx):
                deta_dt[j] -= self.sponge[j] * eta[j]
        
        return deta_dt, du_dt
    
    def rk4_stage(self, eta: np.ndarray, u: np.ndarray, t: float, dt: float,
                  k_eta: np.ndarray, k_u: np.ndarray, stage: int) -> Tuple[np.ndarray, np.ndarray]:
        """Compute one stage of RK4."""
        c = self.rk4_c[stage]
        
        # Intermediate values
        eta_stage = eta + c * dt * k_eta
        u_stage = u + c * dt * k_u
        
        # Apply velocity limiter
        u_stage = self.u_max * np.tanh(u_stage / self.u_max)
        
        # Compute derivatives at intermediate time
        return self.compute_derivatives(eta_stage, u_stage, t + c * dt)
    
    def step(self, eta: np.ndarray, u: np.ndarray, t: float) -> Tuple[np.ndarray, np.ndarray]:
        """Advance solution using 4th-order Runge-Kutta."""
        dt = self.dt
        
        # RK4 stages
        k1_eta, k1_u = self.compute_derivatives(eta, u, t)
        k2_eta, k2_u = self.rk4_stage(eta, u, t, dt, k1_eta, k1_u, 1)
        k3_eta, k3_u = self.rk4_stage(eta, u, t, dt, k2_eta, k2_u, 2)
        k4_eta, k4_u = self.rk4_stage(eta, u, t, dt, k3_eta, k3_u, 3)
        
        # Combine stages
        eta_new = eta + dt * (self.rk4_b[0]*k1_eta + self.rk4_b[1]*k2_eta + 
                              self.rk4_b[2]*k3_eta + self.rk4_b[3]*k4_eta)
        u_new = u + dt * (self.rk4_b[0]*k1_u + self.rk4_b[1]*k2_u + 
                         self.rk4_b[2]*k3_u + self.rk4_b[3]*k4_u)
        
        # Apply boundary conditions
        ramp = self.ramp_function(t + dt)
        eta_new[0] = ramp * self.A * np.sin(self.omega * (t + dt))
        eta_new[-1] = eta_new[-2]  # Neumann
        
        u_new[0] = 0   # No flow at boundary
        u_new[-1] = 0  # No flow at end
        
        # Final velocity limiting
        u_new = self.u_max * np.tanh(u_new / self.u_max)
        
        return eta_new, u_new
    
    def compute_wave_properties(self, eta: np.ndarray, vegetation_zones: list) -> Dict[str, float]:
        """Compute wave transmission coefficient."""
        if not vegetation_zones:
            return {'Kt': 1.0, 'H_incident': self.H, 'H_transmitted': self.H}
        
        # Find measurement regions
        first_veg_start = vegetation_zones[0][0]
        last_veg_end = vegetation_zones[-1][1]
        L_wave = self.config['wavelength']
        
        # Incident wave region
        idx_before = (self.grid.x_eta > L_wave) & (self.grid.x_eta < first_veg_start - L_wave)
        if np.any(idx_before):
            H_incident = 2 * np.sqrt(2) * np.std(eta[idx_before])
        else:
            H_incident = self.H
        
        # Transmitted wave region
        idx_after = (self.grid.x_eta > last_veg_end + L_wave) & (self.grid.x_eta < self.grid.L - L_wave)
        if np.any(idx_after):
            H_transmitted = 2 * np.sqrt(2) * np.std(eta[idx_after])
        else:
            H_transmitted = H_incident
        
        Kt = H_transmitted / (H_incident + 1e-10)
        
        return {
            'Kt': np.clip(Kt, 0, 1),
            'H_incident': H_incident,
            'H_transmitted': H_transmitted
        }
