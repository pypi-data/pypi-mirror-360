from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wave-vegetation-1d",
    version="1.0.1",  # Increment version for update
    author="Sandy Herho, Iwan Anwar",
    author_email="sandy.herho@email.ucr.edu",
    description="Physics-based 1D wave propagation model through vegetated coastal areas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sandyherho/wave-veg-1d",
    project_urls={
        "Bug Tracker": "https://github.com/sandyherho/wave-veg-1d/issues",
        "Documentation": "https://github.com/sandyherho/wave-veg-1d#readme",
        "Source Code": "https://github.com/sandyherho/wave-veg-1d",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
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
    keywords="oceanography coastal-engineering wave-modeling vegetation mangroves wave-attenuation coastal-protection",
    include_package_data=True,
    zip_safe=False,
)
