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


''' Standard decorators. '''
# TODO? Add attribute value transformer as standard decorator argument.


from .. import factories as _factories
from .. import utilities as _utilities
from ..decorators import (
    decoration_by,
    produce_class_construction_decorator,
    produce_class_initialization_decorator,
)
from . import __
from . import behaviors as _behaviors
from . import dynadoc as _dynadoc
from . import nomina as _nomina


_dataclass_core = __.dcls.dataclass( kw_only = True, slots = True )
_dynadoc_configuration = _dynadoc.produce_dynadoc_configuration( )


def prepare_dataclass_for_instances(
    cls: type,
    decorators: _nomina.DecoratorsMutable[ __.U ], /, *,
    attributes_namer: _nomina.AttributesNamer,
) -> None:
    ''' Annotates dataclass in support of instantiation machinery. '''
    annotations = __.inspect.get_annotations( cls )
    behaviors_name = attributes_namer( 'instance', 'behaviors' )
    # TODO: Only use mangling if not slotted.
    # behaviors_name_ = _utilities.mangle_name( cls, behaviors_name )
    behaviors_name_ = behaviors_name
    annotations[ behaviors_name_ ] = set[ str ]
    setattr( cls, '__annotations__', annotations ) # in case of absence
    setattr( cls, behaviors_name_, __.dcls.field(
        compare = False, hash = False, init = False, repr = False ) )


def apply_cfc_core_functions(
    clscls: type[ __.T ], /,
    attributes_namer: _nomina.AttributesNamer,
    assigner_core: __.typx.Optional[ _nomina.AssignerCore ] = None,
    deleter_core: __.typx.Optional[ _nomina.DeleterCore ] = None,
    surveyor_core: __.typx.Optional[ _nomina.SurveyorCore ] = None,
) -> None:
    ''' Stores core functions on metaclass. '''
    cores = dict(
        classes_assigner_core = assigner_core,
        classes_deleter_core = deleter_core,
        classes_surveyor_core = surveyor_core )
    cores_default = dict(
        assigner = _behaviors.assign_attribute_if_mutable,
        deleter = _behaviors.delete_attribute_if_mutable,
        surveyor = _behaviors.survey_visible_attributes )
    for core_name in ( 'assigner', 'deleter', 'surveyor' ):
        core_function = _behaviors.access_core_function(
            clscls,
            attributes_namer = attributes_namer,
            arguments = cores,
            level = 'classes', name = core_name,
            default = cores_default[ core_name ] )
        core_aname = attributes_namer( 'classes', f"{core_name}_core" )
        setattr( clscls, core_aname, core_function )


def apply_cfc_dynadoc_configuration(
    clscls: type[ __.T ], /,
    attributes_namer: _nomina.AttributesNamer,
    configuration: _nomina.DynadocConfiguration,
) -> None:
    ''' Stores Dynadoc configuration on metaclass. '''
    configuration_name = attributes_namer( 'classes', 'dynadoc_configuration' )
    setattr( clscls, configuration_name, configuration )


def apply_cfc_constructor(
    clscls: type[ __.T ], /,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
) -> None:
    ''' Injects '__new__' method into metaclass. '''
    preprocessors = (
        _behaviors.produce_class_construction_preprocessor(
            attributes_namer = attributes_namer ), )
    postprocessors = (
        _behaviors.produce_class_construction_postprocessor(
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider ), )
    constructor: _nomina.ClassConstructor[ __.T ] = (
        _factories.produce_class_constructor(
            attributes_namer = attributes_namer,
            preprocessors = preprocessors,
            postprocessors = postprocessors ) )
    decorator = produce_class_construction_decorator(
        attributes_namer = attributes_namer, constructor = constructor )
    decorator( clscls )


def apply_cfc_initializer(
    clscls: type[ __.T ], /, attributes_namer: _nomina.AttributesNamer
) -> None:
    ''' Injects '__init__' method into metaclass. '''
    completers = (
        _behaviors.produce_class_initialization_completer(
            attributes_namer = attributes_namer ), )
    initializer = (
        _factories.produce_class_initializer(
            attributes_namer = attributes_namer,
            completers = completers ) )
    decorator = produce_class_initialization_decorator(
        attributes_namer = attributes_namer, initializer = initializer )
    decorator( clscls )


def apply_cfc_attributes_assigner(
    clscls: type[ __.T ], /,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    implementation_core: __.typx.Optional[ _nomina.AssignerCore ],
) -> None:
    ''' Injects '__setattr__' method into metaclass. '''
    decorator = produce_attributes_assignment_decorator(
        level = 'classes',
        attributes_namer = attributes_namer,
        error_class_provider = error_class_provider,
        implementation_core = implementation_core )
    decorator( clscls )


