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


''' Recipe for advanced formatters.

    .. note::

        To use this module, you must have the ``rich`` package installed.
'''

# TODO? Allow selection of trace color gradients.



from rich.console import Console as _Console
from rich.style import Style as _Style

from . import __


_validate_arguments = (
    __.validate_arguments(
        globalvars = globals( ),
        errorclass = __.exceptions.ArgumentClassInvalidity ) )


InterpolantsStylesRegistry: __.typx.TypeAlias = (
    __.accret.Dictionary[ str, _Style ] )


class Auxiliaries( __.immut.DataclassObject ):
    ''' Auxiliary functions used by formatters and interpolation.

        Typically used by unit tests to inject mock dependencies,
        but can also be used to deeply customize output.
    '''

    exc_info_discoverer: __.typx.Annotated[
        __.typx.Callable[ [ ], __.ExceptionInfo ],
        __.typx.Doc( ''' Returns information on current exception. ''' ),
    ] = __.sys.exc_info
    pid_discoverer: __.typx.Annotated[
        __.typx.Callable[ [ ], int ],
        __.typx.Doc( ''' Returns ID of current process. ''' ),
    ] = __.os.getpid
    thread_discoverer: __.typx.Annotated[
        __.typx.Callable[ [ ], __.threads.Thread ],
        __.typx.Doc( ''' Returns current thread. ''' ),
    ] = __.threads.current_thread
    time_formatter: __.typx.Annotated[
        __.typx.Callable[ [ str ], str ],
        __.typx.Doc( ''' Returns current time in specified format. ''' ),
    ] = __.time.strftime



class FlavorSpecification( __.immut.DataclassObject ):
    ''' Specification for custom flavor. '''

    color: __.typx.Annotated[
        str, __.typx.Doc( ''' Name of prefix color. ''' ) ]
    emoji: __.typx.Annotated[ str, __.typx.Doc( ''' Prefix emoji. ''' ) ]
    label: __.typx.Annotated[ str, __.typx.Doc( ''' Prefix label. ''' ) ]
    stack: __.typx.Annotated[
        bool, __.typx.Doc( ''' Include stack trace? ''' )
    ] = False


class PrefixDecorations( __.enum.IntFlag ):
    ''' Decoration styles for prefix emission. '''

    Plain =     0
    Color =     __.enum.auto( )
    Emoji =     __.enum.auto( )


class PrefixLabelPresentations( __.enum.IntFlag ):
    ''' How prefix label should be presented. '''

    Nothing =   0
    Words =     __.enum.auto( )
    Emoji =     __.enum.auto( )


class PrefixFormatControl( __.immut.DataclassObject ):
    ''' Format control for prefix emission. '''

    colorize: __.typx.Annotated[
        bool, __.typx.Doc( ''' Attempt to colorize? ''' )
    ] = True
    label_as: __.typx.Annotated[
        PrefixLabelPresentations,
        __.typx.Doc(
            ''' How to present prefix label.

                ``Words``: As words like ``TRACE0`` or ``ERROR``.
                ``Emoji``: As emoji like ``🔎`` or ``❌``.

                For both emoji and words: ``Emoji | Words``.
            ''' )
    ] = PrefixLabelPresentations.Words
    styles: __.typx.Annotated[
        InterpolantsStylesRegistry,
        __.typx.Doc(
            ''' Mapping of interpolant names to ``rich`` style objects. ''' ),
    ] = __.dcls.field( default_factory = InterpolantsStylesRegistry )
    template: __.typx.Annotated[
        str,
        __.typx.Doc(
            ''' String format for prefix.

                The following interpolants are supported:
                ``flavor``: Decorated flavor.
                ``module_qname``: Qualified name of invoking module.
                ``timestamp``: Current timestamp, formatted as string.
                ``process_id``: ID of current process according to OS kernel.
                ``thread_id``: ID of current thread.
                ``thread_name``: Name of current thread.
            ''' ),
    ] = "{flavor}| " # "{timestamp} [{module_qname}] {flavor}| "
    ts_format: __.typx.Annotated[
        str,
        __.typx.Doc(
            ''' String format for prefix timestamp.

                Used by :py:func:`time.strftime` or equivalent.
            ''' ),
    ] = '%Y-%m-%d %H:%M:%S.%f'


ProduceModulecfgAuxiliariesArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ Auxiliaries ],
    __.typx.Doc( ''' Auxiliary functions for formatting. ''' ),
]
ProduceModulecfgColorizeArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ bool ],
    __.typx.Doc( ''' Attempt to colorize output prefixes? ''' ),
]
ProduceModulecfgConsoleFactoryArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ __.typx.Callable[ [ ], _Console ] ],
    __.typx.Doc(
        ''' Factory function that produces Rich console instances. ''' ),
]
ProduceModulecfgPrefixLabelAsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ PrefixLabelPresentations ],
    __.typx.Doc(
        ''' How to present prefix labels (words, emoji, or both). ''' ),
]
ProduceModulecfgPrefixStylesArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ __.cabc.Mapping[ str, _Style ] ],
    __.typx.Doc( ''' Mapping of interpolant names to Rich style objects. ''' ),
]
ProduceModulecfgPrefixTemplateArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ str ],
    __.typx.Doc( ''' String template for prefix formatting. ''' ),
]
ProduceModulecfgPrefixTsFormatArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ str ],
    __.typx.Doc( ''' Timestamp format string for prefix. ''' ),
]


_flavor_specifications: __.immut.Dictionary[
    str, FlavorSpecification
] = __.immut.Dictionary(
    note = FlavorSpecification(
        color = 'blue',
        emoji = '\N{Information Source}\ufe0f',
        label = 'NOTE' ),
    monition = FlavorSpecification(
        color = 'yellow',
        emoji = '\N{Warning Sign}\ufe0f',
        label = 'MONITION' ),
    error = FlavorSpecification(
        color = 'red', emoji = '❌', label = 'ERROR' ),
    errorx = FlavorSpecification(
        color = 'red', emoji = '❌', label = 'ERROR', stack = True ),
    abort = FlavorSpecification(
        color = 'bright_red', emoji = '💥', label = 'ABORT' ),
    abortx = FlavorSpecification(
        color = 'bright_red', emoji = '💥', label = 'ABORT', stack = True ),
    future = FlavorSpecification(
        color = 'magenta', emoji = '🔮', label = 'FUTURE' ),
    success = FlavorSpecification(
        color = 'green', emoji = '✅', label = 'SUCCESS' ),
)

_flavor_aliases: __.immut.Dictionary[
    str, str
] = __.immut.Dictionary( {
    'n': 'note', 'm': 'monition',
    'e': 'error', 'a': 'abort',
    'ex': 'errorx', 'ax': 'abortx',
    'f': 'future', 's': 'success',
} )

_trace_color_names: tuple[ str, ... ] = (
    'grey85', 'grey82', 'grey78', 'grey74', 'grey70',
    'grey66', 'grey62', 'grey58', 'grey54', 'grey50' )

_trace_prefix_styles: tuple[ _Style, ... ] = tuple(
    _Style( color = name ) for name in _trace_color_names )


def _produce_console( ) -> _Console: # pragma: no cover
    # TODO? safe_box = True
    # Ideally, we want TTY so that Rich can detect proper attributes.
    # Failing that, stream to null device. (Output capture should still work.)
    for stream in ( __.sys.stderr, __.sys.stdout ):
        if not stream.isatty( ): continue
        return _Console( stderr = stream is __.sys.stderr )
    blackhole = open( # noqa: SIM115
        __.os.devnull, 'w', encoding = __.locale.getpreferredencoding( ) )
    # TODO? height = 24, width = 80
    return _Console( file = blackhole, force_terminal = True )


