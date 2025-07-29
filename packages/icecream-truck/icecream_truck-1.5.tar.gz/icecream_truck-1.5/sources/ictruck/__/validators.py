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


''' Validators for internal use. '''



from . import imports as __


def validate_arguments(
    globalvars: dict[ str, __.typx.Any ],
    errorclass: type[ Exception ],
):
    ''' Decorator factory which produces argument validators. '''

    def decorate( function: __.cabc.Callable[ ..., __.typx.Any ] ):
        ''' Decorates function to be validated. '''

        @__.funct.wraps( function )
        def validate( *posargs: __.typx.Any, **nomargs: __.typx.Any ):
            ''' Validates arguments before invocation. '''
            signature = __.inspect.signature( function )
            inspectee = signature.bind( *posargs, **nomargs )
            inspectee.apply_defaults( )
            for name, value in inspectee.arguments.items( ):
                param = signature.parameters[ name ]
                annotation = param.annotation
                if __.is_absent( value ): continue
                if annotation is param.empty: continue
                classes = _reduce_annotation(
                    annotation, globalvars = globalvars )
                if not isinstance( value, classes ):
                    raise errorclass( name, classes )
            return function( *posargs, **nomargs )

        return validate

    return decorate


def _reduce_annotation(
    annotation: __.typx.Any, globalvars: dict[ str, __.typx.Any ]
) -> tuple[ type, ... ]:
    if isinstance( annotation, str ):
        return _reduce_annotation(
            eval( annotation, globalvars ), # noqa: S307
            globalvars = globalvars )
    origin = __.typx.get_origin( annotation )
    if isinstance( annotation, __.types.UnionType ) or origin is __.typx.Union:
        return tuple( __.itert.chain.from_iterable(
            map(
                lambda a: _reduce_annotation( a, globalvars = globalvars ),
                __.typx.get_args( annotation ) ) ) )
    if origin is None: return ( annotation, )
    if origin is __.typx.Annotated:
        return _reduce_annotation(
            annotation.__origin__, globalvars = globalvars )
    # TODO? Other special forms.
    return ( origin, )
