from setuptools import setup
from Cython.Build import cythonize

setup(
    name='Devil',
    ext_modules=cythonize("Devil.py", build_dir="build", compiler_directives={'language_level': "3"}),
    zip_safe=False,
)
