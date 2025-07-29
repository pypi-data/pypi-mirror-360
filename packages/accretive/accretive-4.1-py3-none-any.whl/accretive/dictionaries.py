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


''' Accretive dictionaries.

    Dictionaries which can grow but never shrink. Once an entry is added, it
    cannot be modified or removed.

    * :py:class:`AbstractDictionary`:
      Base class defining the accretive dictionary interface. Implementations
      must provide ``__getitem__``, ``__iter__``, ``__len__``, and storage
      methods.

    * :py:class:`Dictionary`:
      Standard implementation of an accretive dictionary. Supports all usual
      dict operations except those that would modify or remove existing
      entries.

    * :py:class:`ProducerDictionary`:
      Automatically generates values for missing keys using a supplied factory
      function. Similar to :py:class:`collections.defaultdict` but with
      accretive behavior.

    * :py:class:`ValidatorDictionary`:
      Validates entries before addition using a supplied predicate function.

    * :py:class:`ProducerValidatorDictionary`:
      Combines producer and validator behaviors. Generated values must pass
      validation before being added.

    >>> from accretive import Dictionary
    >>> d = Dictionary( apples = 12, bananas = 6 )
    >>> d[ 'cherries' ] = 42  # Add new entry
    >>> d[ 'apples' ] = 14    # Attempt modification
    Traceback (most recent call last):
        ...
    accretive.exceptions.EntryImmutability: Could not alter or remove existing entry for 'apples'.
    >>> del d[ 'bananas' ]    # Attempt removal
    Traceback (most recent call last):
        ...
    accretive.exceptions.EntryImmutability: Could not alter or remove existing entry for 'bananas'.

    >>> from accretive import ProducerDictionary
    >>> d = ProducerDictionary( list )  # list() called for missing keys
    >>> d[ 'new' ]
    []
    >>> d[ 'new' ].append( 1 )  # List is mutable, but entry is fixed
    >>> d[ 'new' ] = [ ]  # Attempt modification
    Traceback (most recent call last):
        ...
    accretive.exceptions.EntryImmutability: Could not alter or remove existing entry for 'new'.

    >>> from accretive import ValidatorDictionary
    >>> d = ValidatorDictionary( lambda k, v: isinstance( v, int ) )
    >>> d[ 'valid' ] = 42  # Passes validation
    >>> d[ 'invalid' ] = 'str'  # Fails validation
    Traceback (most recent call last):
        ...
    accretive.exceptions.EntryInvalidity: Could not add invalid entry with key, 'invalid', and value, 'str', to dictionary.
''' # noqa: E501


from . import __
from . import classes as _classes


class AbstractDictionary( __.cabc.Mapping[ __.H, __.V ] ):
    ''' Abstract base class for dictionaries that can grow but not shrink.

        An accretive dictionary allows new entries to be added but prevents
        modification or removal of existing entries. This provides a middle
        ground between immutable and fully mutable mappings.

        Implementations must provide:
        - __getitem__, __iter__, __len__
        - _pre_setitem_ for entry validation/preparation
        - _store_item_ for storage implementation
    '''

    @__.abc.abstractmethod
    def __iter__( self ) -> __.cabc.Iterator[ __.H ]:
        raise NotImplementedError # pragma: no coverage

    @__.abc.abstractmethod
    def __len__( self ) -> int:
        raise NotImplementedError # pragma: no coverage

    @__.abc.abstractmethod
    def __getitem__( self, key: __.H ) -> __.V:
        raise NotImplementedError # pragma: no coverage

    def _pre_setitem_(
        self, key: __.H, value: __.V
    ) -> tuple[ __.H, __.V ]:
        ''' Validates and/or prepares entry before addition.

            Should raise appropriate exception if entry is invalid.
        '''
        return key, value

    @__.abc.abstractmethod
    def _store_item_( self, key: __.H, value: __.V ) -> None:
        ''' Stores entry in underlying storage. '''
        raise NotImplementedError # pragma: no coverage

    def __setitem__( self, key: __.H, value: __.V ) -> None:
        key, value = self._pre_setitem_( key, value )
        if key in self:
            from .exceptions import EntryImmutability
            raise EntryImmutability( key )
        self._store_item_( key, value )

    def __delitem__( self, key: __.H ) -> None:
        from .exceptions import EntryImmutability
        raise EntryImmutability( key )

    def setdefault( self, key: __.H, default: __.V ) -> __.V:
        ''' Returns value for key, setting it to default if missing. '''
        try: return self[ key ]
        except KeyError:
            self[ key ] = default
            return default

    def update(
        self,
        *iterables: __.DictionaryPositionalArgument[ __.H, __.V ],
        **entries: __.DictionaryNominativeArgument[ __.V ],
    ) -> __.typx.Self:
        ''' Adds new entries as a batch. Returns self. '''
        from itertools import chain
        updates: list[ tuple[ __.H, __.V ] ] = [ ]
        for indicator, value in chain.from_iterable( map( # pyright: ignore
            lambda element: ( # pyright: ignore
                element.items( )
                if isinstance( element, __.cabc.Mapping )
                else element
            ),
            ( *iterables, entries )
        ) ):
            indicator_, value_ = (
                self._pre_setitem_( indicator, value ) ) # pyright: ignore
            if indicator_ in self:
                from .exceptions import EntryImmutability
                raise EntryImmutability( indicator_ )
            updates.append( ( indicator_, value_ ) )
        for indicator, value in updates: self._store_item_( indicator, value )
        return self


