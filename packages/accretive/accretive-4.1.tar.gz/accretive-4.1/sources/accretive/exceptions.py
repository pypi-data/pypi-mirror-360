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


''' Family of exceptions for package API.

    Provides a hierarchy of exceptions that are raised when accretive behavior
    is violated. The hierarchy is designed to allow both specific and general
    exception handling.
'''


from . import __
from . import classes as _classes


class Omniexception(
    _classes.Object, BaseException,
    instances_visibles = (
        '__cause__', '__context__', __.is_public_identifier ),
):
    ''' Base exceptions for package. '''


class Omnierror( Omniexception, Exception ):
    ''' Base for error exceptions raised by package API. '''


class AttributeImmutability( Omnierror, AttributeError, TypeError ):

    def __init__( self, name: str, target: str ):
        super( ).__init__(
            f"Could not assign or delete attribute {name!r} on {target}." )


class EntryImmutability( Omnierror, TypeError ):

    def __init__( self, indicator: __.cabc.Hashable ) -> None:
        super( ).__init__(
            f"Could not alter or remove existing entry for {indicator!r}." )


class EntryInvalidity( Omnierror, ValueError ):

    def __init__(
        self, indicator: __.cabc.Hashable, value: __.typx.Any
    ) -> None:
        super( ).__init__(
            f"Could not add invalid entry with key, {indicator!r}, "
            f"and value, {value!r}, to dictionary." )


class ErrorProvideFailure( Omnierror, RuntimeError ):

    def __init__( self, name: str, reason: str ):
        super( ).__init__(
            f"Could not provide error class {name!r}. Reason: {reason}" )
