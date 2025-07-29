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


''' Recipes for integration with standard logging. '''



import logging as _logging

from . import __


_validate_arguments = (
    __.validate_arguments(
        globalvars = globals( ),
        errorclass = __.exceptions.ArgumentClassInvalidity ) )


InstallAdditionalAliasesArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ __.cabc.Mapping[ str, str ] ],
    __.typx.Doc(
        ''' Mapping of builtins attribute names to flavors. ''' ),
]


@_validate_arguments
def install(
    alias: __.InstallAliasArgument = __.builtins_alias_default,
    additional_aliases: InstallAdditionalAliasesArgument = __.absent,
) -> __.Truck:
    ''' Produces truck and installs it into builtins with alias.

        Replaces an existing truck, preserving global module configurations.

        Library developers should call :py:func:`__.register_module` instead.
    '''
    truck = produce_truck( ).install( alias = alias )
    if __.is_absent( additional_aliases ): additional_aliases = { }
    for falias, flavor in additional_aliases.items( ):
        __.install_builtin_safely(
            falias, truck( flavor ), __.exceptions.AttributeNondisplacement )
    return truck


@_validate_arguments
def produce_printer( mname: str, flavor: __.Flavor ) -> __.Printer:
    ''' Produces printer which maps flavors to logging levels. '''
    logger = _logging.getLogger( mname )
    level = (
        getattr( _logging, flavor.upper( ) ) if isinstance( flavor, str )
        else _logging.DEBUG )
    return lambda x: logger.log( level, x )


@_validate_arguments
def produce_truck( ) -> __.Truck:
    ''' Produces icecream truck which integrates with standard logging. '''
    active_flavors = { None: frozenset( {
        'debug', 'info', 'warning', 'error', 'critical' } ) }
    flavors: __.immut.Dictionary[ __.Flavor, __.FlavorConfiguration ] = (
        __.immut.Dictionary(
            {   name: __.FlavorConfiguration( )
                for name in active_flavors[ None ] } ) )
    generalcfg = __.VehicleConfiguration( flavors = flavors )
    nomargs = dict(
        active_flavors = active_flavors,
        generalcfg = generalcfg,
        printer_factory = produce_printer )
    return __.Truck( **nomargs ) # pyright: ignore
