# setup.py
from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11

ext_modules = [
    Pybind11Extension(
        "core",           # имя модуля в Python: import core
        ["inertia_calculator.cpp"], 
        ["inertia_calculator.h"],
        ["main.cpp"],  
        cxx_std=17,
    ),
]

setup(
    name="core",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)