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


''' Vehicles which vend flavors of Icecream debugger. '''



import icecream as _icecream

from . import __
from . import configuration as _cfg
from . import exceptions as _exceptions
from . import printers as _printers


# if __.typx.TYPE_CHECKING: # pragma: no cover
#     import _typeshed


_installer_lock: __.threads.Lock = __.threads.Lock( )
_registrar_lock: __.threads.Lock = __.threads.Lock( )
_self_modulecfg: _cfg.ModuleConfiguration = _cfg.ModuleConfiguration(
    flavors = __.immut.Dictionary(
        note = _cfg.FlavorConfiguration( prefix_emitter = 'NOTE| ' ),
        error = _cfg.FlavorConfiguration( prefix_emitter = 'ERROR| ' ) ) )
_validate_arguments = (
    __.validate_arguments(
        globalvars = globals( ),
        errorclass = _exceptions.ArgumentClassInvalidity ) )


class ModulesConfigurationsRegistry(
    __.accret.Dictionary[ str, _cfg.ModuleConfiguration ]
):
    ''' Accretive dictionary specifically for module registrations. '''

    def __init__(
        self,
        *iterables: __.DictionaryPositionalArgument[
            str, _cfg.ModuleConfiguration ],
        **entries: __.DictionaryNominativeArgument[
            _cfg.ModuleConfiguration ],
    ):
        super( ).__init__( { __.package_name: _self_modulecfg } )
        self.update( *iterables, **entries )


class Omniflavor( __.enum.Enum ):
    ''' Singleton to match any flavor. '''

    Instance = __.enum.auto( )


ActiveFlavors: __.typx.TypeAlias = Omniflavor | frozenset[ _cfg.Flavor ]
ActiveFlavorsLiberal: __.typx.TypeAlias = __.typx.Union[
    Omniflavor,
    __.cabc.Sequence[ _cfg.Flavor ],
    __.cabc.Set[ _cfg.Flavor ],
]
ActiveFlavorsRegistry: __.typx.TypeAlias = (
    __.immut.Dictionary[ str | None, ActiveFlavors ] )
ActiveFlavorsRegistryLiberal: __.typx.TypeAlias = (
    __.cabc.Mapping[ str | None, ActiveFlavorsLiberal ] )
ModulesConfigurationsRegistryLiberal: __.typx.TypeAlias = (
    __.cabc.Mapping[ str, _cfg.ModuleConfiguration ] )
ReportersRegistry: __.typx.TypeAlias = (
    __.accret.Dictionary[
        tuple[ str, _cfg.Flavor ], _icecream.IceCreamDebugger ] )
TraceLevelsRegistry: __.typx.TypeAlias = (
    __.immut.Dictionary[ str | None, int ] )
TraceLevelsRegistryLiberal: __.typx.TypeAlias = (
    __.cabc.Mapping[ str | None, int ] )


builtins_alias_default: __.typx.Annotated[
    str,
    __.typx.Doc( ''' Default alias for global truck in builtins module. ''' ),
] = 'ictr'
modulecfgs: __.typx.Annotated[
    ModulesConfigurationsRegistry,
    __.typx.Doc( ''' Global registry of module configurations. ''' ),
] = ModulesConfigurationsRegistry( )
omniflavor: __.typx.Annotated[
    Omniflavor, __.typx.Doc( ''' Matches any flavor. ''' )
] = Omniflavor.Instance


