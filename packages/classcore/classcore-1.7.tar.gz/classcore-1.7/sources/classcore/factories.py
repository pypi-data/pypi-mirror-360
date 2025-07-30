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


''' Factories which produce metaclass implementations. '''


from . import __
from . import decorators as _decorators
from . import nomina as _nomina
from . import utilities as _utilities


def produce_class_constructor(
    attributes_namer: _nomina.AttributesNamer,
    preprocessors: _nomina.ClassConstructionPreprocessors[ __.T ] = ( ),
    postprocessors: _nomina.ClassConstructionPostprocessors[ __.T ] = ( ),
) -> _nomina.ClassConstructor[ __.T ]:
    ''' Produces constructors for classes. '''

    def construct( # noqa: PLR0913
        clscls: type[ __.T ],
        superf: _nomina.ClassConstructorLigation,
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ],
        arguments: __.NominativeArguments,
        decorators: _nomina.Decorators[ __.T ],
    ) -> type:
        ''' Constructs class, applying decorators and hooks. '''
        bases_ = list( bases )
        arguments_ = dict( arguments )
        decorators_ = list( decorators )
        for preprocessor in preprocessors:
            preprocessor(
                clscls, name, bases_, namespace, arguments_, decorators_ )
        cls = superf( clscls, name, tuple( bases_ ), namespace, **arguments_ )
        # Some decorators create new classes, which invokes this method again.
        # Short-circuit to prevent recursive decoration and other tangles.
        progress_name = attributes_namer( 'class', 'in_progress' )
        progress_name_m = _utilities.mangle_name( cls, progress_name )
        in_progress = getattr( cls, progress_name_m, False )
        if in_progress: return cls
        setattr( cls, progress_name_m, True )
        for postprocessor in postprocessors: postprocessor( cls, decorators_ )
        cls = _decorators.apply_decorators( cls, decorators_ )
        setattr( cls, progress_name_m, False )
        return cls

    return construct


def produce_class_initializer(
    attributes_namer: _nomina.AttributesNamer,
    completers: _nomina.ClassInitializationCompleters = ( ),
) -> _nomina.ClassInitializer:
    ''' Produces initializers for classes. '''

    def initialize(
        cls: type,
        superf: _nomina.InitializerLigation,
        posargs: __.PositionalArguments,
        nomargs: __.NominativeArguments,
    ) -> None:
        ''' Initializes class, applying hooks. '''
        superf( *posargs, **nomargs )
        progress_name = attributes_namer( 'class', 'in_progress' )
        progress_name_m = _utilities.mangle_name( cls, progress_name )
        in_progress = getattr( cls, progress_name_m, False )
        if in_progress: return # If non-empty, then not top-level.
        delattr( cls, progress_name_m )
        for completer in completers: completer( cls )

    return initialize
