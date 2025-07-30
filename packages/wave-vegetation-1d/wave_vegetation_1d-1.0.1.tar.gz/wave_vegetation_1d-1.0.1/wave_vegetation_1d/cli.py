"""Command-line interface for wave-vegetation-1d solver."""

import sys
import os
import argparse
from pathlib import Path
from .core import parse_config, WaveVegetationSolver


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Wave-Vegetation-1D: Physics-based wave attenuation solver v1.0.0"
    )
    parser.add_argument('config', help='Configuration file path')
    parser.add_argument('--version', action='version', version='1.0.0')
    
    args = parser.parse_args()
    
    # Handle config path
    config_path = Path(args.config)
    if not config_path.exists():
        package_dir = Path(__file__).parent.parent
        config_path = package_dir / args.config
        if not config_path.exists():
            config_path = package_dir / 'configs' / args.config
    
    if not config_path.exists():
        print(f"Error: Configuration file not found: {args.config}")
        sys.exit(1)
    
    try:
        print("="*70)
        print("WAVE-VEGETATION-1D SOLVER v1.0.0")
        print("Physics-based wave attenuation through coastal vegetation")
        print("="*70)
        
        config = parse_config(str(config_path))
        print(f"Configuration: {config_path.name}")
        print(f"Wave conditions: H={config['wave_height']:.2f}m, T={config['wave_period']:.1f}s")
        print(f"Water depth: h={config['water_depth']:.2f}m")
        print(f"Domain: L={config['domain_length']:.1f}m, dx={config['dx']:.3f}m")
        print(f"Time step: dt={config['dt']:.4f}s (CFL={config['computed_cfl']:.3f})")
        print("-"*70)
        
        solver = WaveVegetationSolver(config, config_name=config_path.stem)
        solver.run()
        
        print("\nSuccess! Results saved to ../outputs/")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