class Truck( __.immut.DataclassObject ):
    ''' Vends flavors of Icecream debugger. '''

    active_flavors: __.typx.Annotated[
        ActiveFlavorsRegistry,
        __.typx.Doc(
            ''' Mapping of module names to active flavor sets.

                Key ``None`` applies globally. Module-specific entries
                override globals for that module.
            ''' ),
    ] = __.dcls.field( default_factory = ActiveFlavorsRegistry )
    generalcfg: __.typx.Annotated[
        _cfg.VehicleConfiguration,
        __.typx.Doc(
            ''' General configuration.

                Top of configuration inheritance hierarchy.
                Default is suitable for application use.
            ''' ),
    ] = __.dcls.field( default_factory = _cfg.VehicleConfiguration )
    modulecfgs: __.typx.Annotated[
        ModulesConfigurationsRegistry,
        __.typx.Doc(
            ''' Registry of per-module configurations.

                Modules inherit configuration from their parent packages.
                Top-level packages inherit from general instance
                configruration.
            ''' ),
    ] = __.dcls.field( default_factory = lambda: modulecfgs )
    printer_factory: __.typx.Annotated[
        _printers.PrinterFactoryUnion,
        __.typx.Doc(
            ''' Factory which produces callables to output text somewhere.

                May also be writable text stream.
                Factories take two arguments, module name and flavor, and
                return a callable which takes one argument, the string
                produced by a formatter.
            ''' ),
    ] = __.funct.partial( _printers.produce_simple_printer, __.sys.stderr )
    trace_levels: __.typx.Annotated[
        TraceLevelsRegistry,
        __.typx.Doc(
            ''' Mapping of module names to maximum trace depths.

                Key ``None`` applies globally. Module-specific entries
                override globals for that module.
            ''' ),
    ] = __.dcls.field(
        default_factory = lambda: __.immut.Dictionary( { None: -1 } ) )
    _debuggers: __.typx.Annotated[
        ReportersRegistry,
        __.typx.Doc(
            ''' Cache of debugger instances by module and flavor. ''' ),
    ] = __.dcls.field( default_factory = ReportersRegistry )
    _debuggers_lock: __.typx.Annotated[
        __.threads.Lock,
        __.typx.Doc( ''' Access lock for cache of debugger instances. ''' ),
    ] = __.dcls.field( default_factory = __.threads.Lock )

    @_validate_arguments
    def __call__(
        self,
        flavor: _cfg.Flavor, *,
        module_name: __.Absential[ str ] = __.absent,
    ) -> _icecream.IceCreamDebugger:
        ''' Vends flavor of Icecream debugger. '''
        mname = (
            _discover_invoker_module_name( ) if __.is_absent( module_name )
            else module_name )
        cache_index = ( mname, flavor )
        if cache_index in self._debuggers:
            with self._debuggers_lock:
                return self._debuggers[ cache_index ]
        configuration = _produce_ic_configuration( self, mname, flavor )
        control = _cfg.FormatterControl( )
        initargs = _calculate_ic_initargs(
            self, configuration, control, mname, flavor )
        debugger = _icecream.IceCreamDebugger( **initargs )
        if isinstance( flavor, int ):
            trace_level = (
                _calculate_effective_trace_level( self.trace_levels, mname) )
            debugger.enabled = flavor <= trace_level
        elif isinstance( flavor, str ): # pragma: no branch
            active_flavors = (
                _calculate_effective_flavors( self.active_flavors, mname ) )
            debugger.enabled = (
                isinstance( active_flavors, Omniflavor )
                or flavor in active_flavors )
        with self._debuggers_lock:
            self._debuggers[ cache_index ] = debugger
        return debugger

    @_validate_arguments
    def install( self, alias: str = builtins_alias_default ) -> __.typx.Self:
        ''' Installs truck into builtins with provided alias.

            Replaces an existing truck. Preserves global module configurations.

            Library developers should call :py:func:`register_module` instead.
        '''
        import builtins
        with _installer_lock:
            truck_o = getattr( builtins, alias, None )
            if isinstance( truck_o, Truck ):
                self( 'note', module_name = __name__ )(
                    'Installed truck is being replaced.' )
                setattr( builtins, alias, self )
            else:
                __.install_builtin_safely(
                    alias, self, _exceptions.AttributeNondisplacement )
        return self

    @_validate_arguments
    def register_module(
        self,
        name: __.Absential[ str ] = __.absent,
        configuration: __.Absential[ _cfg.ModuleConfiguration ] = __.absent,
    ) -> __.typx.Self:
        ''' Registers configuration for module.

            If no module or package name is given, then the current module is
            inferred.

            If no configuration is provided, then a default is generated.
        '''
        if __.is_absent( name ):
            name = _discover_invoker_module_name( )
        if __.is_absent( configuration ):
            configuration = _cfg.ModuleConfiguration( )
        with _registrar_lock:
            self.modulecfgs[ name ] = configuration
        return self