class _DictionaryOperations( AbstractDictionary[ __.H, __.V ] ):
    ''' Mix-in providing additional dictionary operations. '''

    def __init__(
        self, *posargs: __.typx.Any, **nomargs: __.typx.Any
    ) -> None:
        super( ).__init__( *posargs, **nomargs )

    def __or__( self, other: __.cabc.Mapping[ __.H, __.V ] ) -> __.typx.Self:
        if not isinstance( other, __.cabc.Mapping ): return NotImplemented
        conflicts = set( self.keys( ) ) & set( other.keys( ) )
        if conflicts:
            from .exceptions import EntryImmutability
            raise EntryImmutability( next( iter( conflicts ) ) )
        data = dict( self )
        data.update( other )
        return self.with_data( data )

    def __ror__( self, other: __.cabc.Mapping[ __.H, __.V ] ) -> __.typx.Self:
        if not isinstance( other, __.cabc.Mapping ): return NotImplemented
        return self | other

    def __and__(
        self,
        other: __.cabc.Set[ __.H ] | __.cabc.Mapping[ __.H, __.V ]
    ) -> __.typx.Self:
        if isinstance( other, __.cabc.Mapping ):
            return self.with_data( # pyright: ignore
                ( key, value ) for key, value in self.items( )
                if key in other and other[ key ] == value )
        if isinstance( other, ( __.cabc.Set, __.cabc.KeysView ) ):
            return self.with_data( # pyright: ignore
                ( key, self[ key ] ) for key in self.keys( ) & other )
        return NotImplemented

    def __rand__(
        self,
        other: __.cabc.Set[ __.H ] | __.cabc.Mapping[ __.H, __.V ]
    ) -> __.typx.Self:
        if not isinstance(
            other, ( __.cabc.Mapping, __.cabc.Set, __.cabc.KeysView )
        ): return NotImplemented
        return self & other

    @__.abc.abstractmethod
    def copy( self ) -> __.typx.Self:
        ''' Provides fresh copy of dictionary. '''
        raise NotImplementedError # pragma: no coverage

    @__.abc.abstractmethod
    def with_data(
        self,
        *iterables: __.DictionaryPositionalArgument[ __.H, __.V ],
        **entries: __.DictionaryNominativeArgument[ __.V ],
    ) -> __.typx.Self:
        ''' Creates new dictionary with same behavior but different data. '''
        raise NotImplementedError # pragma: no coverage


