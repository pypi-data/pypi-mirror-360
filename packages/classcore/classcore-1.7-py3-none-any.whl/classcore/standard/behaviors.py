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


''' Implementations for standard behaviors. '''
# TODO? Support introspection of PEP 593 annotations for behavior exclusions.
#       Maybe enum for mutability and visibility.


from .. import utilities as _utilities
from . import __
from . import nomina as _nomina


def access_core_function( # noqa: PLR0913
    cls: type, /, *,
    attributes_namer: _nomina.AttributesNamer,
    arguments: __.cabc.Mapping[ str, __.typx.Any ],
    level: str,
    name: str,
    default: __.cabc.Callable[ ..., __.typx.Any ],
) -> __.cabc.Callable[ ..., __.typx.Any ]:
    ''' Accesses core behavior function.

        First checks for override argument, then checks for heritable
        attribute. Finally, falls back to provided default.
    '''
    argument_name = f"{level}_{name}_core"
    attribute_name = attributes_namer( level, f"{name}_core" )
    return (
            arguments.get( argument_name )
        or  getattr( cls, attribute_name, default ) )


def assign_attribute_if_mutable( # noqa: PLR0913
    obj: object, /, *,
    ligation: _nomina.AssignerLigation,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    level: str,
    name: str,
    value: __.typx.Any,
) -> None:
    ''' Assigns attribute if it is mutable, else raises error. '''
    leveli = 'instance' if level == 'instances' else level
    behaviors_name = attributes_namer( leveli, 'behaviors' )
    behaviors = _utilities.getattr0( obj, behaviors_name, frozenset( ) )
    if _nomina.immutability_label not in behaviors:
        ligation( name, value )
        return
    names_name = attributes_namer( level, 'mutables_names' )
    names: _nomina.BehaviorExclusionNamesOmni = (
        getattr( obj, names_name, frozenset( ) ) )
    if names == '*' or name in names:
        ligation( name, value )
        return
    predicates_name = attributes_namer( level, 'mutables_predicates' )
    predicates: _nomina.BehaviorExclusionPredicates = (
        getattr( obj, predicates_name, ( ) ) )
    for predicate in predicates:
        if predicate( name ):
            # TODO? Cache predicate hit.
            ligation( name, value )
            return
    regexes_name = attributes_namer( level, 'mutables_regexes' )
    regexes: _nomina.BehaviorExclusionRegexes = (
        getattr( obj, regexes_name, ( ) ) )
    for regex in regexes:
        if regex.fullmatch( name ):
            # TODO? Cache regex hit.
            ligation( name, value )
            return
    target = _utilities.describe_object( obj )
    raise error_class_provider( 'AttributeImmutability' )( name, target )


def delete_attribute_if_mutable( # noqa: PLR0913
    obj: object, /, *,
    ligation: _nomina.DeleterLigation,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    level: str,
    name: str,
) -> None:
    ''' Deletes attribute if it is mutable, else raises error. '''
    leveli = 'instance' if level == 'instances' else level
    behaviors_name = attributes_namer( leveli, 'behaviors' )
    behaviors = _utilities.getattr0( obj, behaviors_name, frozenset( ) )
    if _nomina.immutability_label not in behaviors:
        ligation( name )
        return
    names_name = attributes_namer( level, 'mutables_names' )
    names: _nomina.BehaviorExclusionNamesOmni = (
        getattr( obj, names_name, frozenset( ) ) )
    if names == '*' or name in names:
        ligation( name )
        return
    predicates_name = attributes_namer( level, 'mutables_predicates' )
    predicates: _nomina.BehaviorExclusionPredicates = (
        getattr( obj, predicates_name, ( ) ) )
    for predicate in predicates:
        if predicate( name ):
            # TODO? Cache predicate hit.
            ligation( name )
            return
    regexes_name = attributes_namer( level, 'mutables_regexes' )
    regexes: _nomina.BehaviorExclusionRegexes = (
        getattr( obj, regexes_name, ( ) ) )
    for regex in regexes:
        if regex.fullmatch( name ):
            # TODO? Cache regex hit.
            ligation( name )
            return
    target = _utilities.describe_object( obj )
    raise error_class_provider( 'AttributeImmutability' )( name, target )