InstallAliasArgument: __.typx.TypeAlias = __.typx.Annotated[
    str,
    __.typx.Doc(
        ''' Alias under which the truck is installed in builtins. ''' ),
]
ProduceTruckActiveFlavorsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ ActiveFlavorsLiberal | ActiveFlavorsRegistryLiberal ],
    __.typx.Doc(
        ''' Flavors to activate.

            Can be collection, which applies globally across all registered
            modules. Or, can be mapping of module names to sets.

            Module-specific entries merge with global entries.
        ''' ),
]
ProduceTruckEvnActiveFlavorsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ __.typx.Optional[ str ] ],
    __.typx.Doc(
        ''' Name of environment variable for active flavors or ``None``.

            If absent, then a default environment variable name is used.

            If ``None``, then active flavors are not parsed from the process
            environment.

            If active flavors are supplied directly to a function,
            which also accepts this argument, then active flavors are not
            parsed from the process environment.
        ''' ),
]
ProduceTruckEvnTraceLevelsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ __.typx.Optional[ str ] ],
    __.typx.Doc(
        ''' Name of environment variable for trace levels or ``None``.

            If absent, then a default environment variable name is used.

            If ``None``, then trace levels are not parsed from the process
            environment.

            If trace levels are supplied directly to a function,
            which also accepts this argument, then trace levels are not
            parsed from the process environment.
        ''' ),
]
ProduceTruckFlavorsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ _cfg.FlavorsRegistryLiberal ],
    __.typx.Doc( ''' Registry of flavor identifiers to configurations. ''' ),
]
ProduceTruckGeneralcfgArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ _cfg.VehicleConfiguration ],
    __.typx.Doc(
        ''' General configuration for the truck.

            Top of configuration inheritance hierarchy. If absent,
            defaults to a suitable configuration for application use.
        ''' ),
]
ProduceTruckModulecfgsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ ModulesConfigurationsRegistryLiberal ],
    __.typx.Doc(
        ''' Module configurations for the truck.

            If absent, defaults to global modules registry.
        ''' ),
]
ProduceTruckPrinterFactoryArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ _printers.PrinterFactoryUnion ],
    __.typx.Doc(
        ''' Factory which produces callables to output text somewhere.

            May also be writable text stream.
            Factories take two arguments, module name and flavor, and
            return a callable which takes one argument, the string
            produced by a formatter.

            If absent, uses a default.
        ''' ),
]
ProduceTruckTraceLevelsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ int | TraceLevelsRegistryLiberal ],
    __.typx.Doc(
        ''' Maximum trace depths.

            Can be an integer, which applies globally across all registered
            modules. Or, can be a mapping of module names to integers.

            Module-specific entries override global entries.
        ''' ),
]
RegisterModuleFormatterFactoryArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ _cfg.FormatterFactory ],
    __.typx.Doc(
        ''' Factory which produces formatter callable.

            Takes formatter control, module name, and flavor as arguments.
            Returns formatter to convert an argument to a string.
        ''' ),
]
RegisterModuleIncludeContextArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ bool ],
    __.typx.Doc( ''' Include stack frame with output? ''' ),
]
RegisterModuleNameArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ str ],
    __.typx.Doc(
        ''' Name of the module to register.

            If absent, infers the current module name.
        ''' ),
]
RegisterModulePrefixEmitterArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ _cfg.PrefixEmitterUnion ],
    __.typx.Doc(
        ''' String or factory which produces output prefix string.

            Factory takes formatter control, module name, and flavor as
            arguments. Returns prefix string.
        ''' ),
]


