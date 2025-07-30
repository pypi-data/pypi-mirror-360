"""
A package for generating dummy EXR files following VFX naming conventions.

Basic usage:
    from fakeshot import Template, generate_dummy_shots

    template = Template(show='my_project')
    generate_dummy_shots(template, './output')
"""

from __future__ import annotations

from .template import Template
from .generate_csv import generate_csv
from .generate_exr import generate_exr
from .generate_shots import generate_shots

__all__ = [
    'Template',
    'generate_csv',
    'generate_shots',
    'generate_exr'
]

__version__ = '0.3.2'
