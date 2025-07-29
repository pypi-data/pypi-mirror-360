# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Flexible factory for Icecream debuggers.

    A debugging library that enhances the `icecream
    <https://github.com/gruns/icecream>`_ package with flexible, flavorful
    traces and module-specific configurations. Designed for both application
    and library developers, it provides granular control over debug output
    while ensuring isolation between different configurations.

    The package organizes its functionality across several modules, providing
    exceptions, configuration hierarchies, and specialized output recipes.
'''


from . import __
# --- BEGIN: Injected by Copier ---
from . import exceptions
# --- END: Injected by Copier ---


from .configuration import *
from .exceptions import *
from .printers import *
from .vehicles import *


__version__: str
__version__ = '1.5'


__.immut.finalize_module( __name__, recursive = True )
