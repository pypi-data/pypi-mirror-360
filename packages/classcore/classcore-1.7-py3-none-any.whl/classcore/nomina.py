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


''' Catalog of common type aliases. '''


from . import __


AttributesNamer: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ str, str ], str ],
    __.ddoc.Doc(
        ''' Names attribute from level and core arguments.

            Level will be one of 'class', 'instances', or 'instance'.
            Core will be the core of the name as supplied this package.

            Can be used by downstream packages to determine names of
            bookkeeping attributes assigned by this package.
        ''' ),
]

Decorator: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ type[ __.U ] ], type[ __.U ] ],
    __.ddoc.Doc(
        ''' Class decorator.

            Takes class argument and returns class.
        ''' ),
]
Decorators: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Sequence[ Decorator[ __.U ] ],
    __.ddoc.Doc(
        ''' Sequence of class decorators.

            Each element takes a class argument and returns a class.
        ''' ),
]
DecoratorsMutable: __.typx.TypeAlias = __.typx.Annotated[
   __.cabc.MutableSequence[ Decorator[ __.U ] ],
    __.ddoc.Doc(
        ''' Sequence of class decorators.

            Each element takes a class argument and returns a class.

            Decorators may be inserted or removed from sequence.
        ''' ),
]

DecorationPreparer: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ type[ __.U ], DecoratorsMutable[ __.U ] ], None ],
    __.ddoc.Doc(
        ''' Class decoration preparer.

            Takes class and mutable sequence of decorators as arguments.
            Can alter the sequence.
        ''' ),
]
DecorationPreparers: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Sequence[ DecorationPreparer[ __.U ] ],
    __.ddoc.Doc(
        ''' Sequence of class decoration preparers.

            Each element takes class and mutable sequence of decorators as
            arguments. And, each element can alter the sequence.
        ''' ),
]

ClassConstructorLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ ..., type ],
    __.ddoc.Doc(
        ''' Bound class constructor function.

            Usually from ``super( ).__new__`` or a partial function.
        ''' ),
]
InitializerLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ ..., None ],
    __.ddoc.Doc(
        ''' Bound initializer function.

            Usually from ``super( ).__init__`` or a partial function.
        ''' ),
]
AssignerLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ str, __.typx.Any ], None ],
    __.ddoc.Doc(
        ''' Bound attributes assigner function.

            Usually from ``super( ).__setattr__`` or a partial function.
        ''' ),
]
DeleterLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ str ], None ],
    __.ddoc.Doc(
        ''' Bound attributes deleter function.

            Usually from ``super( ).__delattr__`` or a partial function.
        ''' ),
]
SurveyorLigation: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ ], __.cabc.Iterable[ str ] ],
    __.ddoc.Doc(
        ''' Bound attributes surveyor function.

            Usually from ``super( ).__dir__`` or a partial function.
        ''' ),
]


ClassConstructionPreprocessor: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [
            type[ type ],               # metaclass
            str,                        # class name
            list[ type ],               # bases (mutable)
            dict[ str, __.typx.Any ],   # namespace (mutable)
            dict[ str, __.typx.Any ],   # arguments (mutable)
            DecoratorsMutable[ __.U ],  # decorators (mutable)
        ],
        None
    ],
    __.ddoc.Doc(
        ''' Processes class data before construction.

            For use cases, such as argument conversion.
        ''' ),
]
ClassConstructionPreprocessors: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Sequence[ ClassConstructionPreprocessor[ __.U ] ],
    __.ddoc.Doc( ''' Processors to apply before construction of class. ''' ),
]
ClassConstructionPostprocessor: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ type, DecoratorsMutable[ __.U ] ], None ],
    __.ddoc.Doc(
        ''' Processes class before decoration.

            For use cases, such as decorator list manipulation.
        ''' ),
]
ClassConstructionPostprocessors: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Sequence[ ClassConstructionPostprocessor[ __.U ] ],
    __.ddoc.Doc(
        ''' Processors to apply before decoration of class. ''' ),
]
# TODO: ClassInitializationPreparer (arguments mutation)
ClassInitializationCompleter: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ type ], None ],
    __.ddoc.Doc(
        ''' Completes initialization of class.

            For use cases, such as enabling immutability once all other
            initialization has occurred.
        ''' ),
]
ClassInitializationCompleters: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Sequence[ ClassInitializationCompleter ],
    __.ddoc.Doc(
        ''' Processors to apply at final stage of class initialization. ''' ),
]


ClassConstructor: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [
            type,
            ClassConstructorLigation,
            str,
            tuple[ type, ... ],
            dict[ str, __.typx.Any ],
            __.NominativeArguments,
            Decorators[ __.U ],
        ],
        type
    ],
    __.ddoc.Doc( ''' Constructor to use with metaclass. ''' ),
]
ClassInitializer: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [
            type,
            InitializerLigation,
            __.PositionalArguments,
            __.NominativeArguments,
        ],
        None
    ],
    __.ddoc.Doc( ''' Initializer to use with metaclass. ''' ),
]
