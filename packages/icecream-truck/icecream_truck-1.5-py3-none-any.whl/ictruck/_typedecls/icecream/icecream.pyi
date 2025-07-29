from collections.abc import Callable

from typing_extensions import Any

DEFAULT_ARG_TO_STRING_FUNCTION: Callable[ [ Any ], str ]
DEFAULT_OUTPUT_FUNCTION: Callable[ [ str ], None ]
DEFAULT_PREFIX: str

class IceCreamDebugger:

    enabled: bool = ...
    lineWrapWidth: int = ...
    contextDelimiter: str = ...

    def __init__(
        self,
        prefix: str = ...,
        outputFunction: Callable[ [ str ], None ] = ...,
        argToStringFunction: Callable[ [ Any ], str ] = ...,
        includeContext: bool = ...,
        contextAbsPath: bool = ...,
    ) -> None:
        ...

    def __call__( self, *args: Any ) -> tuple[ Any, ... ] | None:
        ...

    def format( self, *args: Any ) -> str:
        ...

    def enable( self ) -> None:
        ...

    def disable( self ) -> None:
        ...

    def configureOutput(
        self,
        prefix: str = ...,
        outputFunction: Callable[ ..., str ] = ...,
        argToStringFunction: Callable[ [ Any ], str ] = ...,
        includeContext: bool = ...,
        contextAbsPath: bool = ...
    ) -> None:
        ...


ic: IceCreamDebugger = ...