def apply_cfc_attributes_deleter(
    clscls: type[ __.T ], /,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    implementation_core: __.typx.Optional[ _nomina.DeleterCore ],
) -> None:
    ''' Injects '__delattr__' method into metaclass. '''
    decorator = produce_attributes_deletion_decorator(
        level = 'classes',
        attributes_namer = attributes_namer,
        error_class_provider = error_class_provider,
        implementation_core = implementation_core )
    decorator( clscls )


def apply_cfc_attributes_surveyor(
    clscls: type[ __.T ],
    attributes_namer: _nomina.AttributesNamer,
    implementation_core: __.typx.Optional[ _nomina.SurveyorCore ],
) -> None:
    ''' Injects '__dir__' method into metaclass. '''
    decorator = produce_attributes_surveillance_decorator(
        level = 'classes',
        attributes_namer = attributes_namer,
        implementation_core = implementation_core )
    decorator( clscls )


def class_factory( # noqa: PLR0913
    attributes_namer: _nomina.AttributesNamer = __.calculate_attrname,
    error_class_provider: _nomina.ErrorClassProvider = __.provide_error_class,
    assigner_core: __.typx.Optional[ _nomina.AssignerCore ] = None,
    deleter_core: __.typx.Optional[ _nomina.DeleterCore ] = None,
    surveyor_core: __.typx.Optional[ _nomina.SurveyorCore ] = None,
    dynadoc_configuration: __.cabc.Mapping[ str, __.typx.Any ] = (
        _dynadoc_configuration ),
) -> _nomina.Decorator[ __.T ]:
    ''' Produces decorator to apply standard behaviors to metaclass. '''
    def decorate( clscls: type[ __.T ] ) -> type[ __.T ]:
        apply_cfc_core_functions(
            clscls,
            attributes_namer = attributes_namer,
            assigner_core = assigner_core,
            deleter_core = deleter_core,
            surveyor_core = surveyor_core )
        apply_cfc_dynadoc_configuration(
            clscls,
            attributes_namer = attributes_namer,
            configuration = dynadoc_configuration )
        apply_cfc_constructor(
            clscls,
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider )
        apply_cfc_initializer( clscls, attributes_namer = attributes_namer )
        apply_cfc_attributes_assigner(
            clscls,
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            implementation_core = assigner_core )
        apply_cfc_attributes_deleter(
            clscls,
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            implementation_core = deleter_core )
        apply_cfc_attributes_surveyor(
            clscls,
            attributes_namer = attributes_namer,
            implementation_core = surveyor_core )
        return clscls

    return decorate


def produce_instances_inception_decorator( # noqa: PLR0913
    attributes_namer: _nomina.AttributesNamer,
    assigner_core: __.typx.Optional[ _nomina.AssignerCore ],
    deleter_core: __.typx.Optional[ _nomina.DeleterCore ],
    surveyor_core: __.typx.Optional[ _nomina.SurveyorCore ],
    ignore_init_arguments: bool,
    mutables: _nomina.BehaviorExclusionVerifiersOmni,
    visibles: _nomina.BehaviorExclusionVerifiersOmni,
) -> _nomina.Decorator[ __.U ]:
    ''' Produces decorator to inject '__new__' or '__init__' method.

        Also handles common bookkeeping tasks.
    '''
    cores = dict(
        instances_assigner_core = assigner_core,
        instances_deleter_core = deleter_core,
        instances_surveyor_core = surveyor_core )
    cores_default = dict(
        assigner = _behaviors.assign_attribute_if_mutable,
        deleter = _behaviors.delete_attribute_if_mutable,
        surveyor = _behaviors.survey_visible_attributes )

    def decorate( cls: type[ __.U ] ) -> type[ __.U ]:
        for core_name in ( 'assigner', 'deleter', 'surveyor' ):
            core_function = _behaviors.access_core_function(
                cls,
                attributes_namer = attributes_namer,
                arguments = cores,
                level = 'instances', name = core_name,
                default = cores_default[ core_name ] )
            core_aname = attributes_namer( 'instances', f"{core_name}_core" )
            setattr( cls, core_aname, core_function )
        behaviors: set[ str ] = set( )
        _behaviors.record_behavior(
            cls, attributes_namer = attributes_namer,
            level = 'instances', basename = 'mutables',
            label = _nomina.immutability_label, behaviors = behaviors,
            verifiers = mutables )
        _behaviors.record_behavior(
            cls, attributes_namer = attributes_namer,
            level = 'instances', basename = 'visibles',
            label = _nomina.concealment_label, behaviors = behaviors,
            verifiers = visibles )
        decorator = produce_instances_initialization_decorator(
            attributes_namer = attributes_namer,
            behaviors = behaviors,
            ignore_init_arguments = ignore_init_arguments )
        return decorator( cls )

    return decorate


