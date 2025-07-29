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


''' Immutable classes. '''


from . import __


dataclass_core = __.dcls.dataclass( kw_only = True, slots = True )
mutables_default = ( )
visibles_default = ( __.is_public_identifier, )


def assign_attribute_if_absent_mutable( # noqa: PLR0913
    objct: object, /, *,
    ligation: __.AssignerLigation,
    attributes_namer: __.AttributesNamer,
    error_class_provider: __.ErrorClassProvider,
    level: str,
    name: str,
    value: __.typx.Any,
) -> None:
    ''' Assigns attribute if it is absent or mutable, else raises error. '''
    if not hasattr( objct, name ):
        ligation( name, value )
        return
    leveli = 'instance' if level == 'instances' else level
    behaviors_name = attributes_namer( leveli, 'behaviors' )
    behaviors = __.ccutils.getattr0( objct, behaviors_name, frozenset( ) )
    if __.immutability_label not in behaviors:
        ligation( name, value )
        return
    names_name = attributes_namer( level, 'mutables_names' )
    names: __.BehaviorExclusionNamesOmni = (
        getattr( objct, names_name, frozenset( ) ) )
    if names == '*' or name in names:
        ligation( name, value )
        return
    predicates_name = attributes_namer( level, 'mutables_predicates' )
    predicates: __.BehaviorExclusionPredicates = (
        getattr( objct, predicates_name, ( ) ) )
    for predicate in predicates:
        if predicate( name ):
            # TODO? Cache predicate hit.
            ligation( name, value )
            return
    regexes_name = attributes_namer( level, 'mutables_regexes' )
    regexes: __.BehaviorExclusionRegexes = (
        getattr( objct, regexes_name, ( ) ) )
    for regex in regexes:
        if regex.fullmatch( name ):
            # TODO? Cache regex hit.
            ligation( name, value )
            return
    target = __.ccutils.describe_object( objct )
    raise error_class_provider( 'AttributeImmutability' )( name, target )


def provide_error_class( name: str ) -> type[ Exception ]:
    ''' Provides error class for this package. '''
    match name:
        case 'AttributeImmutability':
            from .exceptions import AttributeImmutability as error
        case _:
            from .exceptions import ErrorProvideFailure
            raise ErrorProvideFailure( name, reason = 'Does not exist.' )
    return error


dynadoc_configuration = (
    __.ccstd.dynadoc.produce_dynadoc_configuration( table = __.fragments ) )
_class_factory = __.funct.partial(
    __.ccstd.class_factory,
    attributes_namer = __.calculate_attrname,
    dynadoc_configuration = dynadoc_configuration,
    error_class_provider = provide_error_class )


@_class_factory( )
class Class( type ):
    ''' Metaclass for immutable classes. '''

    _dynadoc_fragments_ = (
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
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
    ''' Metaclass for immutable dataclasses. '''

    _dynadoc_fragments_ = (
        'cfc produce dataclass',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
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
    ''' Metaclass for immutable dataclasses with mutable instances. '''

    _dynadoc_fragments_ = (
        'cfc produce dataclass',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
        'cfc instance conceal' )

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
class AbstractBaseClass( __.abc.ABCMeta ):
    ''' Metaclass for immutable abstract base classes. '''

    _dynadoc_fragments_ = (
        'cfc produce abstract base class',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
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
class ProtocolClass( type( __.typx.Protocol ) ):
    ''' Metaclass for immutable protocol classes. '''

    _dynadoc_fragments_ = (
        'cfc produce protocol class',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
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
    ''' Metaclass for immutable protocol dataclasses. '''

    _dynadoc_fragments_ = (
        'cfc produce protocol class', 'cfc produce dataclass',
        'cfc class conceal', 'cfc class protect', 'cfc dynadoc',
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
class ProtocolDataclassMutable( type( __.typx.Protocol ) ):
    ''' Metaclass for immutable protocol dataclasses with mutable instances.
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
    ) -> __.T:
        return super( ).__new__( clscls, name, bases, namespace )