def active_flavors_from_environment(
    evname: __.Absential[ str ] = __.absent
) -> ActiveFlavorsRegistry:
    ''' Extracts active flavors from named environment variable. '''
    active_flavors: ActiveFlavorsRegistryLiberal = { }
    name = 'ICTRUCK_ACTIVE_FLAVORS' if __.is_absent( evname ) else evname
    value = __.os.getenv( name, '' )
    for part in value.split( '+' ):
        if not part: continue
        if ':' in part:
            mname, flavors = part.split( ':', 1 )
        else: mname, flavors = None, part
        match flavors:
            case '*': active_flavors[ mname ] = omniflavor
            case _: active_flavors[ mname ] = flavors.split( ',' )
    return __.immut.Dictionary( {
        mname:
            flavors if isinstance( flavors, Omniflavor )
            else frozenset( flavors )
        for mname, flavors in active_flavors.items( ) } )


def trace_levels_from_environment(
    evname: __.Absential[ str ] = __.absent
) -> TraceLevelsRegistry:
    ''' Extracts trace levels from named environment variable. '''
    trace_levels: TraceLevelsRegistryLiberal = { None: -1 }
    name = 'ICTRUCK_TRACE_LEVELS' if __.is_absent( evname ) else evname
    value = __.os.getenv( name, '' )
    for part in value.split( '+' ):
        if not part: continue
        if ':' in part: mname, level = part.split( ':', 1 )
        else: mname, level = None, part
        if not level.isdigit( ):
            __.warnings.warn(
                f"Non-integer trace level {level!r} "
                f"in environment variable {name!r}." )
            continue
        trace_levels[ mname ] = int( level )
    return __.immut.Dictionary( trace_levels )


@_validate_arguments
def install( # noqa: PLR0913
    alias: InstallAliasArgument = builtins_alias_default,
    active_flavors: ProduceTruckActiveFlavorsArgument = __.absent,
    generalcfg: ProduceTruckGeneralcfgArgument = __.absent,
    printer_factory: ProduceTruckPrinterFactoryArgument = __.absent,
    trace_levels: ProduceTruckTraceLevelsArgument = __.absent,
    evname_active_flavors: ProduceTruckEvnActiveFlavorsArgument = __.absent,
    evname_trace_levels: ProduceTruckEvnTraceLevelsArgument = __.absent,
) -> Truck:
    ''' Produces truck and installs it into builtins with alias.

        Replaces an existing truck, preserving global module configurations.

        Library developers should call :py:func:`register_module` instead.
    '''
    truck = produce_truck(
        active_flavors = active_flavors,
        generalcfg = generalcfg,
        printer_factory = printer_factory,
        trace_levels = trace_levels,
        evname_active_flavors = evname_active_flavors,
        evname_trace_levels = evname_trace_levels )
    return truck.install( alias = alias )


@_validate_arguments
def produce_truck( # noqa: PLR0913
    active_flavors: ProduceTruckActiveFlavorsArgument = __.absent,
    generalcfg: ProduceTruckGeneralcfgArgument = __.absent,
    modulecfgs: ProduceTruckModulecfgsArgument = __.absent,
    printer_factory: ProduceTruckPrinterFactoryArgument = __.absent,
    trace_levels: ProduceTruckTraceLevelsArgument = __.absent,
    evname_active_flavors: ProduceTruckEvnActiveFlavorsArgument = __.absent,
    evname_trace_levels: ProduceTruckEvnTraceLevelsArgument = __.absent,
) -> Truck:
    ''' Produces icecream truck with some shorthand argument values. '''
    # TODO: Deeper validation of active flavors and trace levels.
    # TODO: Deeper validation of printer factory.
    initargs: dict[ str, __.typx.Any ] = { }
    if not __.is_absent( generalcfg ):
        initargs[ 'generalcfg' ] = generalcfg
    if not __.is_absent( modulecfgs ):
        initargs[ 'modulecfgs' ] = ModulesConfigurationsRegistry(
            {   mname: configuration for mname, configuration
                in modulecfgs.items( ) } )
    if not __.is_absent( printer_factory ):
        initargs[ 'printer_factory' ] = printer_factory
    _add_truck_initarg_active_flavors(
        initargs, active_flavors, evname_active_flavors )
    _add_truck_initarg_trace_levels(
        initargs, trace_levels, evname_trace_levels )
    return Truck( **initargs )


