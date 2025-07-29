from setuptools import setup
from Cython.Build import cythonize
# import numpy

setup(
    ext_modules=cythonize(
        [
            "poc/*.py"
        ],
        compiler_directives={"language_level": "3"},
        include_path=[
            # numpy.get_include()
        ],
    ),
    zip_safe=False,
)