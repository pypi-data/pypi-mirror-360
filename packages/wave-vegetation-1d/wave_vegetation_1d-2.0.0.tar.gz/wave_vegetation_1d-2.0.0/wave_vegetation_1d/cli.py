"""Command-line interface for wave-vegetation-1d solver."""

import sys
import argparse
from pathlib import Path
from .core import parse_config, WaveVegetationSolver


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Wave-Vegetation-1D: High-accuracy solver v2.0.0"
    )
    parser.add_argument('config', help='Configuration file path')
    parser.add_argument('--version', action='version', version='2.0.0')
    
    args = parser.parse_args()
    
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
        print("WAVE-VEGETATION-1D HIGH-ACCURACY SOLVER v2.0.0")
        print("4th-order Runge-Kutta time integration")
        print("="*70)
        
        config = parse_config(str(config_path))
        solver = WaveVegetationSolver(config, config_name=config_path.stem)
        solver.run()
        
        print("\nSuccess! Results saved to ../wave_veg_outputs/")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
