from setuptools import setup, find_packages

setup(
    name="wave-vegetation-1d",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "xarray>=0.19.0",
        "netCDF4>=1.5.7",
    ],
    entry_points={
        "console_scripts": [
            "wave-veg-1d=wave_vegetation_1d.cli:main",
        ],
    },
)