@_validate_arguments
def register_module(
    name: RegisterModuleNameArgument = __.absent,
    flavors: ProduceTruckFlavorsArgument = __.absent,
    formatter_factory: RegisterModuleFormatterFactoryArgument = __.absent,
    include_context: RegisterModuleIncludeContextArgument = __.absent,
    prefix_emitter: RegisterModulePrefixEmitterArgument = __.absent,
) -> _cfg.ModuleConfiguration:
    ''' Registers module configuration on the builtin truck.

        If no truck exists in builtins, installs one which produces null
        printers.

        Intended for library developers to configure debugging flavors
        without overriding anything set by the application or other libraries.
        Application developers should call :py:func:`install` instead.
    '''
    import builtins
    truck = getattr( builtins, builtins_alias_default, None )
    if not isinstance( truck, Truck ):
        truck = Truck( )
        __.install_builtin_safely(
            builtins_alias_default,
            truck,
            _exceptions.AttributeNondisplacement )
    nomargs: dict[ str, __.typx.Any ] = { }
    if not __.is_absent( flavors ):
        nomargs[ 'flavors' ] = __.immut.Dictionary( flavors )
    if not __.is_absent( formatter_factory ):
        nomargs[ 'formatter_factory' ] = formatter_factory
    if not __.is_absent( include_context ):
        nomargs[ 'include_context' ] = include_context
    if not __.is_absent( prefix_emitter ):
        nomargs[ 'prefix_emitter' ] = prefix_emitter
    configuration = _cfg.ModuleConfiguration( **nomargs )
    return truck.register_module( name = name, configuration = configuration )


def _add_truck_initarg_active_flavors(
    initargs: dict[ str, __.typx.Any ],
    active_flavors: ProduceTruckActiveFlavorsArgument = __.absent,
    evname_active_flavors: ProduceTruckEvnActiveFlavorsArgument = __.absent,
) -> None:
    name = 'active_flavors'
    if not __.is_absent( active_flavors ):
        if isinstance( active_flavors, Omniflavor ):
            initargs[ name ] = __.immut.Dictionary(
                { None: active_flavors } )
        elif isinstance( active_flavors, ( __.cabc.Sequence,  __.cabc.Set ) ):
            initargs[ name ] = __.immut.Dictionary(
                { None: frozenset( active_flavors ) } )
        else:
            initargs[ name ] = __.immut.Dictionary( {
                mname:
                    flavors if isinstance( flavors, Omniflavor )
                    else frozenset( flavors )
                for mname, flavors in active_flavors.items( ) } )
    elif evname_active_flavors is not None:
        initargs[ name ] = (
            active_flavors_from_environment( evname = evname_active_flavors ) )


def _add_truck_initarg_trace_levels(
    initargs: dict[ str, __.typx.Any ],
    trace_levels: ProduceTruckTraceLevelsArgument = __.absent,
    evname_trace_levels: ProduceTruckEvnTraceLevelsArgument = __.absent,
) -> None:
    name = 'trace_levels'
    if not __.is_absent( trace_levels ):
        if isinstance( trace_levels, int ):
            initargs[ name ] = __.immut.Dictionary( { None: trace_levels } )
        else:
            trace_levels_: TraceLevelsRegistryLiberal = { None: -1 }
            trace_levels_.update( trace_levels )
            initargs[ name ] = __.immut.Dictionary( trace_levels_ )
    elif evname_trace_levels is not None:
        initargs[ name ] = (
            trace_levels_from_environment( evname = evname_trace_levels ) )


def _calculate_effective_flavors(
    flavors: ActiveFlavorsRegistry, mname: str
) -> ActiveFlavors:
    result_ = flavors.get( None ) or frozenset( )
    if isinstance( result_, Omniflavor ): return result_
    result = result_
    for mname_ in _iterate_module_name_ancestry( mname ):
        if mname_ in flavors:
            result_ = flavors.get( mname_ ) or frozenset( )
            if isinstance( result_, Omniflavor ): return result_
            result |= result_
    return result


def _calculate_effective_trace_level(
    levels: TraceLevelsRegistry, mname: str
) -> int:
    result = levels.get( None, -1 )
    for mname_ in _iterate_module_name_ancestry( mname ):
        if mname_ in levels:
            result = levels[ mname_ ]
    return result


