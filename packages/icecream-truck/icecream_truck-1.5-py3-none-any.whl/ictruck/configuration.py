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


''' Portions of configuration hierarchy. '''


import icecream as _icecream

from . import __


class FormatterControl( __.immut.DataclassObject ):
    ''' Contextual data for formatter and prefix factories. '''

    columns_count_effective: __.typx.Annotated[
        __.typx.Optional[ int ],
        __.typx.Doc(
            ''' Available line length after accounting for embellishments.

                May be ``None`` if not determinable.
            '''
        ),
    ] = None


Flavor: __.typx.TypeAlias = int | str
Formatter: __.typx.TypeAlias = __.typx.Callable[ [ __.typx.Any ], str ]
FormatterFactory: __.typx.TypeAlias = (
    __.typx.Callable[ [ FormatterControl, str, Flavor ], Formatter ] )
PrefixEmitter: __.typx.TypeAlias = __.typx.Callable[ [ str, Flavor ], str ]
PrefixEmitterUnion: __.typx.TypeAlias = str | PrefixEmitter


class FlavorConfiguration( __.immut.DataclassObject ):
    ''' Per-flavor configuration. '''

    formatter_factory: __.typx.Annotated[
        __.typx.Optional[ FormatterFactory ],
        __.typx.Doc(
            ''' Factory which produces formatter callable.

                Takes formatter control, module name, and flavor as arguments.
                Returns formatter to convert an argument to a string.

                Default ``None`` inherits from cumulative configuration.
            ''' ),
    ] = None
    include_context: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.typx.Doc(
            ''' Include stack frame with output?

                Default ``None`` inherits from cumulative configuration.
            ''' ),
    ] = None
    prefix_emitter: __.typx.Annotated[
        __.typx.Optional[ PrefixEmitterUnion ],
        __.typx.Doc(
            ''' String or factory which produces output prefix string.

                Factory takes formatter control, module name, and flavor as
                arguments. Returns prefix string.

                Default ``None`` inherits from cumulative configuration.
            ''' ),
    ] = None


def produce_default_flavors( ) -> __.immut.Dictionary[
    Flavor, FlavorConfiguration
]:
    ''' Produces flavors for trace depths 0 through 9. '''
    return __.immut.Dictionary( {
        i: FlavorConfiguration(
            prefix_emitter = f"TRACE{i}| " ) for i in range( 10 ) } )


FlavorsRegistry: __.typx.TypeAlias = (
    __.immut.Dictionary[ Flavor, FlavorConfiguration ] )
FlavorsRegistryLiberal: __.typx.TypeAlias = (
    __.cabc.Mapping[ Flavor, FlavorConfiguration ] )


class ModuleConfiguration( __.immut.DataclassObject ):
    ''' Per-module or per-package configuration. '''

    flavors: __.typx.Annotated[
        FlavorsRegistry,
        __.typx.Doc(
            ''' Registry of flavor identifiers to configurations. ''' ),
    ] = __.dcls.field( default_factory = FlavorsRegistry )
    formatter_factory: __.typx.Annotated[
        __.typx.Optional[ FormatterFactory ],
        __.typx.Doc(
            ''' Factory which produces formatter callable.

                Takes formatter control, module name, and flavor as arguments.
                Returns formatter to convert an argument to a string.

                Default ``None`` inherits from cumulative configuration.
            ''' ),
    ] = None
    include_context: __.typx.Annotated[
        __.typx.Optional[ bool ],
        __.typx.Doc(
            ''' Include stack frame with output?

                Default ``None`` inherits from cumulative configuration.
            ''' ),
    ] = None
    prefix_emitter: __.typx.Annotated[
        __.typx.Optional[ PrefixEmitterUnion ],
        __.typx.Doc(
            ''' String or factory which produces output prefix string.

                Factory takes formatter control, module name, and flavor as
                arguments. Returns prefix string.

                Default ``None`` inherits from cumulative configuration.
            ''' ),
    ] = None


class VehicleConfiguration( __.immut.DataclassObject ):
    ''' Per-vehicle configuration. '''

    flavors: __.typx.Annotated[
        FlavorsRegistry,
        __.typx.Doc(
            ''' Registry of flavor identifiers to configurations. ''' ),
    ] = __.dcls.field( default_factory = produce_default_flavors )
    formatter_factory: __.typx.Annotated[
        FormatterFactory,
        __.typx.Doc(
            ''' Factory which produces formatter callable.

                Takes formatter control, module name, and flavor as arguments.
                Returns formatter to convert an argument to a string.
            ''' ),
    ] = lambda ctrl, mname, flavor: _icecream.DEFAULT_ARG_TO_STRING_FUNCTION
    include_context: __.typx.Annotated[
        bool, __.typx.Doc( ''' Include stack frame with output? ''' )
    ] = False
    prefix_emitter: __.typx.Annotated[
        PrefixEmitterUnion,
        __.typx.Doc(
            ''' String or factory which produces output prefix string.

                Factory takes formatter control, module name, and flavor as
                arguments. Returns prefix string.
            ''' ),
    ] = _icecream.DEFAULT_PREFIX
