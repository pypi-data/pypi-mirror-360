from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wave-vegetation-1d",
    version="2.0.0",
    author="Sandy Herho, Iwan Anwar",
    author_email="sandy.herho@email.ucr.edu",
    description="High-accuracy 1D wave propagation model through vegetated coastal areas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sandyherho/wave-veg-1d",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "xarray>=0.19.0",
        "netCDF4>=1.5.7",
    ],
    entry_points={
        "console_scripts": [
            "wave-veg-1d=wave_vegetation_1d.cli:main",
        ],
    },
)