def _calculate_ic_initargs(
    truck: Truck,
    configuration: __.immut.Dictionary[ str, __.typx.Any ],
    control: _cfg.FormatterControl,
    mname: str,
    flavor: _cfg.Flavor,
) -> dict[ str, __.typx.Any ]:
    nomargs: dict[ str, __.typx.Any ] = { }
    nomargs[ 'argToStringFunction' ] = (
        configuration[ 'formatter_factory' ]( control, mname, flavor ) )
    nomargs[ 'includeContext' ] = configuration[ 'include_context' ]
    if isinstance( truck.printer_factory, __.io.TextIOBase ):
        printer = __.funct.partial( print, file = truck.printer_factory )
    else: printer = truck.printer_factory( mname, flavor )
    nomargs[ 'outputFunction' ] = printer
    prefix_emitter = configuration[ 'prefix_emitter' ]
    nomargs[ 'prefix' ] = (
        prefix_emitter if isinstance( prefix_emitter, str )
        else prefix_emitter( mname, flavor ) )
    return nomargs


def _dict_from_dataclass( objct: object ) -> dict[ str, __.typx.Any ]:
    # objct = __.typx.cast( _typeshed.DataclassInstance, objct )
    return {
        field.name: getattr( objct, field.name )
        for field in __.dcls.fields( objct ) # pyright: ignore[reportArgumentType]
        if not field.name.startswith( '_' ) }


def _discover_invoker_module_name( ) -> str:
    frame = __.inspect.currentframe( )
    while frame: # pragma: no branch
        module = __.inspect.getmodule( frame )
        if module is None:
            if '<stdin>' == frame.f_code.co_filename: # pragma: no cover
                name = '__main__'
                break
            raise _exceptions.ModuleInferenceFailure
        name = module.__name__
        if not name.startswith( f"{__.package_name}." ): break
        frame = frame.f_back
    return name


def _iterate_module_name_ancestry( name: str ) -> __.cabc.Iterator[ str ]:
    parts = name.split( '.' )
    for i in range( len( parts ) ):
        yield '.'.join( parts[ : i + 1 ] )


def _merge_ic_configuration(
    base: dict[ str, __.typx.Any ], update_objct: object,
) -> dict[ str, __.typx.Any ]:
    update: dict[ str, __.typx.Any ] = _dict_from_dataclass( update_objct )
    result: dict[ str, __.typx.Any ] = { }
    result[ 'flavors' ] = (
            dict( base.get( 'flavors', dict( ) ) )
        |   dict( update.get( 'flavors', dict( ) ) ) )
    for ename in ( 'formatter_factory', 'include_context', 'prefix_emitter' ):
        uvalue = update.get( ename )
        if uvalue is not None: result[ ename ] = uvalue
        elif ename in base: result[ ename ] = base[ ename ]
    return result


def _produce_ic_configuration(
    vehicle: Truck, mname: str, flavor: _cfg.Flavor
) -> __.immut.Dictionary[ str, __.typx.Any ]:
    fconfigs: list[ _cfg.FlavorConfiguration ] = [ ]
    vconfig = vehicle.generalcfg
    configd: dict[ str, __.typx.Any ] = {
        field.name: getattr( vconfig, field.name )
        for field in __.dcls.fields( vconfig )
        if not field.name.startswith( '_' ) }
    if flavor in vconfig.flavors:
        fconfigs.append( vconfig.flavors[ flavor ] )
    for mname_ in _iterate_module_name_ancestry( mname ):
        if mname_ not in vehicle.modulecfgs: continue
        mconfig = vehicle.modulecfgs[ mname_ ]
        configd = _merge_ic_configuration( configd, mconfig )
        if flavor in mconfig.flavors:
            fconfigs.append( mconfig.flavors[ flavor ] )
    if not fconfigs: raise _exceptions.FlavorInavailability( flavor )
    # Apply collected flavor configs after general and module configs.
    # (Applied in top-down order for correct overrides.)
    for fconfig in fconfigs:
        configd = _merge_ic_configuration( configd, fconfig )
    return __.immut.Dictionary( configd )