@_validate_arguments
def produce_module_configuration( # noqa: PLR0913
    colorize: ProduceModulecfgColorizeArgument = __.absent,
    prefix_label_as: ProduceModulecfgPrefixLabelAsArgument = __.absent,
    prefix_styles: ProduceModulecfgPrefixStylesArgument = __.absent,
    prefix_template: ProduceModulecfgPrefixTemplateArgument = __.absent,
    prefix_ts_format: ProduceModulecfgPrefixTsFormatArgument = __.absent,
    console_factory: ProduceModulecfgConsoleFactoryArgument = __.absent,
    auxiliaries: ProduceModulecfgAuxiliariesArgument = __.absent,
) -> __.ModuleConfiguration:
    ''' Produces module configuration with sundae-specific flavor settings. '''
    if __.is_absent( console_factory ): console_factory = _produce_console
    if __.is_absent( auxiliaries ): auxiliaries = Auxiliaries( )
    console = console_factory( )
    prefix_fmtctl_initargs: dict[ str, __.typx.Any ] = { }
    if not __.is_absent( colorize ):
        prefix_fmtctl_initargs[ 'colorize' ] = colorize
    if not __.is_absent( prefix_label_as ):
        prefix_fmtctl_initargs[ 'label_as' ] = prefix_label_as
    if not __.is_absent( prefix_styles ):
        prefix_fmtctl_initargs[ 'styles' ] = prefix_styles
    if not __.is_absent( prefix_template ):
        prefix_fmtctl_initargs[ 'template' ] = prefix_template
    if not __.is_absent( prefix_ts_format ):
        prefix_fmtctl_initargs[ 'ts_format' ] = prefix_ts_format
    prefix_fmtctl = PrefixFormatControl( **prefix_fmtctl_initargs )
    flavors = _produce_flavors( console, auxiliaries, prefix_fmtctl )
    formatter_factory = _produce_formatter_factory( console, auxiliaries )
    return __.ModuleConfiguration(
        flavors = flavors, formatter_factory = formatter_factory )


@_validate_arguments
def register_module( # noqa: PLR0913
    name: __.RegisterModuleNameArgument = __.absent,
    colorize: ProduceModulecfgColorizeArgument = __.absent,
    prefix_label_as: ProduceModulecfgPrefixLabelAsArgument = __.absent,
    prefix_styles: ProduceModulecfgPrefixStylesArgument = __.absent,
    prefix_template: ProduceModulecfgPrefixTemplateArgument = __.absent,
    prefix_ts_format: ProduceModulecfgPrefixTsFormatArgument = __.absent,
    console_factory: ProduceModulecfgConsoleFactoryArgument = __.absent,
    auxiliaries: ProduceModulecfgAuxiliariesArgument = __.absent,
) -> __.ModuleConfiguration:
    ''' Registers module with sundae-specific flavor configurations. '''
    configuration = produce_module_configuration(
        colorize = colorize,
        prefix_label_as = prefix_label_as,
        prefix_styles = prefix_styles,
        prefix_template = prefix_template,
        prefix_ts_format = prefix_ts_format,
        console_factory = console_factory,
        auxiliaries = auxiliaries )
    return __.register_module(
        name = name,
        flavors = configuration.flavors,
        formatter_factory = configuration.formatter_factory )


def _produce_flavors(
    console: _Console, auxiliaries: Auxiliaries, control: PrefixFormatControl
) -> __.FlavorsRegistry:
    emitter = _produce_prefix_emitter( console, auxiliaries, control )
    flavors: __.FlavorsRegistryLiberal = { }
    for name in _flavor_specifications:
        flavors[ name ] = __.FlavorConfiguration( prefix_emitter = emitter )
    for alias, name in _flavor_aliases.items( ):
        flavors[ alias ] = flavors[ name ]
    for level in range( 10 ):
        flavors[ level ] = __.FlavorConfiguration( prefix_emitter = emitter )
    return __.immut.Dictionary( flavors )


