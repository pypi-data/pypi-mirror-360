"""Spatial discretization on staggered grid for coastal wave modeling."""

import numpy as np
from typing import List, Tuple


class StaggeredGrid1D:
    """1D staggered grid for shallow water equations.
    
    Uses Arakawa C-grid arrangement:
    - Water elevation η at cell centers
    - Velocity u at cell faces
    """
    
    def __init__(self, L: float, nx: int):
        """Initialize 1D staggered grid.
        
        Parameters:
        -----------
        L : float
            Domain length [m]
        nx : int
            Number of grid cells
        """
        self.L = L
        self.nx = nx
        self.dx = L / nx
        
        # Cell centers (η points) - water surface elevation
        self.x_eta = np.linspace(0.5*self.dx, L - 0.5*self.dx, nx)
        
        # Cell faces (u points) - velocity
        self.x_u = np.linspace(0, L, nx + 1)
        
        # Alias for convenience
        self.x = self.x_eta
        
    def create_vegetation_arrays(self, vegetation_zones: List[Tuple[float, float, float, float]]) -> Tuple[np.ndarray, np.ndarray]:
        """Create vegetation coefficient arrays.
        
        Parameters:
        -----------
        vegetation_zones : list
            List of (x_start, x_end, Cf, Cd) tuples where:
            - x_start, x_end: zone boundaries [m]
            - Cf: friction coefficient [-]
            - Cd: eddy viscosity [m²/s]
            
        Returns:
        --------
        cf_array : ndarray
            Friction coefficients at u-points
        cd_array : ndarray
            Eddy viscosity at u-points
        """
        cf_array = np.zeros(self.nx + 1)
        cd_array = np.zeros(self.nx + 1)
        
        for x_start, x_end, cf, cd in vegetation_zones:
            mask = (self.x_u >= x_start) & (self.x_u <= x_end)
            cf_array[mask] = cf
            cd_array[mask] = cd
            
        return cf_array, cd_array
    
    def create_sponge_layer(self, width_fraction: float = 0.1, strength: float = 5.0) -> np.ndarray:
        """Create sponge layer for wave absorption at boundary.
        
        Uses cubic polynomial ramp for smooth absorption.
        
        Parameters:
        -----------
        width_fraction : float
            Fraction of domain for sponge layer
        strength : float
            Maximum damping coefficient [1/s]
            
        Returns:
        --------
        sponge : ndarray
            Damping coefficients at η-points
        """
        sponge = np.zeros(self.nx)
        sponge_width = width_fraction * self.L
        sponge_start = self.L - sponge_width
        
        for i, x in enumerate(self.x_eta):
            if x > sponge_start:
                # Normalized position in sponge layer
                xi = (x - sponge_start) / sponge_width
                # Smooth cubic ramp
                sponge[i] = strength * xi**3
                
        return sponge


def initialize_wave(grid: StaggeredGrid1D, config: dict) -> Tuple[np.ndarray, np.ndarray]:
    """Initialize water elevation and velocity fields.
    
    Start from rest with zero elevation for smooth ramp-up.
    
    Parameters:
    -----------
    grid : StaggeredGrid1D
        Spatial grid
    config : dict
        Configuration parameters
        
    Returns:
    --------
    eta : ndarray
        Initial water surface elevation [m]
    u : ndarray
        Initial velocity [m/s]
    """
    eta = np.zeros(grid.nx)
    u = np.zeros(grid.nx + 1)
    return eta, u