# def produce_instances_construction_decorator(
#     attributes_namer: _nomina.AttributesNamer,
#     behaviors: __.cabc.MutableSet[ str ],
# ) -> _nomina.Decorator[ __.U ]:
#     ''' Produces decorator to inject '__new__' method. '''
#     def decorate( cls_: type[ __.U ] ) -> type[ __.U ]:
#         behaviors_name = attributes_namer( 'instance', 'behaviors' )
#         original = cls_.__dict__.get( '__new__' )
#
#         if original is None:
#
#             def initialize_with_super(
#                 cls: type[ __.U ],
#                 *posargs: __.typx.Any,
#                 **nomargs: __.typx.Any,
#             ) -> __.U:
#                 self = super( cls_, cls ).__new__( cls, *posargs, **nomargs )
#                 _activate_instance_behaviors(
#                     cls_, self, behaviors_name, behaviors )
#                 return self
#
#             cls_.__new__ = initialize_with_super
#
#         else:
#
#             @__.funct.wraps( original )
#             def initialize_with_original(
#                 cls: type[ __.U ],
#                 *posargs: __.typx.Any,
#                 **nomargs: __.typx.Any,
#             ) -> __.U:
#                 self = original( cls, *posargs, **nomargs )
#                 _activate_instance_behaviors(
#                     cls_, self, behaviors_name, behaviors )
#                 return self
#
#             cls_.__new__ = initialize_with_original
#
#         return cls_
#
#     return decorate


def produce_instances_initialization_decorator(
    attributes_namer: _nomina.AttributesNamer,
    behaviors: __.cabc.MutableSet[ str ],
    ignore_init_arguments: bool,
) -> _nomina.Decorator[ __.U ]:
    ''' Produces decorator to inject '__init__' method into class. '''
    def decorate( cls: type[ __.U ] ) -> type[ __.U ]:
        behaviors_name = attributes_namer( 'instance', 'behaviors' )
        original = cls.__dict__.get( '__init__' )

        if original is None:

            def initialize_with_super(
                self: object, *posargs: __.typx.Any, **nomargs: __.typx.Any
            ) -> None:
                if ignore_init_arguments: super( cls, self ).__init__( )
                else: super( cls, self ).__init__( *posargs, **nomargs )
                _activate_instance_behaviors(
                    cls, self, behaviors_name, behaviors )

            cls.__init__ = initialize_with_super

        else:

            @__.funct.wraps( original )
            def initialize_with_original(
                self: object, *posargs: __.typx.Any, **nomargs: __.typx.Any
            ) -> None:
                if ignore_init_arguments: original( self )
                else: original( self, *posargs, **nomargs )
                _activate_instance_behaviors(
                    cls, self, behaviors_name, behaviors )

            cls.__init__ = initialize_with_original

        return cls

    return decorate


def produce_attributes_assignment_decorator(
    level: str,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    implementation_core: __.typx.Optional[ _nomina.AssignerCore ],
) -> _nomina.Decorator[ __.U ]:
    ''' Produces decorator to inject '__setattr__' method into class. '''
    def decorate( cls: type[ __.U ] ) -> type[ __.U ]:
        leveli = 'class' if level == 'classes' else level
        original = cls.__dict__.get( '__setattr__' )
        core = _behaviors.access_core_function(
            cls,
            attributes_namer = attributes_namer,
            arguments = { f"{level}_assigner": implementation_core },
            level = level, name = 'assigner',
            default = _behaviors.assign_attribute_if_mutable )

        if original is None:

            def assign_with_super(
                self: object, name: str, value: __.typx.Any
            ) -> None:
                ligation = super( cls, self ).__setattr__
                # Only enforce behaviors at start of MRO.
                if cls is not type( self ):
                    ligation( name, value )
                    return
                core(
                    self,
                    ligation = ligation,
                    attributes_namer = attributes_namer,
                    error_class_provider = error_class_provider,
                    level = leveli,
                    name = name, value = value )

            cls.__setattr__ = assign_with_super

        else:

            @__.funct.wraps( original )
            def assign_with_original(
                self: object, name: str, value: __.typx.Any
            ) -> None:
                ligation = __.funct.partial( original, self )
                # Only enforce behaviors at start of MRO.
                if cls is not type( self ):
                    ligation( name, value )
                    return
                core(
                    self,
                    ligation = ligation,
                    attributes_namer = attributes_namer,
                    error_class_provider = error_class_provider,
                    level = leveli,
                    name = name, value = value )

            cls.__setattr__ = assign_with_original

        return cls

    return decorate