class Dictionary(
    _DictionaryOperations[ __.H, __.V ],
    metaclass = _classes.AbstractBaseClass,
):
    ''' Accretive dictionary. '''

    __slots__ = ( '_data_', )

    _data_: __.AccretiveDictionary[ __.H, __.V ]
    _dynadoc_fragments_ = ( 'dictionary entries accrete', )

    def __init__(
        self,
        *iterables: __.DictionaryPositionalArgument[ __.H, __.V ],
        **entries: __.DictionaryNominativeArgument[ __.V ],
    ) -> None:
        self._data_ = __.AccretiveDictionary( *iterables, **entries )
        super( ).__init__( )

    __hash__ = None

    def __iter__( self ) -> __.cabc.Iterator[ __.H ]:
        return iter( self._data_ )

    def __len__( self ) -> int:
        return len( self._data_ )

    def __repr__( self ) -> str:
        return "{fqname}( {contents} )".format(
            fqname = __.ccutils.qualify_class_name( type( self ) ),
            contents = str( self._data_ ) )

    def __str__( self ) -> str:
        return str( self._data_ )

    def __contains__( self, key: __.typx.Any ) -> bool:
        return key in self._data_

    def __getitem__( self, key: __.H ) -> __.V:
        return self._data_[ key ]

    def __eq__( self, other: __.typx.Any ) -> __.ComparisonResult:
        if isinstance( other, __.cabc.Mapping ):
            return self._data_ == other
        return NotImplemented

    def __ne__( self, other: __.typx.Any ) -> __.ComparisonResult:
        if isinstance( other, __.cabc.Mapping ):
            return self._data_ != other
        return NotImplemented

    def copy( self ) -> __.typx.Self:
        ''' Provides fresh copy of dictionary. '''
        return type( self )( self )

    def get( # pyright: ignore
        self, key: __.H, default: __.Absential[ __.V ] = __.absent
    ) -> __.typx.Annotated[
        __.V,
        __.typx.Doc(
            'Value of entry, if it exists. '
            'Else, supplied default value or ``None``.' )
    ]:
        ''' Retrieves entry associated with key, if it exists. '''
        if __.is_absent( default ):
            return self._data_.get( key ) # pyright: ignore
        return self._data_.get( key, default )

    def keys( self ) -> __.cabc.KeysView[ __.H ]:
        ''' Provides iterable view over dictionary keys. '''
        return self._data_.keys( )

    def items( self ) -> __.cabc.ItemsView[ __.H, __.V ]:
        ''' Provides iterable view over dictionary items. '''
        return self._data_.items( )

    def values( self ) -> __.cabc.ValuesView[ __.V ]:
        ''' Provides iterable view over dictionary values. '''
        return self._data_.values( )

    def with_data(
        self,
        *iterables: __.DictionaryPositionalArgument[ __.H, __.V ],
        **entries: __.DictionaryNominativeArgument[ __.V ],
    ) -> __.typx.Self:
        return type( self )( *iterables, **entries )

    def _store_item_( self, key: __.H, value: __.V ) -> None:
        self._data_[ key ] = value


class ProducerDictionary( Dictionary[ __.H, __.V ] ):
    ''' Accretive dictionary with default value for missing entries. '''

    __slots__ = ( '_producer_', )

    _dynadoc_fragments_ = (
        'dictionary entries accrete', 'dictionary entries produce' )
    _producer_: __.DictionaryProducer[ __.V ]

    def __init__(
        self,
        producer: __.DictionaryProducer[ __.V ],
        /,
        *iterables: __.DictionaryPositionalArgument[ __.H, __.V ],
        **entries: __.DictionaryNominativeArgument[ __.V ],
    ):
        # TODO: Validate producer argument.
        self._producer_ = producer
        super( ).__init__( *iterables, **entries )

    def __repr__( self ) -> str:
        return "{fqname}( {producer}, {contents} )".format(
            fqname = __.ccutils.qualify_class_name( type( self ) ),
            producer = self._producer_,
            contents = str( self._data_ ) )

    def __getitem__( self, key: __.H ) -> __.V:
        if key not in self:
            value = self._producer_( )
            self[ key ] = value
        else: value = super( ).__getitem__( key )
        return value

    def copy( self ) -> __.typx.Self:
        ''' Provides fresh copy of dictionary. '''
        dictionary = type( self )( self._producer_ )
        return dictionary.update( self )

    def setdefault( self, key: __.H, default: __.V ) -> __.V:
        ''' Returns value for key, setting it to default if missing. '''
        if key not in self:
            self[ key ] = default
            return default
        return self[ key ]

    def with_data(
        self,
        *iterables: __.DictionaryPositionalArgument[ __.H, __.V ],
        **entries: __.DictionaryNominativeArgument[ __.V ],
    ) -> __.typx.Self:
        return type( self )( self._producer_, *iterables, **entries )


