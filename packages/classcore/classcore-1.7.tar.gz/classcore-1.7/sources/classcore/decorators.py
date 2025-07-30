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


''' Utilities for the decoration of classes, including metaclasses. '''


from . import __
from . import nomina as _nomina
from . import utilities as _utilities


def apply_decorators(
    cls: type[ __.U ], decorators: _nomina.Decorators[ __.U ]
) -> type:
    ''' Applies sequence of decorators to class.

        If decorators replace classes (e.g., ``dataclass( slots = True )``),
        then any necessary repairs are performed on the replacement class with
        respect to the original. E.g., on CPython, the class closure cell is
        repaired so that ``super`` operates correctly in methods of the
        replacement class.
    '''
    for decorator in decorators:
        cls_ = decorator( cls )
        if cls is cls_: continue # Simple mutation. No replacement.
        _utilities.repair_class_reproduction( cls, cls_ )
        cls = cls_ # Use the replacement class.
    return cls


def decoration_by(
    *decorators: _nomina.Decorator[ __.U ],
    preparers: _nomina.DecorationPreparers[ __.U ] = ( ),
) -> _nomina.Decorator[ __.U ]:
    ''' Class decorator which applies other class decorators.

        Useful to apply a stack of decorators as a sequence.

        Can optionally execute a sequence of decoration preparers before
        applying the decorators proper. These can be used to alter the
        decorators list itself, such as to inject decorators based on
        introspection of the class.
    '''
    def decorate( cls: type[ __.U ] ) -> type[ __.U ]:
        decorators_ = list( decorators )
        for preparer in preparers: preparer( cls, decorators_ )
        return apply_decorators( cls, decorators_ )

    return decorate


def produce_class_construction_decorator(
    attributes_namer: _nomina.AttributesNamer,
    constructor: _nomina.ClassConstructor[ __.T ],
) -> _nomina.Decorator[ __.T ]:
    ''' Produces metaclass decorator to control class construction.

        Decorator overrides ``__new__`` on metaclass.
    '''
    def decorate( clscls: type[ __.T ] ) -> type[ __.T ]:
        original = __.typx.cast(
            _nomina.ClassConstructorLigation | None,
            clscls.__dict__.get( '__new__' ) ) # pyright: ignore

        if original is None:

            def construct_with_super(
                clscls_: type[ __.T ],
                name: str,
                bases: tuple[ type, ... ],
                namespace: dict[ str, __.typx.Any ], *,
                decorators: _nomina.Decorators[ __.T ] = ( ),
                **arguments: __.typx.Any,
            ) -> type[ object ]:
                superf = super( clscls, clscls_ ).__new__
                # TODO? Short-circuit if not at start of MRO.
                return constructor(
                    clscls_, superf,
                    name, bases, namespace, arguments, decorators )

            setattr( clscls, '__new__', construct_with_super )

        else:

            def construct_with_original(
                clscls_: type[ __.T ],
                name: str,
                bases: tuple[ type, ... ],
                namespace: dict[ str, __.typx.Any ], *,
                decorators: _nomina.Decorators[ __.T ] = ( ),
                **arguments: __.typx.Any,
            ) -> type[ object ]:
                # TODO? Short-circuit if not at start of MRO.
                return constructor(
                    clscls_, original,
                    name, bases, namespace, arguments, decorators )

            setattr( clscls, '__new__', construct_with_original )

        return clscls

    return decorate


def produce_class_initialization_decorator(
    attributes_namer: _nomina.AttributesNamer,
    initializer: _nomina.ClassInitializer,
) -> _nomina.Decorator[ __.T ]:
    ''' Produces metaclass decorator to control class initialization.

        Decorator overrides ``__init__`` on metaclass.
    '''
    def decorate( clscls: type[ __.T ] ) -> type[ __.T ]:
        original = __.typx.cast(
            _nomina.InitializerLigation | None,
            clscls.__dict__.get( '__init__' ) ) # pyright: ignore

        if original is None:

            def initialize_with_super(
                cls: type, *posargs: __.typx.Any, **nomargs: __.typx.Any
            ) -> None:
                ligation = super( clscls, cls ).__init__
                # TODO? Short-circuit if not at start of MRO.
                initializer( cls, ligation, posargs, nomargs )

            clscls.__init__ = initialize_with_super

        else:

            @__.funct.wraps( original )
            def initialize_with_original(
                cls: type, *posargs: __.typx.Any, **nomargs: __.typx.Any
            ) -> None:
                ligation = __.funct.partial( original, cls )
                # TODO? Short-circuit if not at start of MRO.
                initializer( cls, ligation, posargs, nomargs )

            clscls.__init__ = initialize_with_original

        return clscls

    return decorate
