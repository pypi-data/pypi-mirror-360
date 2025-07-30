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


''' Foundational class factories and decorators.

    Provides ability to create class decorators and metaclasses
    with customization hooks. The metaclasses can apply class decorators
    inline during the class construction and initialization process, properly
    handling cases where decorators replace classes (e.g.,
    ``dataclasses.dataclass( slots = True )``). They also backport the repair
    mechanism from newer versions of CPython to ensure that the class closure
    cells are rectified on replaced classes, so that zero-argument ``super``
    calls function correctly in them.

    The ``classcore.standard`` subpackage is an example of the decorators and
    customization hooks being used to provide a set of practical classes and
    class decorators. Furthermore, the exception classes in the
    :py:mod:`classcore.exceptions` module inherit from one of the standard
    classes, making both the exception classes, themselves, and their
    instances immutable and concealing their non-public attributes to reduce
    API noise. I.e., this package "eats its own dog food" and provides
    practical examples in so doing.

    This package is not as magical as it might seem. It does **not** rely on
    any ``exec`` or ``eval`` calls and it does **not** do anything with
    ``ctypes`` or similar surgical instruments. It relies completely on the
    documented Python data model and the machinery that it provides. While it
    is true that metaclasses can be tricky, this package is developed with a
    deep, highly-evolved understanding of them. We seek simplicity over
    cleverness and maintain robust tests across multiple Python
    implementations and versions. The package is also very clean in terms of
    static type checking (via Pyright).
'''


from . import __
from . import exceptions
from . import nomina
from . import standard
# --- BEGIN: Injected by Copier ---
# --- END: Injected by Copier ---

from .decorators import *
from .factories import *


__version__: __.typx.Annotated[ str, __.ddoc.Visibilities.Reveal ]
__version__ = '1.7'


standard.finalize_module(
    __name__, dynadoc_table = __.fragments, recursive = True )
