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


''' Decorators and class factories providing concealment and immutability.

    Concealment restricts the visibility of attributes on classes and their
    instances. By default, only public attributes (ones which do not start with
    ``_``) are revealed for :py:func:`dir` calls. This behavior can be
    overriden by supplying visibility verifiers as a decorator factory
    argument or metaclass argument. These can be a sequence of attribute
    names, regular expression :py:class:`re.Pattern` objects which match
    attribute names, or predicate functions which match attribute names. Or,
    total visibility (per the Python default) can be achieved by supplying
    ``visibles = '*'`` instead of a sequence of verifiers.

    Immutability prevents assignment (including reassignment) or deletion of
    attrubtes on classes and their instances after they have been completely
    initialized. In addition to any standard Python class, this can be applied
    to dataclasses, allowing them to use ``__post_init__`` to set attributes,
    which ``dataclasses.dataclass( frozen = True )`` prevents. The
    immutability behavior can be overridden by supplying mutability verifiers
    as a decorator factory argument or metaclass argument. These behave
    similarly to the visibility verifiers described above.

    Hooks to modify the concealment and immutability behaviors are also
    available.
'''


from . import dynadoc
from . import nomina

from .classes import *
from .decorators import *
from .modules import *
