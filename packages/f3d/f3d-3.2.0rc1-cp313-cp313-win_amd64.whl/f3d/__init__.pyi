"""

Fast and minimalist 3D viewer
"""
from __future__ import annotations
from f3d.pyf3d import Camera
from f3d.pyf3d import CameraState
from f3d.pyf3d import Engine
from f3d.pyf3d import Image
from f3d.pyf3d import InteractionBind
from f3d.pyf3d import Interactor
from f3d.pyf3d import LibInformation
from f3d.pyf3d import Log
from f3d.pyf3d import Mesh
from f3d.pyf3d import Options
from f3d.pyf3d import ReaderInformation
from f3d.pyf3d import Scene
from f3d.pyf3d import Utils
from f3d.pyf3d import Window
import os as os
import pathlib._local
from pathlib._local import Path
import re as re
import sys as sys
from typing import Any
import warnings as warnings
from . import pyf3d
__all__: list = ['Camera', 'CameraState', 'Engine', 'Image', 'InteractionBind', 'Interactor', 'LibInformation', 'Log', 'Mesh', 'Options', 'ReaderInformation', 'Scene', 'Utils', 'Window']
def _add_deprecation_warnings():
    ...
def _deprecated_decorator(f, reason):
    ...
def _f3d_options_update(self, arg: typing.Union[typing.Mapping[str, typing.Any], typing.Iterable[tuple[str, typing.Any]]]) -> None:
    ...
F3D_ABSOLUTE_DLLS: list = ['D:/a/f3d-superbuild/f3d-superbuild/fsbb/install/bin', 'D:/a/f3d-superbuild/f3d-superbuild/fsbb/install/lib', 'C:/Users/runneradmin/AppData/Local/Temp/tmpahyw3xy0/build/bin']
F3D_RELATIVE_DLLS: list = list()
__version__: str = '3.2.0'
abs_path: str = 'C:/Users/runneradmin/AppData/Local/Temp/tmpahyw3xy0/build/bin'
root: pathlib._local.WindowsPath  # value = WindowsPath('C:/Users/runneradmin/AppData/Local/Temp/tmpahyw3xy0/build/f3d')