def produce_attributes_deletion_decorator(
    level: str,
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    implementation_core: __.typx.Optional[ _nomina.DeleterCore ],
) -> _nomina.Decorator[ __.U ]:
    ''' Produces decorator to inject '__delattr__' method into class. '''
    def decorate( cls: type[ __.U ] ) -> type[ __.U ]:
        leveli = 'class' if level == 'classes' else level
        original = cls.__dict__.get( '__delattr__' )
        core = _behaviors.access_core_function(
            cls,
            attributes_namer = attributes_namer,
            arguments = { f"{level}_deleter": implementation_core },
            level = level, name = 'deleter',
            default = _behaviors.delete_attribute_if_mutable )

        if original is None:

            def delete_with_super( self: object, name: str ) -> None:
                ligation = super( cls, self ).__delattr__
                # Only enforce behaviors at start of MRO.
                if cls is not type( self ):
                    ligation( name )
                    return
                core(
                    self,
                    ligation = ligation,
                    attributes_namer = attributes_namer,
                    error_class_provider = error_class_provider,
                    level = leveli,
                    name = name )

            cls.__delattr__ = delete_with_super

        else:

            @__.funct.wraps( original )
            def delete_with_original( self: object, name: str ) -> None:
                ligation = __.funct.partial( original, self )
                # Only enforce behaviors at start of MRO.
                if cls is not type( self ):
                    ligation( name )
                    return
                core(
                    self,
                    ligation = ligation,
                    attributes_namer = attributes_namer,
                    error_class_provider = error_class_provider,
                    level = leveli,
                    name = name )

            cls.__delattr__ = delete_with_original

        return cls

    return decorate


def produce_attributes_surveillance_decorator(
    level: str,
    attributes_namer: _nomina.AttributesNamer,
    implementation_core: __.typx.Optional[ _nomina.SurveyorCore ],
) -> _nomina.Decorator[ __.U ]:
    ''' Produces decorator to inject '__dir__' method into class. '''
    def decorate( cls: type[ __.U ] ) -> type[ __.U ]:
        leveli = 'class' if level == 'classes' else level
        original = cls.__dict__.get( '__dir__' )
        core = _behaviors.access_core_function(
            cls,
            attributes_namer = attributes_namer,
            arguments = { f"{level}_surveyor": implementation_core },
            level = level, name = 'surveyor',
            default = _behaviors.survey_visible_attributes )

        if original is None:

            def survey_with_super(
                self: object
            ) -> __.cabc.Iterable[ str ]:
                ligation = super( cls, self ).__dir__
                # Only enforce behaviors at start of MRO.
                if cls is not type( self ): return ligation( )
                return core(
                    self,
                    ligation = ligation,
                    attributes_namer = attributes_namer,
                    level = leveli )

            cls.__dir__ = survey_with_super

        else:

            @__.funct.wraps( original )
            def survey_with_original(
                self: object
            ) -> __.cabc.Iterable[ str ]:
                ligation = __.funct.partial( original, self )
                # Only enforce behaviors at start of MRO.
                if cls is not type( self ): return ligation( )
                return core(
                    self,
                    ligation = ligation,
                    attributes_namer = attributes_namer,
                    level = leveli )

            cls.__dir__ = survey_with_original

        return cls

    return decorate


@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
def dataclass_with_standard_behaviors( # noqa: PLR0913
    attributes_namer: _nomina.AttributesNamer = __.calculate_attrname,
    error_class_provider: _nomina.ErrorClassProvider = __.provide_error_class,
    decorators: _nomina.Decorators[ __.U ] = ( ),
    assigner_core: __.typx.Optional[ _nomina.AssignerCore ] = None,
    deleter_core: __.typx.Optional[ _nomina.DeleterCore ] = None,
    surveyor_core: __.typx.Optional[ _nomina.SurveyorCore ] = None,
    ignore_init_arguments: bool = False,
    mutables: _nomina.BehaviorExclusionVerifiersOmni = __.mutables_default,
    visibles: _nomina.BehaviorExclusionVerifiersOmni = __.visibles_default,
) -> _nomina.Decorator[ __.U ]:
    # https://github.com/microsoft/pyright/discussions/10344
    ''' Dataclass decorator factory. '''
    decorators_: _nomina.Decorators[ __.U ] = (
        _produce_instances_decorators(
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            assigner_core = assigner_core,
            deleter_core = deleter_core,
            surveyor_core = surveyor_core,
            ignore_init_arguments = ignore_init_arguments,
            mutables = mutables,
            visibles = visibles ) )
    preparers: _nomina.DecorationPreparers[ __.U ] = (
        _produce_instances_decoration_preparers(
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            class_preparer = prepare_dataclass_for_instances ) )
    return decoration_by(
        *decorators, _dataclass_core, *decorators_, preparers = preparers )


