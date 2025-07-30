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


''' Catalog of common names and type aliases. '''
# ruff: noqa: F403,F405


from . import __
from ..nomina import *


concealment_label = 'concealment'
immutability_label = 'immutability'


BehaviorExclusionNames: __.typx.TypeAlias = __.cabc.Set[ str ]
BehaviorExclusionNamesOmni: __.typx.TypeAlias = (
    BehaviorExclusionNames | __.typx.Literal[ '*' ] )
BehaviorExclusionPredicate: __.typx.TypeAlias = (
    __.cabc.Callable[ [ str ], bool ] )
BehaviorExclusionPredicates: __.typx.TypeAlias = (
    __.cabc.Sequence[ BehaviorExclusionPredicate ] )
BehaviorExclusionRegex: __.typx.TypeAlias = __.re.Pattern[ str ]
BehaviorExclusionRegexes: __.typx.TypeAlias = (
    __.cabc.Sequence[ BehaviorExclusionRegex ] )
BehaviorExclusionVerifier: __.typx.TypeAlias = (
    str | BehaviorExclusionRegex | BehaviorExclusionPredicate )
BehaviorExclusionVerifiers: __.typx.TypeAlias = (
    __.cabc.Sequence[ BehaviorExclusionVerifier ] )
BehaviorExclusionVerifiersOmni: __.typx.TypeAlias = (
    BehaviorExclusionVerifiers | __.typx.Literal[ '*' ] )
ErrorClassProvider: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ str ], type[ Exception ] ],
    __.ddoc.Doc(
        ''' Takes name of exception class and returns corresponding class.

            Can be used by downstream packages to provide exceptions from their
            own hierarchies rather than the hierarchy from this package.
        ''' ),
]


class AssignerCore( __.typx.Protocol ):
    ''' Core implementation of attributes assigner. '''

    @staticmethod
    def __call__( # noqa: PLR0913 # pragma: no branch
        obj: object, /, *,
        ligation: AssignerLigation,
        attributes_namer: AttributesNamer,
        error_class_provider: ErrorClassProvider,
        level: str,
        name: str,
        value: __.typx.Any,
    ) -> None: raise NotImplementedError


class DeleterCore( __.typx.Protocol ):
    ''' Core implementation of attributes deleter. '''

    @staticmethod
    def __call__( # noqa: PLR0913 # pragma: no branch
        obj: object, /, *,
        ligation: DeleterLigation,
        attributes_namer: AttributesNamer,
        error_class_provider: ErrorClassProvider,
        level: str,
        name: str,
    ) -> None: raise NotImplementedError


class SurveyorCore( __.typx.Protocol ):
    ''' Core implementation of attributes surveyor. '''

    @staticmethod
    def __call__( # pragma: no branch
        obj: object, /, *,
        ligation: SurveyorLigation,
        attributes_namer: AttributesNamer,
        level: str,
    ) -> __.cabc.Iterable[ str ]: raise NotImplementedError


class ClassPreparer( __.typx.Protocol ):
    ''' Prepares class for decorator application. '''

    @staticmethod
    def __call__( # pragma: no branch
        class_: type,
        decorators: DecoratorsMutable[ __.U ], /, *,
        attributes_namer: AttributesNamer,
    ) -> None: raise NotImplementedError


DynadocConfiguration: __.typx.TypeAlias = __.cabc.Mapping[ str, __.typx.Any ]
# TODO: Use argument type aliases from 'dynadoc' package.
DynadocContextArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.ddoc.Context,
    __.ddoc.Doc(
        ''' Dynadoc context.

            Renderer, dictionaries for resolution of stringified annotations,
            etc....
        ''' ),
]
DynadocIntrospectionArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.ddoc.IntrospectionControl,
    __.ddoc.Doc(
        ''' Dynadoc introspection control.

            Which kinds of object to recursively introspect?
            Scan unnannotated attributes?
            Consider base classes?
            Etc...
        ''' ),
]
DynadocPreserveArgument: __.typx.TypeAlias = __.typx.Annotated[
    bool, __.ddoc.Doc( ''' Preserve existing docstring? ''' )
]
DynadocTableArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Mapping[ str, str ],
    __.ddoc.Doc( ''' Table of documentation fragments. ''' ),
]
ProduceDynadocConfigurationReturn: __.typx.TypeAlias = __.typx.Annotated[
    DynadocConfiguration,
    __.ddoc.Doc(
        ''' Dynadoc configuration dictionary.

            Suitable as a keyword expansion (``**``) argument to
            ``assign_module_docstring`` or ``with_docstring``.
        ''' ),
]
