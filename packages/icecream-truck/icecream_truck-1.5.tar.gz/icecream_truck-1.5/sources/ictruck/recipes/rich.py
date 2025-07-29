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


''' Recipes for Rich formatters and printers.

    .. note::

        To use this module, you must have the ``rich`` package installed.
'''



from rich.console import Console as _Console
from rich.pretty import pretty_repr as _pretty_repr

from . import __


_validate_arguments = (
    __.validate_arguments(
        globalvars = globals( ),
        errorclass = __.exceptions.ArgumentClassInvalidity ) )


class ConsoleTextIoInvalidity( __.exceptions.Omnierror, TypeError ):
    ''' Text stream invalid for use with Rich console. '''

    def __init__( self, stream: __.typx.Any ):
        super( ).__init__( f"Invalid stream for Rich console: {stream!r}" )


class Modes( __.enum.Enum ):
    ''' Operation modes for Rich truck. '''

    Formatter = 'formatter'
    Printer = 'printer'


ProduceTruckModeArgument: __.typx.TypeAlias = __.typx.Annotated[
    Modes,
    __.typx.Doc(
        ''' Operation mode.

            ``Formatter`` uses Rich to highlight and pretty text prior to
            printing (output). Text from non-Rich formatters will be printed
            as-is. Safer, but slightly more boring option.
            ``Printer`` uses Rich to highlight and pretty text while printing
            (output). Text from non-Rich formatters will be potentially be
            highlighted and prettied. If the text already contains ANSI SGR
            sequences (e.g., terminal colorization), then it might be
            reprocessed by the printer, causing visual artifacts. Less safe,
            but more vibrant option.
        ''' ),
]
ProduceTruckStderrArgument: __.typx.TypeAlias = __.typx.Annotated[
    bool, __.typx.Doc( ''' Output to standard diagnostic stream? ''' )
]


@_validate_arguments
def install( # noqa: PLR0913
    alias: __.InstallAliasArgument = __.builtins_alias_default,
    flavors: __.ProduceTruckFlavorsArgument = __.absent,
    active_flavors: __.ProduceTruckActiveFlavorsArgument = __.absent,
    trace_levels: __.ProduceTruckTraceLevelsArgument = __.absent,
    mode: ProduceTruckModeArgument = Modes.Formatter,
    stderr: ProduceTruckStderrArgument = True,
) -> __.Truck:
    ''' Produces truck and installs it into builtins with alias.

        Replaces an existing truck, preserving global module configurations.

        Library developers should call :py:func:`__.register_module` instead.
    '''
    truck = produce_truck(
        flavors = flavors,
        active_flavors = active_flavors,
        trace_levels = trace_levels,
        mode = mode,
        stderr = stderr )
    return truck.install( alias = alias )


@_validate_arguments
def produce_console_formatter(
    console: _Console,
    control: __.FormatterControl,
    mname: str,
    flavor: int | str,
) -> __.Formatter:
    ''' Produces formatter which uses Rich highlighter and prettier. '''
    return __.funct.partial( _console_format, console )


@_validate_arguments
def produce_console_printer(
    console: _Console, mname: str, flavor: __.Flavor
) -> __.Printer:
    # TODO: Remove from recipe. Should always use simple printer.
    ''' Produces a printer that uses Rich console printing.

        .. note::

            May reprocess ANSI SGR codes or markup from formatters, potentially
            causing visual artifacts. Be careful to use this only with "safe"
            formatters.
    '''
    return console.print


@_validate_arguments
def produce_pretty_formatter(
    control: __.FormatterControl, mname: str, flavor: int | str
) -> __.Formatter:
    ''' Produces formatter which uses Rich prettier. '''
    return _pretty_repr