def with_standard_behaviors( # noqa: PLR0913
    attributes_namer: _nomina.AttributesNamer = __.calculate_attrname,
    error_class_provider: _nomina.ErrorClassProvider = __.provide_error_class,
    decorators: _nomina.Decorators[ __.U ] = ( ),
    assigner_core: __.typx.Optional[ _nomina.AssignerCore ] = None,
    deleter_core: __.typx.Optional[ _nomina.DeleterCore ] = None,
    surveyor_core: __.typx.Optional[ _nomina.SurveyorCore ] = None,
    ignore_init_arguments: bool = False,
    mutables: _nomina.BehaviorExclusionVerifiersOmni = __.mutables_default,
    visibles: _nomina.BehaviorExclusionVerifiersOmni = __.visibles_default,
) -> _nomina.Decorator[ __.U ]:
    ''' Class decorator factory. '''
    decorators_: _nomina.Decorators[ __.U ] = (
        _produce_instances_decorators(
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            assigner_core = assigner_core,
            deleter_core = deleter_core,
            surveyor_core = surveyor_core,
            ignore_init_arguments = ignore_init_arguments,
            mutables = mutables,
            visibles = visibles ) )
    preparers: _nomina.DecorationPreparers[ __.U ] = (
        _produce_instances_decoration_preparers(
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider ) )
    return decoration_by( *decorators, *decorators_, preparers = preparers )


def _activate_instance_behaviors(
    cls: type[ __.U ],
    self: object,
    behaviors_name: str,
    behaviors: __.cabc.MutableSet[ str ],
) -> None:
    # Only record behaviors at start of MRO.
    if cls is not type( self ): return
    behaviors_: set[ str ] = (
        _utilities.getattr0( self, behaviors_name, set( ) ) )
    behaviors_.update( behaviors )
    _utilities.setattr0( self, behaviors_name, frozenset( behaviors_ ) )


def _produce_instances_decoration_preparers(
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    class_preparer: __.typx.Optional[ _nomina.ClassPreparer ] = None,
) -> _nomina.DecorationPreparers[ __.U ]:
    ''' Produces processors for standard decorators. '''
    preprocessors: list[ _nomina.DecorationPreparer[ __.U ] ] = [ ]
    if class_preparer is not None:
        preprocessors.append(
            __.funct.partial(
                class_preparer, attributes_namer = attributes_namer ) )
    return tuple( preprocessors )


def _produce_instances_decorators( # noqa: PLR0913
    attributes_namer: _nomina.AttributesNamer,
    error_class_provider: _nomina.ErrorClassProvider,
    assigner_core: __.typx.Optional[ _nomina.AssignerCore ],
    deleter_core: __.typx.Optional[ _nomina.DeleterCore ],
    surveyor_core: __.typx.Optional[ _nomina.SurveyorCore ],
    ignore_init_arguments: bool,
    mutables: _nomina.BehaviorExclusionVerifiersOmni,
    visibles: _nomina.BehaviorExclusionVerifiersOmni,
) -> _nomina.Decorators[ __.U ]:
    ''' Produces standard decorators. '''
    decorators: list[ _nomina.Decorator[ __.U ] ] = [ ]
    decorators.append(
        produce_instances_inception_decorator(
            attributes_namer = attributes_namer,
            assigner_core = assigner_core,
            deleter_core = deleter_core,
            surveyor_core = surveyor_core,
            ignore_init_arguments = ignore_init_arguments,
            mutables = mutables, visibles = visibles ) )
    decorators.append(
        produce_attributes_assignment_decorator(
            level = 'instances',
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            implementation_core = assigner_core ) )
    decorators.append(
        produce_attributes_deletion_decorator(
            level = 'instances',
            attributes_namer = attributes_namer,
            error_class_provider = error_class_provider,
            implementation_core = deleter_core ) )
    decorators.append(
        produce_attributes_surveillance_decorator(
            level = 'instances',
            attributes_namer = attributes_namer,
            implementation_core = surveyor_core ) )
    return decorators
