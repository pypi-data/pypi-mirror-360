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


''' Dynadoc integration. '''


from .. import utilities as _utilities
from . import __
from . import nomina as _nomina


dynadoc_context = __.ddoc.produce_context( )
dynadoc_class_introspection_control = (
    __.ddoc.ClassIntrospectionControl(
        inheritance = True,
        introspectors = (
            __.ddoc.introspection.introspect_special_classes, ) ) )
dynadoc_module_introspection_control = (
    __.ddoc.ModuleIntrospectionControl( ) )


def dynadoc_avoid_immutables(
    objct: object,
    introspection: __.ddoc.IntrospectionControl,
    attributes_namer: _nomina.AttributesNamer,
) -> __.ddoc.IntrospectionControl:
    ''' Disables introspection of immutable objects. '''
    if __.inspect.isclass( objct ):
        behaviors_name = attributes_namer( 'class', 'behaviors' )
        behaviors = _utilities.getattr0( objct, behaviors_name, frozenset( ) )
        if _nomina.immutability_label in behaviors:
            return introspection.with_limit(
                __.ddoc.IntrospectionLimit( disable = True ) )
    return introspection


def produce_dynadoc_introspection_limiter(
    attributes_namer: _nomina.AttributesNamer = __.calculate_attrname,
) -> __.ddoc.IntrospectionLimiter:
    ''' Produces introspection limiter which avoids immutable objects. '''
    return __.funct.partial(
        dynadoc_avoid_immutables, attributes_namer = attributes_namer )

dynadoc_introspection_limiter = produce_dynadoc_introspection_limiter( )


def produce_dynadoc_introspection_control(
    enable: bool = True,
    class_control: __.ddoc.ClassIntrospectionControl = (
        dynadoc_class_introspection_control ),
    module_control: __.ddoc.ModuleIntrospectionControl = (
        dynadoc_module_introspection_control ),
    limiters: __.ddoc.IntrospectionLimiters = (
        dynadoc_introspection_limiter, ),
    targets: __.ddoc.IntrospectionTargets = (
            __.ddoc.IntrospectionTargetsSansModule ),
) -> __.ddoc.IntrospectionControl:
    ''' Produces compatible Dynadoc introspection control. '''
    return __.ddoc.IntrospectionControl(
        enable = enable,
        class_control = class_control,
        module_control = module_control,
        limiters = limiters,
        targets = targets )

dynadoc_introspection_on_class = produce_dynadoc_introspection_control( )
dynadoc_introspection_on_package = (
    produce_dynadoc_introspection_control(
        targets = __.ddoc.IntrospectionTargetsOmni ) )


def assign_module_docstring( # noqa: PLR0913
    module: str | __.types.ModuleType, /,
    *fragments: __.ddoc.interfaces.Fragment,
    context: _nomina.DynadocContextArgument = dynadoc_context,
    introspection: _nomina.DynadocIntrospectionArgument = (
        dynadoc_introspection_on_package ),
    preserve: _nomina.DynadocPreserveArgument = True,
    renderer: __.ddoc.xtnsapi.Renderer = (
        __.ddoc.assembly.renderer_default ),
    table: _nomina.DynadocTableArgument = __.dictproxy_empty,
) -> None:
    ''' Updates module docstring based on introspection.

        By default, recursively updates docstrings of all module members
        which have docstrings.

        By default, ignores previously-decorated immutable classes.
    '''
    __.ddoc.assign_module_docstring(
        module,
        *fragments,
        context = context,
        introspection = introspection,
        preserve = preserve,
        renderer = renderer,
        table = table )


def produce_dynadoc_configuration(
    context: _nomina.DynadocContextArgument = dynadoc_context,
    introspection: _nomina.DynadocIntrospectionArgument = (
        dynadoc_introspection_on_class ),
    preserve: _nomina.DynadocPreserveArgument = True,
    table: _nomina.DynadocTableArgument = __.dictproxy_empty,
) -> _nomina.ProduceDynadocConfigurationReturn:
    ''' Produces compatible Dynadoc configuration. '''
    return __.types.MappingProxyType( dict(
        context = context,
        introspection = introspection,
        preserve = preserve,
        table = table ) )
