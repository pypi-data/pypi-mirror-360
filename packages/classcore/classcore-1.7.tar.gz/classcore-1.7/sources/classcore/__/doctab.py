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


''' Docstring fragments. '''


from . import imports as __


_FragmentsTable: __.typx.TypeAlias = __.cabc.Mapping[ str, str ]
fragments: _FragmentsTable = __.types.MappingProxyType( {

    'cfc class conceal':
    ''' By default, conceals non-public class attributes. ''',

    'cfc class protect':
    ''' By default, protects class attributes. ''',

    'cfc dynadoc': ''' Applies Dynadoc decoration to classes. ''',

    'cfc instance conceal':
    ''' Produces classes which can conceal instance attributes. ''',

    'cfc instance protect':
    ''' Produces classes which can protect instance attributes. ''',

    'cfc produce dataclass':
    ''' Produces inheritable dataclasses with keyword-only instantiation. ''',

    'cfc produce protocol class':
    ''' Produces :pep:`544` protocol classes. ''',

    'class concealment':
    ''' By default, non-public class attributes are invisible. ''',

    'class protection':
    ''' By default, class attributes are immutable. ''',

    'class instance conceal':
    ''' By default, conceals non-public instance attributes. ''',

    'class instance protect':
    ''' By default, protects instance attributes. ''',

    'dataclass':
    ''' Inheritable dataclass with keyword-only instantiation. ''',

    'protocol class':
    ''' Protocol class (:pep:`544`). Nominal and structural subtyping. ''',

    'class dynadoc': ''' Is decorated by Dynadoc. ''',

} )
