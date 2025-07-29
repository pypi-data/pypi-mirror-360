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


''' Printers, printer factories, and auxiliary functions and types. '''



import colorama as _colorama

from . import __
from . import configuration as _cfg
from . import exceptions as _exceptions


_validate_arguments = (
    __.validate_arguments(
        globalvars = globals( ),
        errorclass = _exceptions.ArgumentClassInvalidity ) )


Printer: __.typx.TypeAlias = __.cabc.Callable[ [ str ], None ]
PrinterFactory: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str, _cfg.Flavor ], Printer ] )
PrinterFactoryUnion: __.typx.TypeAlias = __.io.TextIOBase | PrinterFactory


@_validate_arguments
def produce_simple_printer(
    target: __.io.TextIOBase,
    mname: str,
    flavor: _cfg.Flavor,
    force_color: bool = False,
) -> Printer:
    ''' Produces printer which uses standard Python 'print'. '''
    match __.sys.platform:
        case 'win32':
            winansi = _colorama.AnsiToWin32( target ) # pyright: ignore
            target_ = ( # pragma: no cover
                winansi.stream if winansi.convert else target )
        case _: target_ = target
    return __.funct.partial(
        _simple_print,
        target = target_, # pyright: ignore
        force_color = force_color )


def _remove_ansi_c1_sequences( text: str ) -> str:
    # https://stackoverflow.com/a/14693789/14833542
    regex = __.re.compile( r'''\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])''' )
    return regex.sub( '', text )


def _simple_print(
    text: str, target: __.io.TextIOBase, force_color = False
) -> None:
    if not force_color and not target.isatty( ):
        print( _remove_ansi_c1_sequences( text ), file = target )
        return
    print( text, file = target )
