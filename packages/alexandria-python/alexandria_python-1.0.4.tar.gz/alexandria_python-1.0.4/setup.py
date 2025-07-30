from setuptools import setup, find_packages

# read long description from README.md
with open("README.md", "r") as readme:
    long_description = readme.read()

# set up the package
setup(
    name = "alexandria-python",
    license = "Other/Proprietary License",
    version = "1.0.4",
    packages = find_packages('.'),  
    include_package_data = True,
    author = "Romain Legrand",
    author_email = "alexandria.toolbox@gmail.com",
    description = "a software for Bayesian vector autoregressions and other Bayesian time-series applications",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    python_requires = ">=3.6",
    keywords=["python", "Bayesian", "time-series", "econometrics"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics"]
)