class ValidatorDictionary( Dictionary[ __.H, __.V ] ):
    ''' Accretive dictionary with validation of new entries. '''

    __slots__ = ( '_validator_', )

    _dynadoc_fragments_ = (
        'dictionary entries accrete', 'dictionary entries validate' )
    _validator_: __.DictionaryValidator[ __.H, __.V ]

    def __init__(
        self,
        validator: __.DictionaryValidator[ __.H, __.V ],
        /,
        *iterables: __.DictionaryPositionalArgument[ __.H, __.V ],
        **entries: __.DictionaryNominativeArgument[ __.V ],
    ) -> None:
        self._validator_ = validator
        super( ).__init__( *iterables, **entries )

    def __repr__( self ) -> str:
        return "{fqname}( {validator}, {contents} )".format(
            fqname = __.ccutils.qualify_class_name( type( self ) ),
            validator = self._validator_,
            contents = str( self._data_ ) )

    def _pre_setitem_( self, key: __.H, value: __.V ) -> tuple[ __.H, __.V ]:
        if not self._validator_( key, value ):
            from .exceptions import EntryInvalidity
            raise EntryInvalidity( key, value )
        return key, value

    def copy( self ) -> __.typx.Self:
        ''' Provides fresh copy of dictionary. '''
        dictionary = type( self )( self._validator_ )
        return dictionary.update( self )

    def with_data(
        self,
        *iterables: __.DictionaryPositionalArgument[ __.H, __.V ],
        **entries: __.DictionaryNominativeArgument[ __.V ],
    ) -> __.typx.Self:
        return type( self )( self._validator_, *iterables, **entries )


class ProducerValidatorDictionary( Dictionary[ __.H, __.V ] ):
    ''' Accretive dictionary with defaults and validation. '''

    __slots__ = ( '_producer_', '_validator_' )

    _dynadoc_fragments_ = (
        'dictionary entries accrete',
        'dictionary entries produce',
        'dictionary entries validate' )
    _producer_: __.DictionaryProducer[ __.V ]
    _validator_: __.DictionaryValidator[ __.H, __.V ]

    def __init__(
        self,
        producer: __.DictionaryProducer[ __.V ],
        validator: __.DictionaryValidator[ __.H, __.V ],
        /,
        *iterables: __.DictionaryPositionalArgument[ __.H, __.V ],
        **entries: __.DictionaryNominativeArgument[ __.V ],
    ) -> None:
        self._producer_ = producer
        self._validator_ = validator
        super( ).__init__( *iterables, **entries )

    def __repr__( self ) -> str:
        return "{fqname}( {producer}, {validator}, {contents} )".format(
            fqname = __.ccutils.qualify_class_name( type( self ) ),
            producer = self._producer_,
            validator = self._validator_,
            contents = str( self._data_ ) )

    def __getitem__( self, key: __.H ) -> __.V:
        if key not in self:
            value = self._producer_( )
            if not self._validator_( key, value ):
                from .exceptions import EntryInvalidity
                raise EntryInvalidity( key, value )
            self[ key ] = value
        else: value = super( ).__getitem__( key )
        return value

    def _pre_setitem_( self, key: __.H, value: __.V ) -> tuple[ __.H, __.V ]:
        if not self._validator_( key, value ):
            from .exceptions import EntryInvalidity
            raise EntryInvalidity( key, value )
        return key, value

    def copy( self ) -> __.typx.Self:
        ''' Provides fresh copy of dictionary. '''
        dictionary = type( self )( self._producer_, self._validator_ )
        return dictionary.update( self )

    def setdefault( self, key: __.H, default: __.V ) -> __.V:
        ''' Returns value for key, setting it to default if missing. '''
        if key not in self:
            self[ key ] = default
            return default
        return self[ key ]

    def with_data(
        self,
        *iterables: __.DictionaryPositionalArgument[ __.H, __.V ],
        **entries: __.DictionaryNominativeArgument[ __.V ],
    ) -> __.typx.Self:
        return type( self )(
            self._producer_, self._validator_, *iterables, **entries )
