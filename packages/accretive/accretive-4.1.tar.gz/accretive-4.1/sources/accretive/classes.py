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


''' Accretive classes. '''

# ruff: noqa: F811


from . import __
from . import iclasses as _iclasses


mutables_default = _iclasses.mutables_default
visibles_default = _iclasses.visibles_default


_class_factory = __.funct.partial(
    __.ccstd.class_factory,
    assigner_core = _iclasses.assign_attribute_if_absent_mutable,
    attributes_namer = __.calculate_attrname,
    dynadoc_configuration = _iclasses.dynadoc_configuration,
    error_class_provider = _iclasses.provide_error_class )


@_class_factory( )
class Class( type ):
    ''' Metaclass for standard classes. '''

    _dynadoc_fragments_ = (
        'cfc class conceal', 'cfc class accrete', 'cfc dynadoc',
        'cfc instance conceal', 'cfc instance protect' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: __.ClassDecorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ __.ccstd.ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class Dataclass( type ):
    ''' Metaclass for standard dataclasses. '''

    _dynadoc_fragments_ = (
        'cfc produce dataclass',
        'cfc class conceal', 'cfc class accrete', 'cfc dynadoc',
        'cfc instance conceal', 'cfc instance protect' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: __.ClassDecorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ __.ccstd.ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
@__.typx.dataclass_transform( kw_only_default = True )
class DataclassMutable( type ):
    ''' Metaclass for dataclasses with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'cfc produce dataclass',
        'cfc class conceal', 'cfc class accrete', 'cfc dynadoc',
        'cfc instance conceal' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: __.ClassDecorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ __.ccstd.ClassFactoryExtraArguments ],
    ) -> __.T: # pragma: no cover
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
class AbstractBaseClass( __.abc.ABCMeta ):
    ''' Metaclass for standard abstract base classes. '''

    _dynadoc_fragments_ = (
        'cfc produce abstract base class',
        'cfc class conceal', 'cfc class accrete', 'cfc dynadoc',
        'cfc instance conceal', 'cfc instance protect' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: __.ClassDecorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ __.ccstd.ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
class ProtocolClass( type( __.typx.Protocol ) ):
    ''' Metaclass for standard protocol classes. '''

    _dynadoc_fragments_ = (
        'cfc produce protocol class',
        'cfc class conceal', 'cfc class accrete', 'cfc dynadoc',
        'cfc instance conceal', 'cfc instance protect' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: __.ClassDecorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ __.ccstd.ClassFactoryExtraArguments ],
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class ProtocolDataclass( type( __.typx.Protocol ) ):
    ''' Metaclass for standard protocol dataclasses. '''

    _dynadoc_fragments_ = (
        'cfc produce protocol class', 'cfc produce dataclass',
        'cfc class conceal', 'cfc class accrete', 'cfc dynadoc',
        'cfc instance conceal', 'cfc instance protect' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: __.ClassDecorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ __.ccstd.ClassFactoryExtraArguments ],
    ) -> __.T: # pragma: no cover
        return super( ).__new__( clscls, name, bases, namespace )


@_class_factory( )
@__.typx.dataclass_transform( kw_only_default = True )
class ProtocolDataclassMutable( type( __.typx.Protocol ) ):
    ''' Metaclass for protocol dataclasses with mutable instance attributes.
    '''

    _dynadoc_fragments_ = (
        'cfc produce protocol class', 'cfc produce dataclass',
        'cfc class conceal', 'cfc class accrete', 'cfc dynadoc',
        'cfc instance conceal' )

    def __new__( # Typechecker stub.
        clscls: type[ __.T ],
        name: str,
        bases: tuple[ type, ... ],
        namespace: dict[ str, __.typx.Any ], *,
        decorators: __.ClassDecorators[ __.T ] = ( ),
        **arguments: __.typx.Unpack[ __.ccstd.ClassFactoryExtraArguments ],
    ) -> __.T: # pragma: no cover
        return super( ).__new__( clscls, name, bases, namespace )


class Object(
    metaclass = _iclasses.Class,
    instances_assigner_core = _iclasses.assign_attribute_if_absent_mutable,
):
    ''' Standard base class. '''

    _dynadoc_fragments_ = (
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal', 'class instance accrete' )


class ObjectMutable(
    metaclass = _iclasses.Class,
    instances_assigner_core = _iclasses.assign_attribute_if_absent_mutable,
    instances_mutables = '*',
):
    ''' Base class with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal' )


class DataclassObject(
    metaclass = _iclasses.Dataclass,
    instances_assigner_core = _iclasses.assign_attribute_if_absent_mutable,
):
    ''' Standard base dataclass. '''

    _dynadoc_fragments_ = (
        'dataclass',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal', 'class instance accrete' )


class DataclassObjectMutable(
    metaclass = _iclasses.DataclassMutable,
    instances_assigner_core = _iclasses.assign_attribute_if_absent_mutable,
):
    ''' Base dataclass with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'dataclass',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal' )


class Protocol(
    __.typx.Protocol,
    metaclass = _iclasses.ProtocolClass,
    instances_assigner_core = _iclasses.assign_attribute_if_absent_mutable,
):
    ''' Standard base protocol class. '''

    _dynadoc_fragments_ = (
        'protocol class',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal', 'class instance accrete' )


class ProtocolMutable(
    __.typx.Protocol,
    metaclass = _iclasses.ProtocolClass,
    instances_assigner_core = _iclasses.assign_attribute_if_absent_mutable,
    instances_mutables = '*',
):
    ''' Base protocol class with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'protocol class',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal' )


class DataclassProtocol(
    __.typx.Protocol,
    metaclass = _iclasses.ProtocolDataclass,
    instances_assigner_core = _iclasses.assign_attribute_if_absent_mutable,
):
    ''' Standard base protocol dataclass. '''

    _dynadoc_fragments_ = (
        'dataclass', 'protocol class',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal', 'class instance accrete' )


class DataclassProtocolMutable(
    __.typx.Protocol,
    metaclass = _iclasses.ProtocolDataclassMutable,
    instances_assigner_core = _iclasses.assign_attribute_if_absent_mutable,
):
    ''' Base protocol dataclass with mutable instance attributes. '''

    _dynadoc_fragments_ = (
        'dataclass', 'protocol class',
        'class concealment', 'class protection', 'class dynadoc',
        'class instance conceal' )


@__.typx.overload
def dataclass_with_standard_behaviors( # pragma: no cover
    cls: type[ __.U ], /, *,
    decorators: __.ClassDecorators[ __.U ] = ( ),
    mutables: __.BehaviorExclusionVerifiersOmni = mutables_default,
    visibles: __.BehaviorExclusionVerifiersOmni = visibles_default,
) -> type[ __.U ]: ...


@__.typx.overload
def dataclass_with_standard_behaviors( # pragma: no cover
    cls: __.AbsentSingleton = __.absent, /, *,
    decorators: __.ClassDecorators[ __.U ] = ( ),
    mutables: __.BehaviorExclusionVerifiersOmni = mutables_default,
    visibles: __.BehaviorExclusionVerifiersOmni = visibles_default,
) -> __.ClassDecoratorFactory[ __.U ]: ...


@__.typx.dataclass_transform( frozen_default = True, kw_only_default = True )
def dataclass_with_standard_behaviors(
    cls: __.Absential[ type[ __.U ] ] = __.absent, /, *,
    decorators: __.ClassDecorators[ __.U ] = ( ),
    mutables: __.BehaviorExclusionVerifiersOmni = mutables_default,
    visibles: __.BehaviorExclusionVerifiersOmni = visibles_default,
) -> type[ __.U ] | __.ClassDecoratorFactory[ __.U ]:
    ''' Decorates dataclass to enforce standard behaviors on instances. '''
    decorate = __.funct.partial(
        __.ccstd.dataclass_with_standard_behaviors,
        attributes_namer = __.calculate_attrname,
        error_class_provider = _iclasses.provide_error_class,
        assigner_core = _iclasses.assign_attribute_if_absent_mutable,
        decorators = decorators,
        mutables = mutables, visibles = visibles )
    if not __.is_absent( cls ): return decorate( )( cls )
    return decorate( )  # No class to decorate; keyword arguments only.


@__.typx.overload
def with_standard_behaviors( # pragma: no cover
    cls: type[ __.U ], /, *,
    decorators: __.ClassDecorators[ __.U ] = ( ),
    mutables: __.BehaviorExclusionVerifiersOmni = mutables_default,
    visibles: __.BehaviorExclusionVerifiersOmni = visibles_default,
) -> type[ __.U ]: ...


@__.typx.overload
def with_standard_behaviors( # pragma: no cover
    cls: __.AbsentSingleton = __.absent, /, *,
    decorators: __.ClassDecorators[ __.U ] = ( ),
    mutables: __.BehaviorExclusionVerifiersOmni = mutables_default,
    visibles: __.BehaviorExclusionVerifiersOmni = visibles_default,
) -> __.ClassDecoratorFactory[ __.U ]: ...


def with_standard_behaviors(
    cls: __.Absential[ type[ __.U ] ] = __.absent, /, *,
    decorators: __.ClassDecorators[ __.U ] = ( ),
    mutables: __.BehaviorExclusionVerifiersOmni = mutables_default,
    visibles: __.BehaviorExclusionVerifiersOmni = visibles_default,
) -> type[ __.U ] | __.ClassDecoratorFactory[ __.U ]:
    ''' Decorates class to enforce standard behaviors on instances. '''
    decorate = __.funct.partial(
        __.ccstd.with_standard_behaviors,
        attributes_namer = __.calculate_attrname,
        error_class_provider = _iclasses.provide_error_class,
        assigner_core = _iclasses.assign_attribute_if_absent_mutable,
        decorators = decorators,
        mutables = mutables, visibles = visibles )
    if not __.is_absent( cls ): return decorate( )( cls )
    return decorate( )  # No class to decorate; keyword arguments only.
