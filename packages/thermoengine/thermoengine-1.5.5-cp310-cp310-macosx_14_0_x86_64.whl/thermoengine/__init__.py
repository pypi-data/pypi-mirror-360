#!/usr/bin/env
""" file:thermoengine/__init__.py
    author: Aaron S. Wolf; Mark S. Ghiorso
    date: Tuesday June 27, 2017

    description: Python package interface to the PhaseObjC library.
"""
# Load all core methods and place in thermoengine namespace
from thermoengine_utils import core
from thermoengine_utils import coder
from thermoengine_utils.core import *
# from thermoengine.core import chem
from .chemistry import OxideMolComp, OxideWtComp, Oxides, ElemMolComp, Comp
from .phases import Phase


from . import phases
from . import samples
from . import model
from . import calibrate
from . import equilibrate
# from . import equilibrate_solids
from . import chemistry
from . import redox
from . import magmaforge

# from thermoengine import core
# from thermoengine.core import *
# from thermoengine.core import chem
# from thermoengine.chemistry import OxideMolComp, OxideWtComp, Oxides, ElemMolComp, Comp
# from thermoengine.phases import Phase


# from thermoengine import phases
# from thermoengine import samples
# from thermoengine import model
# from thermoengine import calibrate
# from thermoengine import equilibrate
# from thermoengine import equilibrate_solids
# from thermoengine import chemistry



__all__ = [s for s in dir() if not s.startswith('_')]
# __all__.extend(['equilibrate',])
