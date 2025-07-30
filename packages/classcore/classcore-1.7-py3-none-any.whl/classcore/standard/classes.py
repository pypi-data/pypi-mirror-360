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


''' Standard classes and class factories. '''


from . import __
from . import decorators as _decorators
from . import dynadoc as _dynadoc
from . import nomina as _nomina


_dynadoc_configuration = (
    _dynadoc.produce_dynadoc_configuration( table = __.fragments ) )
_class_factory = __.funct.partial(
    _decorators.class_factory, dynadoc_configuration = _dynadoc_configuration )


class ClassFactoryExtraArguments( __.typx.TypedDict, total = False ):
    ''' Extra arguments accepted by standard metaclasses. '''

    class_mutables: _nomina.BehaviorExclusionVerifiersOmni
    class_visibles: _nomina.BehaviorExclusionVerifiersOmni
    dynadoc_configuration: _nomina.DynadocConfiguration
    instances_assigner_core: _nomina.AssignerCore
    instances_deleter_core: _nomina.DeleterCore
    instances_surveyor_core: _nomina.SurveyorCore
    instances_ignore_init_arguments: bool
    instances_mutables: _nomina.BehaviorExclusionVerifiersOmni
    instances_visibles: _nomina.BehaviorExclusionVerifiersOmni


@_class_factory( )
class Class( type ):
    ''' Metaclass for standard classes. '''

    _dynadoc_fragments_ = (
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
        'cfc instance conceal', 'cfc instance protect' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: _nomina.Decorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class Dataclass( type ):
    ''' Metaclass for standard dataclasses. '''

    _dynadoc_fragments_ = (
        'cfc produce dataclass',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
        'cfc instance conceal', 'cfc instance protect' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: _nomina.Decorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
@__.typx.dataclass_transform( kw_only_default = True )
class DataclassMutable( type ):
    ''' Metaclass for dataclasses with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'cfc produce dataclass',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
        'cfc instance conceal' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: _nomina.Decorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
class ProtocolClass( type( __.typx.Protocol ) ):
    ''' Metaclass for standard protocol classes. '''

    _dynadoc_fragments_ = (
        'cfc produce protocol class',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
        'cfc instance conceal', 'cfc instance protect' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: _nomina.Decorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class ProtocolDataclass( type( __.typx.Protocol ) ):
    ''' Metaclass for standard protocol dataclasses. '''

    _dynadoc_fragments_ = (
        'cfc produce protocol class', 'cfc produce dataclass',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
        'cfc instance conceal', 'cfc instance protect' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: _nomina.Decorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
@__.typx.dataclass_transform( kw_only_default = True )
class ProtocolDataclassMutable( type( __.typx.Protocol ) ):
    ''' Metaclass for protocol dataclasses with mutable instance attributes.
    '''

    _dynadoc_fragments_ = (
        'cfc produce protocol class', 'cfc produce dataclass',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
        'cfc instance conceal' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: _nomina.Decorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


class Object( metaclass = Class ):
    ''' Standard base class. '''

    _dynadoc_fragments_ = (
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal', 'class instance protect' )


class ObjectMutable( metaclass = Class, instances_mutables = '*' ):
    ''' Base class with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal' )


class DataclassObject( metaclass = Dataclass ):
    ''' Standard base dataclass. '''

    _dynadoc_fragments_ = (
        'dataclass',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal', 'class instance protect' )


class DataclassObjectMutable( metaclass = DataclassMutable ):
    ''' Base dataclass with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'dataclass',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal' )


class Protocol( __.typx.Protocol, metaclass = ProtocolClass ):
    ''' Standard base protocol class. '''

    _dynadoc_fragments_ = (
        'protocol class',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal', 'class instance protect' )


class ProtocolMutable(
    __.typx.Protocol, metaclass = ProtocolClass, instances_mutables = '*'
):
    ''' Base protocol class with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'protocol class',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal' )


class DataclassProtocol(
    __.typx.Protocol, metaclass = ProtocolDataclass,
):
    ''' Standard base protocol dataclass. '''

    _dynadoc_fragments_ = (
        'dataclass', 'protocol class',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal', 'class instance protect' )


class DataclassProtocolMutable(
    __.typx.Protocol, metaclass = ProtocolDataclassMutable,
):
    ''' Base protocol dataclass with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'dataclass', 'protocol class',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal' )
