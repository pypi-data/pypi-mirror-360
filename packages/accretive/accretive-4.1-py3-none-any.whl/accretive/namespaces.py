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


''' Accretive namespaces.

    Provides a namespace type that can grow but never shrink. Once an attribute is
    set, it cannot be modified or removed. This provides a simple way to create
    objects with named attributes that become immutable after assignment.

    The namespace implementation is modeled after :py:class:`types.SimpleNamespace`
    but adds accretive behavior. Like :py:class:`types.SimpleNamespace`, it
    provides a simple ``__repr__`` which lists all attributes.

    >>> from accretive import Namespace
    >>> ns = Namespace( apples = 12, bananas = 6 )
    >>> ns.cherries = 42  # Add new attribute
    >>> ns.apples = 14    # Attempt modification
    Traceback (most recent call last):
        ...
    accretive.exceptions.AttributeImmutability: Could not assign or delete existing attribute 'apples'.
    >>> del ns.bananas    # Attempt deletion
    Traceback (most recent call last):
        ...
    accretive.exceptions.AttributeImmutability: Could not assign or delete existing attribute 'bananas'.
''' # noqa: E501


from . import __
from . import iclasses as _iclasses


class Namespace( # noqa: PLW1641
    metaclass = _iclasses.Class,
    instances_assigner_core = _iclasses.assign_attribute_if_absent_mutable,
):
    # TODO: Dynadoc fragments.
    ''' Accretive namespaces. '''

    __slots__ = ( '__dict__', )

    def __init__(
        self,
        *iterables: __.DictionaryPositionalArgument[ __.H, __.V ],
        **attributes: __.DictionaryNominativeArgument[ __.V ],
    ) -> None:
        super( ).__init__( )
        super( ).__getattribute__( '__dict__' ).update(
            __.AccretiveDictionary( *iterables, **attributes ) )

    def __repr__( self ) -> str:
        attributes = ', '.join( tuple(
            f"{key} = {value!r}" for key, value
            in getattr( self, '__dict__', { } ).items( ) ) )
        fqname = __.ccutils.qualify_class_name( type( self ) )
        if not attributes: return f"{fqname}( )"
        return f"{fqname}( {attributes} )"

    def __eq__( self, other: __.typx.Any ) -> __.ComparisonResult:
        if isinstance( other, ( Namespace, __.types.SimpleNamespace ) ):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__( self, other: __.typx.Any ) -> __.ComparisonResult:
        if isinstance( other, ( Namespace, __.types.SimpleNamespace ) ):
            return self.__dict__ != other.__dict__
        return NotImplemented