def survey_visible_attributes(
    obj: object, /, *,
    ligation: _nomina.SurveyorLigation,
    attributes_namer: _nomina.AttributesNamer,
    level: str,
) -> __.cabc.Iterable[ str ]:
    ''' Returns sequence of visible attributes. '''
    names_base = ligation( )
    leveli = 'instance' if level == 'instances' else level
    behaviors_name = attributes_namer( leveli, 'behaviors' )
    behaviors = _utilities.getattr0( obj, behaviors_name, frozenset( ) )
    if _nomina.concealment_label not in behaviors: return names_base
    names_name = attributes_namer( level, 'visibles_names' )
    names: _nomina.BehaviorExclusionNamesOmni = (
        getattr( obj, names_name, frozenset( ) ) )
    if names == '*': return names_base # pragma: no branch
    regexes_name = attributes_namer( level, 'visibles_regexes' )
    regexes: _nomina.BehaviorExclusionRegexes = (
        getattr( obj, regexes_name, ( ) ) )
    predicates_name = attributes_namer( level, 'visibles_predicates' )
    predicates: _nomina.BehaviorExclusionPredicates = (
        getattr( obj, predicates_name, ( ) ) )
    names_: list[ str ] = [ ]
    for name in names_base:
        if name in names:
            names_.append( name )
            continue
        for predicate in predicates:
            if predicate( name ):
                # TODO? Cache predicate hit.
                names_.append( name )
                continue
        for regex in regexes:
            if regex.fullmatch( name ):
                # TODO? Cache regex hit.
                names_.append( name )
                continue
    return names_


def augment_class_attributes_allocations(
    attributes_namer: _nomina.AttributesNamer,
    namespace: dict[ str, __.typx.Any ],
) -> None:
    ''' Adds necessary slots for record-keeping attributes. '''
    behaviors_name = attributes_namer( 'instance', 'behaviors' )
    slots: __.typx.Union[
        __.cabc.Mapping[ str, __.typx.Any ],
        __.cabc.Sequence[ str ],
        None
    ] = namespace.get( '__slots__' )
    if slots and behaviors_name in slots: return
    if isinstance( slots, __.cabc.Mapping ):
        slots_ = dict( slots )
        slots_[ behaviors_name ] = 'Active behaviors.'
        slots_ = __.types.MappingProxyType( slots_ )
    elif isinstance( slots, __.cabc.Sequence ):
        slots_ = list( slots )
        slots_.append( behaviors_name )
        slots_ = tuple( slots_ )
    else: return # pragma: no cover
    namespace[ '__slots__' ] = slots_


def classify_behavior_exclusion_verifiers(
    verifiers: _nomina.BehaviorExclusionVerifiers
) -> tuple[
    _nomina.BehaviorExclusionNames,
    _nomina.BehaviorExclusionRegexes,
    _nomina.BehaviorExclusionPredicates,
]:
    ''' Threshes sequence of behavior exclusion verifiers into bins. '''
    names: set[ str ] = set( )
    regexes: list[ __.re.Pattern[ str ] ] = [ ]
    predicates: list[ __.cabc.Callable[ ..., bool ] ] = [ ]
    for verifier in verifiers:
        if isinstance( verifier, str ):
            names.add( verifier )
        elif isinstance( verifier, __.re.Pattern ):
            regexes.append( verifier )
        elif callable( verifier ):
            predicates.append( verifier )
        else:
            from ..exceptions import BehaviorExclusionInvalidity
            raise BehaviorExclusionInvalidity( verifier )
    return frozenset( names ), tuple( regexes ), tuple( predicates )