@_validate_arguments
def produce_truck(
    flavors: __.ProduceTruckFlavorsArgument = __.absent,
    active_flavors: __.ProduceTruckActiveFlavorsArgument = __.absent,
    trace_levels: __.ProduceTruckTraceLevelsArgument = __.absent,
    mode: ProduceTruckModeArgument = Modes.Formatter,
    stderr: ProduceTruckStderrArgument = True,
) -> __.Truck:
    ''' Produces icecream truck which integrates with Rich. '''
    match mode:
        case Modes.Formatter: factory = _produce_formatter_truck
        case Modes.Printer: factory = _produce_printer_truck
    return factory(
        flavors = flavors,
        active_flavors = active_flavors,
        trace_levels = trace_levels,
        stderr = stderr )


@_validate_arguments
def register_module(
    name: __.RegisterModuleNameArgument = __.absent,
    flavors: __.ProduceTruckFlavorsArgument = __.absent,
    include_context: __.RegisterModuleIncludeContextArgument = __.absent,
    prefix_emitter: __.RegisterModulePrefixEmitterArgument = __.absent,
) -> None:
    ''' Registers module with Rich prettier to format arguments.

        Intended for library developers to configure debugging flavors without
        overriding anything set by the application or other libraries.
    '''
    __.register_module(
        name = name,
        flavors = flavors,
        formatter_factory = produce_pretty_formatter,
        include_context = include_context,
        prefix_emitter = prefix_emitter )


def _console_format( console: _Console, value: __.typx.Any ) -> str:
    with console.capture( ) as capture:
        console.print( value )
    return capture.get( )


def _produce_formatter_truck(
    flavors: __.ProduceTruckFlavorsArgument = __.absent,
    active_flavors: __.ProduceTruckActiveFlavorsArgument = __.absent,
    trace_levels: __.ProduceTruckTraceLevelsArgument = __.absent,
    stderr: ProduceTruckStderrArgument = True,
) -> __.Truck:
    console = _Console( stderr = stderr )
    gc_nomargs = { }
    if not __.is_absent( flavors ): gc_nomargs[ 'flavors' ] = flavors
    generalcfg = __.VehicleConfiguration(
        formatter_factory = __.funct.partial(
            produce_console_formatter, console ),
        **gc_nomargs ) # pyright: ignore
    target = __.sys.stderr if stderr else __.sys.stdout
    if not isinstance( target, __.io.TextIOBase ):
        raise ConsoleTextIoInvalidity( target )
    nomargs: dict[ str, __.typx.Any ] = dict(
        active_flavors = active_flavors,
        generalcfg = generalcfg,
        printer_factory = __.funct.partial(
            __.produce_simple_printer, target ),
        trace_levels = trace_levels )
    return __.produce_truck( **nomargs )


def _produce_printer_truck(
    flavors: __.ProduceTruckFlavorsArgument = __.absent,
    active_flavors: __.ProduceTruckActiveFlavorsArgument = __.absent,
    trace_levels: __.ProduceTruckTraceLevelsArgument = __.absent,
    stderr: ProduceTruckStderrArgument = True,
) -> __.Truck:
    console = _Console( stderr = stderr )
    gc_nomargs = { }
    if not __.is_absent( flavors ): gc_nomargs[ 'flavors' ] = flavors
    generalcfg = __.VehicleConfiguration(
        formatter_factory = produce_pretty_formatter,
        **gc_nomargs ) # pyright: ignore
    target = __.sys.stderr if stderr else __.sys.stdout
    if not isinstance( target, __.io.TextIOBase ): # pragma: no cover
        raise ConsoleTextIoInvalidity( target )
    nomargs: dict[ str, __.typx.Any ] = dict(
        active_flavors = active_flavors,
        generalcfg = generalcfg,
        printer_factory = __.funct.partial( produce_console_printer, console ),
        trace_levels = trace_levels )
    return __.produce_truck( **nomargs )


# def _produce_prefix( console: _Console, mname: str, flavor: _Flavor ) -> str:
#     # TODO: Detect if terminal supports 256 colors or true color.
#     #       Make spectrum of hues for trace depths, if so.
#     return _icecream.DEFAULT_PREFIX
