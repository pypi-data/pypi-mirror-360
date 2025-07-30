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


''' Exceptions from package. '''


from . import __
from . import standard as _standard


class Omniexception(
    _standard.Object, BaseException,
    instances_visibles = ( '__cause__', '__context__' ),
):
    ''' Base exception for package. '''


class Omnierror( Omniexception, Exception ):
    ''' Base error for package. '''


class AttributeImmutability( Omnierror, AttributeError ):

    def __init__( self, name: str, target: str ):
        super( ).__init__(
            f"Could not assign or delete attribute {name!r} on {target}." )


class BehaviorExclusionInvalidity( Omnierror, TypeError, ValueError ):

    def __init__( self, verifier: __.typx.Any ):
        super( ).__init__(
            f"Invalid behavior exclusion verifier: {verifier!r}" )


class ErrorProvideFailure( Omnierror, RuntimeError ):

    def __init__( self, name: str, reason: str ):
        super( ).__init__(
            f"Could not provide error class {name!r}. Reason: {reason}" )