def produce_class_construction_preprocessor(
    attributes_namer: _nomina.AttributesNamer
) -> _nomina.ClassConstructionPreprocessor[ __.U ]:
    ''' Produces construction processor which handles metaclass arguments. '''

    def preprocess( # noqa: PLR0913
        clscls: type,
        name: str,
        bases: list[ type ],
        namespace: dict[ str, __.typx.Any ],
        arguments: dict[ str, __.typx.Any ],
        decorators: _nomina.DecoratorsMutable[ __.U ],
    ) -> None:
        record_class_construction_arguments(
            attributes_namer, namespace, arguments )
        if '__slots__' in namespace:
            augment_class_attributes_allocations( attributes_namer, namespace )

    return preprocess


def produce_class_construction_postprocessor(
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
) -> _nomina.ClassConstructionPostprocessor[ __.U ]:
    ''' Produces construction processor which determines class decorators. '''
    arguments_name = attributes_namer( 'class', 'construction_arguments' )
    cores_default = dict(
        assigner = assign_attribute_if_mutable,
        deleter = delete_attribute_if_mutable,
        surveyor = survey_visible_attributes )

    def postprocess(
        cls: type, decorators: _nomina.DecoratorsMutable[ __.U ]
    ) -> None:
        arguments = getattr( cls, arguments_name, { } )
        clscls = type( cls )
        dcls_spec = getattr( cls, '__dataclass_transform__', None )
        if not dcls_spec: # either base class or metaclass may be marked
            dcls_spec = getattr( clscls, '__dataclass_transform__', None )
        cores = { }
        for core_name in ( 'assigner', 'deleter', 'surveyor' ):
            core_function = access_core_function(
                cls,
                attributes_namer = attributes_namer,
                arguments = arguments,
                level = 'instances', name = core_name,
                default = cores_default[ core_name ] )
            cores[ core_name ] = core_function
        instances_mutables = arguments.get(
            'instances_mutables', __.mutables_default )
        instances_visibles = arguments.get(
            'instances_visibles', __.visibles_default )
        instances_ignore_init_arguments = arguments.get(
            'instances_ignore_init_arguments', False )
        if dcls_spec and dcls_spec.get( 'kw_only_default', False ):
            from .decorators import dataclass_with_standard_behaviors
            decorator_factory = dataclass_with_standard_behaviors
            if not dcls_spec.get( 'frozen_default', True ):
                instances_mutables = instances_mutables or '*'
        else:
            from .decorators import with_standard_behaviors
            decorator_factory = with_standard_behaviors
        decorator: _nomina.Decorator[ __.U ] = decorator_factory(
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            assigner_core = __.typx.cast(
                _nomina.AssignerCore, cores[ 'assigner' ] ),
            deleter_core = __.typx.cast(
                _nomina.DeleterCore, cores[ 'deleter' ] ),
            surveyor_core = __.typx.cast(
                _nomina.SurveyorCore, cores[ 'surveyor' ] ),
            ignore_init_arguments = instances_ignore_init_arguments,
            mutables = instances_mutables,
            visibles = instances_visibles )
        decorators.append( decorator )
        # Dynadoc tracks objects in weakset.
        # Must decorate after any potential class replacements.
        dynadoc_cfg = arguments.get( 'dynadoc_configuration', { } )
        if not dynadoc_cfg: # either metaclass argument or attribute
            dynadoc_cfg_name = (
                attributes_namer( 'classes', 'dynadoc_configuration' ) )
            dynadoc_cfg = getattr( clscls, dynadoc_cfg_name, { } )
        decorators.append( __.ddoc.with_docstring( **dynadoc_cfg ) )

    return postprocess