def _produce_formatter_factory(
    console: _Console, auxiliaries: Auxiliaries
) -> __.FormatterFactory:

    def factory(
        control: __.FormatterControl, mname: str, flavor: __.Flavor
    ) -> __.Formatter:

        def formatter( value: __.typx.Any ) -> str:
            tb_text = ''
            if isinstance( flavor, str ):
                flavor_ = _flavor_aliases.get( flavor, flavor )
                spec = _flavor_specifications[ flavor_ ]
                if spec.stack and auxiliaries.exc_info_discoverer( )[ 0 ]:
                    with console.capture( ) as capture:
                        console.print_exception( )
                    tb_text = capture.get( )
            else: flavor_ = flavor
            with console.capture( ) as capture:
                console.print( value, end = '' )
            text = capture.get( )
            if tb_text: return f"\n{tb_text}\n{text}"
            return text

        return formatter

    return factory


def _produce_prefix_emitter(
    console: _Console, auxiliaries: Auxiliaries, control: PrefixFormatControl
) -> __.PrefixEmitter:

    def emitter( mname: str, flavor: __.Flavor ) -> str:
        if isinstance( flavor, int ):
            return _produce_trace_prefix(
                console, auxiliaries, control, mname, flavor )
        name = _flavor_aliases.get( flavor, flavor )
        return _produce_special_prefix(
            console, auxiliaries, control, mname, name )

    return emitter


def _produce_special_prefix(
    console: _Console,
    auxiliaries: Auxiliaries,
    control: PrefixFormatControl,
    mname: str,
    flavor: str,
) -> str:
    styles = dict( control.styles )
    spec = _flavor_specifications[ flavor ]
    label = ''
    if control.label_as & PrefixLabelPresentations.Emoji:
        if control.label_as & PrefixLabelPresentations.Words:
            label = f"{spec.emoji} {spec.label}"
        else: label = f"{spec.emoji}"
    elif control.label_as & PrefixLabelPresentations.Words:
        label = f"{spec.label}"
    if control.colorize: styles[ 'flavor' ] = _Style( color = spec.color )
    return _render_prefix(
        console, auxiliaries, control, mname, label, styles )


def _produce_trace_prefix(
    console: _Console,
    auxiliaries: Auxiliaries,
    control: PrefixFormatControl,
    mname: str,
    level: int,
) -> str:
    # TODO? Option to render indentation guides.
    styles = dict( control.styles )
    label = ''
    if control.label_as & PrefixLabelPresentations.Emoji:
        if control.label_as & PrefixLabelPresentations.Words:
            label = f"🔎 TRACE{level}"
        else: label = '🔎'
    elif control.label_as & PrefixLabelPresentations.Words:
        label = f"TRACE{level}"
    if control.colorize and level < len( _trace_color_names ):
        styles[ 'flavor' ] = _Style( color = _trace_color_names[ level ] )
    indent = '  ' * level
    return _render_prefix(
        console, auxiliaries, control, mname, label, styles ) + indent


def _render_prefix( # noqa: PLR0913
    console: _Console,
    auxiliaries: Auxiliaries,
    control: PrefixFormatControl,
    mname: str,
    flavor: str,
    styles: dict[ str, _Style ],
) -> str:
    # TODO? Performance optimization: Only compute and interpolate PID, thread,
    #       and timestamp, if capabilities set permits.
    thread = auxiliaries.thread_discoverer( )
    interpolants: dict[ str, str ] = {
        'flavor': flavor,
        'module_qname': mname,
        'timestamp': auxiliaries.time_formatter( control.ts_format ),
        'process_id': str( auxiliaries.pid_discoverer( ) ),
        'thread_id': str( thread.ident ),
        'thread_name': thread.name,
    }
    if control.colorize: _stylize_interpolants( console, interpolants, styles )
    return control.template.format( **interpolants )


def _stylize_interpolants(
    console: _Console,
    interpolants: dict[ str, str ],
    styles: dict[ str, _Style ],
) -> None:
    style_default = styles.get( 'flavor' )
    interpolants_: dict[ str, str ] = { }
    for iname, ivalue in interpolants.items( ):
        style = styles.get( iname, style_default )
        if not style: continue # pragma: no branch
        with console.capture( ) as capture:
            console.print(
                ivalue, end = '', highlight = False, style = style  )
        interpolants_[ iname ] = capture.get( )
    interpolants.update( interpolants_ )
