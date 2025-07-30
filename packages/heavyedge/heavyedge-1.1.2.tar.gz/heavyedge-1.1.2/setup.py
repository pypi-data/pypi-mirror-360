import numpy
from Cython.Build import cythonize
from setuptools import Extension, setup

extensions = [
    Extension(
        "heavyedge._wasserstein",
        ["src/heavyedge/_wasserstein.pyx"],
    ),
]

setup(
    ext_modules=cythonize(extensions),
    include_dirs=[numpy.get_include()],
    include_package_data=True,
)