def produce_class_initialization_completer(
    attributes_namer: _nomina.AttributesNamer
) -> _nomina.ClassInitializationCompleter:
    ''' Produces initialization completer which finalizes class behaviors. '''
    arguments_name = attributes_namer( 'class', 'construction_arguments' )

    def complete( cls: type ) -> None:
        arguments: __.typx.Optional[ dict[ str, __.typx.Any ] ] = (
            getattr( cls, arguments_name, None ) )
        if arguments is not None: delattr( cls, arguments_name )
        arguments = arguments or { }
        mutables = arguments.get( 'class_mutables', __.mutables_default )
        visibles = arguments.get( 'class_visibles', __.visibles_default )
        behaviors: set[ str ] = set( )
        record_behavior(
            cls, attributes_namer = attributes_namer,
            level = 'class', basename = 'mutables',
            label = _nomina.immutability_label, behaviors = behaviors,
            verifiers = mutables )
        record_behavior(
            cls, attributes_namer = attributes_namer,
            level = 'class', basename = 'visibles',
            label = _nomina.concealment_label, behaviors = behaviors,
            verifiers = visibles )
        # Set behaviors attribute last since it enables enforcement.
        behaviors_name = attributes_namer( 'class', 'behaviors' )
        _utilities.setattr0( cls, behaviors_name, frozenset( behaviors ) )

    return complete


def record_behavior( # noqa: PLR0913
    cls: type, /, *,
    attributes_namer: _nomina.AttributesNamer,
    level: str,
    basename: str,
    label: str,
    behaviors: set[ str ],
    verifiers: _nomina.BehaviorExclusionVerifiersOmni,
) -> None:
    ''' Records details of particular class behavior, such as immutability. '''
    names_name = attributes_namer( level, f"{basename}_names" )
    if verifiers == '*':
        setattr( cls, names_name, '*' )
        return
    names_omni: _nomina.BehaviorExclusionNamesOmni = (
        getattr( cls, names_name, frozenset( ) ) )
    if names_omni == '*': return
    names, regexes, predicates = (
        classify_behavior_exclusion_verifiers( verifiers ) )
    regexes_name = attributes_namer( level, f"{basename}_regexes" )
    predicates_name = attributes_namer( level, f"{basename}_predicates" )
    names_: _nomina.BehaviorExclusionNames = (
        frozenset( { *names, *names_omni } ) )
    regexes_: _nomina.BehaviorExclusionRegexes = (
        _deduplicate_merge_sequences(
            regexes, getattr( cls, regexes_name, ( ) ) ) )
    predicates_: _nomina.BehaviorExclusionPredicates = (
        _deduplicate_merge_sequences(
            predicates, getattr( cls, predicates_name, ( ) ) ) )
    setattr( cls, names_name, names_ )
    setattr( cls, regexes_name, regexes_ )
    setattr( cls, predicates_name, predicates_ )
    # TODO? Add regexes match cache.
    # TODO? Add predicates match cache.
    behaviors.add( label )


def record_class_construction_arguments(
    attributes_namer: _nomina.AttributesNamer,
    namespace: dict[ str, __.typx.Any ],
    arguments: dict[ str, __.typx.Any ],
) -> None:
    ''' Captures metaclass arguments as class attribute for later use. '''
    arguments_name = attributes_namer( 'class', 'construction_arguments' )
    arguments_ = namespace.get( arguments_name, { } )
    # Decorators, which replace classes, will cause construction of the
    # replacements without arguments. If we had previously recorded them in
    # the class namespace, then we do not want to clobber them.
    if arguments_: return
    arguments_ = { }
    for name in (
        'class_mutables', 'class_visibles',
        'dynadoc_configuration',
        'instances_assigner_core',
        'instances_deleter_core',
        'instances_surveyor_core',
        'instances_ignore_init_arguments',
        'instances_mutables', 'instances_visibles',
    ):
        if name not in arguments: continue
        arguments_[ name ] = arguments.pop( name )
    namespace[ arguments_name ] = arguments_


def _deduplicate_merge_sequences(
    addends: __.cabc.Sequence[ __.typx.Any ],
    augends: __.cabc.Sequence[ __.typx.Any ],
) -> __.cabc.Sequence[ __.typx.Any ]:
    result = list( augends )
    augends_ = set( augends )
    for addend in addends:
        if addend in augends_: continue
        result.append( addend )
    return tuple( result )
