"""High-order spatial discretization on staggered grid."""

import numpy as np
from typing import List, Tuple


class StaggeredGrid1D:
    """1D staggered grid with high-order operators."""
    
    def __init__(self, L: float, nx: int):
        """Initialize 1D staggered grid."""
        self.L = L
        self.nx = nx
        self.dx = L / nx
        
        # Cell centers (η points)
        self.x_eta = np.linspace(0.5*self.dx, L - 0.5*self.dx, nx)
        
        # Cell faces (u points)
        self.x_u = np.linspace(0, L, nx + 1)
        
        self.x = self.x_eta
        
    def create_vegetation_arrays(self, vegetation_zones: List[Tuple[float, float, float, float]]) -> Tuple[np.ndarray, np.ndarray]:
        """Create vegetation coefficient arrays."""
        cf_array = np.zeros(self.nx + 1)
        cd_array = np.zeros(self.nx + 1)
        
        for x_start, x_end, cf, cd in vegetation_zones:
            mask = (self.x_u >= x_start) & (self.x_u <= x_end)
            cf_array[mask] = cf
            cd_array[mask] = cd
            
        return cf_array, cd_array
    
    def create_sponge_layer(self, width_fraction: float = 0.1, strength: float = 10.0) -> np.ndarray:
        """Create sponge layer with quartic profile."""
        sponge = np.zeros(self.nx)
        sponge_width = width_fraction * self.L
        sponge_start = self.L - sponge_width
        
        for i, x in enumerate(self.x_eta):
            if x > sponge_start:
                xi = (x - sponge_start) / sponge_width
                sponge[i] = strength * xi**4  # Quartic for smoother transition
                
        return sponge


def initialize_wave(grid: StaggeredGrid1D, config: dict) -> Tuple[np.ndarray, np.ndarray]:
    """Initialize water elevation and velocity fields."""
    eta = np.zeros(grid.nx)
    u = np.zeros(grid.nx + 1)
    return eta, u
