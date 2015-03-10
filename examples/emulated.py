#!/usr/bin/env python


"""
Emulated Containers for Creating Vim Snippets

These classes are not intended for literal use in a module.  They are written
to help build templates/snippets to use with an editor or code generator.
Since some of these templates contain a fair amount of code, I wanted to
ensure that I wasn't inserting code that doesn't work.

The use case is to create snippets based on these classes, insert the snippet
when needed, then modify the class to the needs of the module (probably by
deleting a lot of unused methods).

To create snipMate snippets, each class contains Vim substitution commands
that can be executed to convert the Python code into automated snippet syntax.
See the `docstring` under each class.
"""


import os


__version__ = '0.0.0'


#=============================================================================
class Descriptor( object ):
    """
    Provides a template for creating a complete descriptor class.

    1,.-1s/Descriptor/\$\{1:Descriptor\}/g
    .+1,$s/Descriptor/\$1/g
    """

    #=========================================================================
    def __init__( self, name, doc = '' ):
        """
        Initializes a Descriptor object.

        @param name The name of the object's property
        @param doc  The property's docstring
        """
        super( Descriptor, self ).__init__()
        self._name   = name
        self.__doc__ = doc


    #=========================================================================
    def __delete__( self, obj ):
        """
        Deletes the described property from the object.

        @param obj The property's owner instance
        """
        if hasattr( obj, self._name ) == False:
            raise AttributeError(
                'Unable to delete unknown property "{}".'.format( self._name )
            )
        delattr( obj, self._name )


    #=========================================================================
    def __get__( self, obj, objtype = None ):
        """
        Returns the value of the described property.

        @param obj     The property's owner instance
        @param objtype The owner instance's type or class
        @return        The return value of the specified getter method
        """
        if obj is None:
            return self
        if hasattr( obj, self._name ) == False:
            raise AttributeError(
                'Unable to get unknown property "{}".'.format( self._name )
            )
        return getattr( obj, self._name )


    #=========================================================================
    def __set__( self, obj, value ):
        """
        Modifies the value of the described property.

        @param obj   The property's owner instance
        @param value The value to pass to the specified setter method
        """
        if hasattr( obj, self._name ) == False:
            raise AttributeError(
                'Unable to set unknown property "{}".'.format( self._name )
            )
        setattr( obj, self._name )


#=============================================================================
class ReadStateDscr( object ):
    """
    Implements a descriptor to enforce read-only, state-style attributes.

    1,.-1s/ReadStateDscr/\$\{1:ReadStateDscr\}/g
    .+1,$s/ReadStateDscr/\$1/g
    """

    #=========================================================================
    def __init__( self, name, doc = '' ):
        """
        Initializes a ReadStateDscr object.
        """
        self._name   = name
        self.__doc__ = doc


    #=========================================================================
    def __get__( self, obj, objtype = None ):
        """
        Retrieves the state of this attribute.
        """
        if obj is None:
            return self
        return getattr( obj, self._name )


#=============================================================================
class BaseStream( object ):
    """
    Implements attributes common to both input and output stream objects.

    Dependencies

        import os
        class ReadStateDescr

    1,.-1s/BaseStream/\$\{1:BaseStream\}/g
    .+1,$s/BaseStream/\$1/g
    """

    #=========================================================================
    # public properties

    # stream closed state
    _closed = True
    closed = ReadStateDscr( '_closed', 'Stream closed state (bool)' )

    # string encoding used by this stream
    _encoding = None
    encoding = ReadStateDscr( '_encoding', 'Stream string encoding.' )

    # the unicode error handler used along with the encoding
    errors = None

    # current mode of the stream
    _mode = 'r'
    mode = ReadStateDscr( '_mode', 'File I/O mode.' )

    # named representation of the stream (e.g. file name)
    _name = ''
    name = ReadStateDscr( '_name', 'Named representation of the stream.' )

    # allow the built-in `print` implementation to keep state in stream
    softspace = 0


    #=========================================================================
    def __init__( self ):
        """
        Initializes a BaseStream object.
        """
        super( BaseStream, self ).__init__()


    #=========================================================================
    def close( self ):
        """
        Closes the file-like stream.
        """
        self._closed = True


    #=========================================================================
    def flush( self ):
        """
        Flushes the internal buffer.
        """
        pass


    #=========================================================================
    # Do not implement if the object does not have a real file descriptor.
    #def fileno( self ):
    #    """
    #    Returns the integer file descriptor.
    #    """
    #    pass


    #=========================================================================
    # Do not implement if the object is not using a real file.
    #def isatty( self ):
    #    """
    #    Tests the stream to determine if it is a TTY (or similar) device.
    #    """
    #    pass


    #=========================================================================
    def seek( self, offset, whence = os.SEEK_SET ):
        """
        Moves the stream's internal position to a new offset.

        @param offset The new offset
        @param whence The reference point of the new offset.  One of:
                      os.SEEK_SET (0): relative the start of the stream
                      os.SEEK_CUR (1): relative the current position
                      os.SEEK_END (2): relative the end of the stream
        """
        pass


    #=========================================================================
    def tell( self ):
        """
        Returns the current position in the stream.
        """
        return 0


#=============================================================================
class InputStream( BaseStream ):
    """
    Emulates a file-like stream for reading data.

    Dependencies

        import os
        class ReadStateDscr
        class BaseStream

    1,.-1s/InputStream/\$\{1:InputStream\}/g
    .+1,$s/InputStream/\$1/g
    """

    #=========================================================================
    # public properties

    # newline style or list of styles encountered in stream
    _newlines = None
    newlines = ReadStateDscr( '_newlines', 'Newlines in stream.' )


    #=========================================================================
    def __init__( self ):
        """
        Initializes an InputStream object.
        """
        pass


    #=========================================================================
    def next( self ):
        """
        Returns the next element from the stream.
        """
        if True:
            raise StopIteration()


    #=========================================================================
    def read( self, size = 0 ):
        """
        Reads data from the stream.

        @param size Limit the maximum number of bytes to return
        @return     Stream data as a string
        """
        has_reached_eof = True
        if has_reached_eof == True:
            return ''
        if size > 0:
            return 'a specified number of bytes from the stream'[ : size ]
        return 'remaining data in stream'


    #=========================================================================
    def readline( self, size = 0 ):
        """
        Reads the next line from the stream.
        If the line is complete, the trailing line terminator is included.

        @param size Limit the maximum number of bytes to return
        @return     The next line from the stream
        """
        return '\n'


    #=========================================================================
    def readlines( self, sizehint = 0 ):
        """
        Reads all remaining lines from the stream.

        @param sizehint Limit the approximate bytes read from the stream
        return          A list of all remaining lines in the stream
        """
        return []


#=============================================================================
class OutputStream( BaseStream ):
    """
    Emulates a file-like stream that can accept output.

    Dependencies

        class BaseStream

    1,.-1s/OutputStream/\$\{1:OutputStream\}/g
    .+1,$s/OutputStream/\$1/g
    """

    #=========================================================================
    def __init__( self ):
        """
        Initializes an OutputStream object.
        """
        super( OutputStream, self ).__init__()


    #=========================================================================
    def truncate( self, size = 0 ):
        """
        Truncate the file's size.  If the size is not specified, the file is
        truncated to the current position.  If the size is specified, the file
        _should_ be that size after truncation (which may include making the
        file larger if it is smaller than the given size).
        """
        pass


    #=========================================================================
    def write( self, string ):
        """
        Writes data to the stream.
        """
        pass


    #=========================================================================
    def writelines( self, sequence ):
        """
        Writes a sequence of strings to the file.  Line separators are not
        added by this method; each item in the sequence should terminate
        themselves.
        """
        pass


#=============================================================================
class ImmutableMapEmulator( object ):
    """
    Emulates an immutable mapping as an object.
    This is used in place of attempting to subclass the `dict` container, and
    has the added benefit of being a read-only (by convention) structure.

    1,.-1s/ImmutableMapEmulator/\$\{1:ImMap\}/g
    .+1,$s/ImmutableMapEmulator/\$1/g
    .+3,.+10s/_data/\$\{2:_data\}/g
    .+11,$s/_data/\$2/g
    """

    #=========================================================================
    def __init__( self, *args, **kwargs ):
        """
        Initializes an ImmutableMapEmulator object.
        """
        self._data = dict( *args, **kwargs )


    #=========================================================================
    def __contains__( self, key ):
        """
        Checks for the presense of a key in the map using the `in` construct.
        """
        return key in self._data


    #=========================================================================
    def __getitem__( self, key ):
        """
        Provides key access to data in the map.
        """
        return self._data[ key ]


    #=========================================================================
    def __iter__( self ):
        """
        Produces an iterator for the data in the map.
        """
        return iter( self._data )


    #=========================================================================
    def __len__( self ):
        """
        Returns the number of items in the map.
        """
        return len( self._data )


    #=========================================================================
    def __str__( self ):
        """
        Represents this map as a string.
        """
        keys    = self._data.keys()
        max_key = max( len( key ) for key in keys )
        fmt     = '"{1}"{0} : {2}'
        pairs   = []
        for key in keys:
            value = self._data[ key ]
            if type( value ) is str:
                value = '"' + value + '"'
            pad = max_key - len( key )
            pairs.append( fmt.format( ( ' ' * pad ), key, value ) )
        return '{\n    ' + ( ',\n    '.join( pairs ) ) + '\n}'


    #=========================================================================
    def copy( self ):
        """
        Returns a shallow copy of the data in the map.
        """
        return self._data.copy()


    #=========================================================================
    def get( self, key, default = None ):
        """
        Returns the value of a given key if it is in the map.
        If it is not in the map, return the default value.
        """
        return self._data.get( key, default )


    #=========================================================================
    def has_key( self, key ):
        """
        Tests for the presense of a key in the map.
        """
        return self._data.has_key( key )


    #=========================================================================
    def items( self ):
        """
        Returns a list of the map's key-value pairs.
        """
        return self._data.items()


    #=========================================================================
    def iteritems( self ):
        """
        Returns an iterator over the list of the map's key-value pairs.
        """
        return self._data.iteritems()


    #=========================================================================
    def iterkeys( self ):
        """
        Returns an iterator over the map's keys.
        """
        return self._data.iterkeys()


    #=========================================================================
    def itervalues( self ):
        """
        Returns an iterator over the map's values.
        """
        return self._data.itervalues()


    #=========================================================================
    def keys( self ):
        """
        Returns a list of the map's keys.
        """
        return self._data.keys()


    #=========================================================================
    def values( self ):
        """
        Returns a list of the map's values.
        """
        return self._data.values()


#=============================================================================
class MutableMapEmulator( ImmutableMapEmulator ):
    """
    Emulates a mutable mapping as an object.
    This is used in place of attempting to subclass the `dict` container.
    Note: This container relies on having ImmutableMapEmulator container in
    the same module.  If that is not desired, simply copy its methods into
    this class, and subclass `object` instead of ImmutableMapEmulator.

    1,.-1s/MutableMapEmulator/\$\{1:MMap\}/g
    .+1,$s/MutableMapEmulator/\$1/g
    .+3,.+18s/_data/\$\{2:_data\}/g
    .+19,$s/_data/\$2/g
    """

    #=========================================================================
    def __init__( self, *args, **kwargs ):
        """
        Initializes a MutableMapEmulator object.
        """
        super( MutableMapEmulator, self ).__init__( *args, **kwargs )


    #=========================================================================
    def __delitem__( self, key ):
        """
        Removes an item from the map with the given key.
        """
        del self._data[ key ]


    #=========================================================================
    def __setitem__( self, key, value ):
        """
        Modifies a value in the map with the given key.
        """
        self._data[ key ] = value


    #=========================================================================
    def clear( self ):
        """
        Removes all items from the map.
        """
        self._data.clear()


    #=========================================================================
    def pop( self, key, *args ):
        """
        Removes and returns an item from the map with the given key.
        If the key doesn't exist, and default is given, return default.
        """
        if len( args ) > 0:
            return self._data.pop( key, args[ 0 ] )
        return self._data.pop( key )


    #=========================================================================
    def popitem( self ):
        """
        Removes and returns an arbitrary key-value pair from the map.
        """
        return self._data.popitem()


    #=========================================================================
    def setdefault( self, key, default = None ):
        """
        Returns the value of key from the map.
        If the key doesn't exist, insert a new item into the map with the
        value specified.
        """
        return self._data.setdefault( key, default )

    #=========================================================================
    def update( self, other ):
        """
        Updates the map with the given key-value pairs, dict, or map.
        Returns None.
        """
        return self._data.update( other )


#=============================================================================
class ImmutableSequenceEmulator( object ):
    """
    Emulates an immutable sequence as an object.
    This is used in place of attempting to subclass the `tuple` container.

    1,.-1s/ImmutableSequenceEmulator/\$\{1:ImSequence\}/g
    .+1,$s/ImmutableSequenceEmulator/\$1/g
    .+3,.+10s/_data/\$\{2:_data\}/g
    .+11,$s/_data/\$2/g
    """

    #=========================================================================
    def __init__( self, *args, **kwargs ):
        """
        Initializes an ImmutableSequenceEmulator object.
        """
        self._data = list( *args, **kwargs )


    #=========================================================================
    def __add__( self, other ):
        """
        Implements sequence concatenation via the `+` operator.
        """
        if type( other ) != list:
            other = list( other )
        return self._data + other


    #=========================================================================
    def __cmp__( self, other ):
        """
        Implements sequence comparison via the `==`, `!=`, `<=`, and `>=`
        operators.
        """
        num_mine   = len( self._data )
        num_theirs = len( other )
        num_diff   = num_mine - num_theirs
        if num_diff != 0:
            return num_diff
        for index in range( num_mine ):
            diff = self._data[ index ] - other[ index ]
            if diff != 0:
                return diff
        return 0


    #=========================================================================
    def __contains__( self, value ):
        """
        Provides support for searching the sequence using the `in` construct.
        """
        return value in self._data


    #=========================================================================
    def __getitem__( self, index ):
        """
        Dereference an item in the sequence by index.
        """
        if isinstance( index, int ):
            return self._data[ index ]
        elif isinstance( index, slice ):
            start, stop, step = index.indices( len( self._data ) )
            return self._data[ start : stop : step ]
        else:
            raise TypeError( 'Sequence indexes must be integers or slices.' )


    #=========================================================================
    def __iter__( self ):
        """
        Provides an iterator for the sequence.
        """
        return iter( self._data )


    #=========================================================================
    def __len__( self ):
        """
        Get the length of the sequence.
        """
        return len( self._data )


    #=========================================================================
    def __mul__( self, other ):
        """
        Implements sequence repitition via the `*` operator.
        """
        return self._data * other


    #=========================================================================
    def __radd__( self, other ):
        """
        Implements reflected sequence concatenation via the `+` operator.
        """
        if type( other ) != list:
            other = list( other )
        return other + self._data


    #=========================================================================
    def __rmul__( self, other ):
        """
        Implements reflected sequence repitition via the `*` operator.
        """
        return other * self._data


    #=========================================================================
    def __str__( self ):
        """
        Returns a string representation of the sequence.
        """
        return '( {} )'.format( ', '.join( str( v ) for v in self._data ) )


    #=========================================================================
    def count( self, value ):
        """
        Counts the number of occurrences of a value in the sequence.
        """
        return self._data.count( value )


    #=========================================================================
    def index( self, value ):
        """
        Returns the first occurrence of a value in the sequence.
        """
        return self._data.index( value )


#=============================================================================
class MutableSequenceEmulator( ImmutableSequenceEmulator ):
    """
    Emulates a mutable sequence as an object.
    This is used in place of attempting to subclass the `list` container.
    Note: This container relies on having ImmutableSequenceEmulator container
    in the same module.  If that is not desired, simply copy its methods into
    this class, and subclass `object` instead of ImmutableSequenceEmulator.

    1,.-1s/MutableSequenceEmulator/\$\{1:MSequence\}/g
    .+1,$s/MutableSequenceEmulator/\$1/g
    .+3,.+18s/_data/\$\{2:_data\}/g
    .+19,$s/_data/\$2/g
    """

    #=========================================================================
    def __init__( self, *args, **kwargs ):
        """
        Initializes a MutableSequenceEmulator object.
        """
        super( MutableSequenceEmulator, self ).__init__( *args, **kwargs )


    #=========================================================================
    def __delitem__( self, index ):
        """
        Deletes an item or items from the sequence at a given index or slice.
        """
        if isinstance( index, int ):
            del self._data[ index ]
        elif isinstance( index, slice ):
            start, stop, step = index.indices( len( self._data ) )
            del self._data[ start : stop : step ]
        else:
            raise TypeError( 'Sequence indexes must be integers or slices.' )


    #=========================================================================
    def __iadd__( self, other ):
        """
        Implements augmented addition to extend the sequence.
        """
        if type( other ) != list:
            other = list( other )
        self._data += other
        return self


    #=========================================================================
    def __imul__( self, other ):
        """
        Implements augmented multiplication to repeat the sequence in place.
        """
        self._data *= other
        return self


    #=========================================================================
    def __setitem__( self, index, value ):
        """
        Modifies an item or items in the sequence at a given index or slice.
        """
        if isinstance( index, int ):
            self._data[ index ] = value
        elif isinstance( index, slice ):
            start, stop, step = index.indices( len( self._data ) )
            self._data[ start : stop : step ] = value
        else:
            raise TypeError( 'Sequence indexes must be integers or slices.' )


    #=========================================================================
    def __str__( self ):
        """
        Returns a string representation of the sequence.
        """
        return '[ {} ]'.format( ', '.join( str( v ) for v in self._data ) )


    #=========================================================================
    def append( self, value ):
        """
        Appends a value to the end of the sequence.
        """
        self._data.append( value )


    #=========================================================================
    def extend( self, sequence ):
        """
        Extends the sequence by appending the given sequence.
        """
        self._data.extend( sequence )


    #=========================================================================
    def insert( self, index, value ):
        """
        Inserts a value at the given index.
        """
        self._data.insert( index, value )


    #=========================================================================
    def pop( self, index = None ):
        """
        Removes a value at the given index, and returns it.
        """
        if index is None:
            index = len( self._data ) - 1
        return self._data.pop( index )


    #=========================================================================
    def remove( self, value ):
        """
        Removes the first given value and returns it.
        """
        self._data.remove( value )


    #=========================================================================
    def reverse( self ):
        """
        Reverses the values in the sequence, in place.
        """
        self._data.reverse()


    #=========================================================================
    def sort( self, cmp = None, key = None, reverse = False ):
        """
        Sorts the values, in place.
        """
        self._data.sort( cmp, key, reverse )



#=============================================================================
def _test_dscr( log ):
    """
    Tests the Descriptor
    """

    log.put( 'Descriptor' )

    class HostClass:
        x = Descriptor( '_x', 'Property X' )
        def __init__( self, log ):
            self._x = 42

    host = HostClass( log )

    # __get__
    test = host.x
    if test != 42:
        log.fail( '__get__' )

    # __set__
    host.x = 43
    if host.x != 43:
        log.fail( '__set__' )

    # __delete__
    #del host.x
    #if hasattr( host, '_x' ):
    #    log.fail( '__del__' )


#=============================================================================
def _test_bas( log ):
    """
    Tests the BaseStream
    """

    log.put( 'BaseStream' )

    bas = BaseStream()

    # closed
    if bas.closed != True:
        log.fail( 'closed' )

    # encoding
    if bas.encoding != None:
        log.fail( 'encoding' )

    # errors
    if bas.errors != None:
        log.fail( 'errors' )

    # mode
    if bas.mode != 'r':
        log.fail( 'mode' )

    # softspace
    if bas.softspace != 0:
        log.fail( 'softspace' )

    # close
    bas.close()
    if bas.closed != True:
        log.fail( 'close' )

    # flush
    bas.flush()

    # fileno
    #bas.fileno()

    # isatty
    #bas.isatty()

    # seek
    bas.seek( 42, os.SEEK_CUR )

    # tell
    position = bas.tell()
    if position != 0:
        log.fail( 'tell' )


#=============================================================================
def _test_ips( log ):
    """
    Tests the InputStream
    """

    log.put( 'InputStream' )

    ips = InputStream()

    # newlines
    if ips.newlines != None:
        log.fail( 'newlines' )

    # next
    try:
        ips.next()
    except StopIteration:
        pass
    else:
        log.fail( 'next' )

    # read
    empty = ips.read()
    if empty != '':
        log.fail( 'read' )

    # readline
    default = ips.readline()
    if default != '\n':
        log.fail( 'readline' )

    # readlines
    lines = ips.readlines()
    if ( type( lines ) is not list ) or ( len( lines ) != 0 ):
        log.fail( 'readlines' )


#=============================================================================
def _test_ops( log ):
    """
    Tests the OutputStream
    """

    log.put( 'OutputStream' )

    ops = OutputStream()

    # truncate
    ops.truncate()

    # write
    ops.write( 'data' )

    # writelines
    ops.writelines( [ 'one\n', 'two\n' ] )


#=============================================================================
def _test_ime( log ):
    """
    Tests the ImmutableMapEmulator
    """

    log.put( 'ImmutableMapEmulator' )

    init_dict = { 'a_key' : 1, 'a_longer_key' : 2, 'some_key' : 'hello' }

    ime = ImmutableMapEmulator( init_dict )

    # __contains__
    if ( 'some_key' not in ime ) or ( 'fake_key' in ime ):
        log.fail( '__contains__' )

    # __getitem__
    try:
        dummy = ime[ 'some_key' ]
    except:
        log.fail( '__getitem__' )
    try:
        dummy = ime[ 'fake_key' ]
    except:
        pass
    else:
        log.fail( '__getitem__' )

    # __iter__
    for key in ime:
        if key not in init_dict:
            log.fail( '__iter__' )

    # __len__
    if len( ime ) != len( init_dict ):
        log.fail( '__len__' )

    # copy
    copy = ime.copy()
    for key in copy:
        if key not in ime:
            log.fail( 'copy' )

    # get
    value = ime.get( 'some_key' )
    if value != init_dict[ 'some_key' ]:
        log.fail( 'get' )

    # has_key
    if ( ime.has_key( 'some_key' ) == False ) \
    or ( ime.has_key( 'fake_key' ) == True ):
        log.fail( 'has_key' )

    # items
    for k, v in ime.items():
        if ( k not in init_dict ) \
        or ( v != init_dict[ k ] ):
            log.fail( 'items' )

    # iteritems
    iteritems = ime.iteritems()
    for k, v in iteritems:
        if ( k not in ime ) or ( ime[ k ] != v ):
            log.fail( 'iteritems' )

    # iterkeys
    iterkeys = ime.iterkeys()
    for k in iterkeys:
        if ( k not in ime ) or ( ime[ k ] != init_dict[ k ] ):
            log.fail( 'iterkeys' )

    # itervalues
    itervalues = ime.itervalues()
    values = init_dict.values()
    for v in itervalues:
        if v not in values:
            log.fail( 'itervalues' )

    # keys
    keys = ime.keys()
    for key in keys:
        if key not in ime:
            log.fail( 'keys' )

    # values
    values = ime.values()
    ivalues = init_dict.values()
    for value in values:
        if value not in ivalues:
            log.fail( 'values' )

    # __str__
    log.put( str( ime ) )


#=============================================================================
def _test_mme( log ):
    """
    Tests the MutableMapEmulator
    """

    log.put( 'MutableMapEmulator' )

    init_dict = { 'a_key' : 1, 'a_longer_key' : 2, 'some_key' : 'hello' }

    # __delitem__
    mme = MutableMapEmulator( init_dict )
    del mme[ 'a_key' ]
    if 'a_key' in mme:
        log.fail( '__del__' )

    # __setitem__
    mme = MutableMapEmulator( init_dict )
    mme[ 'a_key' ] = 42
    if mme[ 'a_key' ] == 1:
        log.fail( '__setitem__' )

    # clear
    mme = MutableMapEmulator( init_dict )
    mme.clear()
    if len( mme ) > 0:
        log.fail( '__clear__' )

    # pop
    mme = MutableMapEmulator( init_dict )
    value = mme.pop( 'a_key' )
    if value != 1:
        log.fail( 'pop' )

    # popitem
    mme = MutableMapEmulator( init_dict )
    item = mme.popitem()
    if len( item ) != 2:
        log.fail( 'popitem' )
    elif item[ 0 ] not in init_dict:
        log.fail( 'popitem' )

    # setdefault
    mme = MutableMapEmulator( init_dict )
    value = mme.setdefault( 'a_key', 42 )
    if value != 1:
        log.fail( 'setdefault' )
    value = mme.setdefault( 'new_key', 3 )
    if value != 3:
        log.fail( 'setdefault' )

    # update
    mme = MutableMapEmulator( init_dict )
    mme.update( { 'a_key' : 42, 'new_key' : 3 } )
    if mme[ 'a_key' ] != 42:
        log.fail( 'update' )
    elif ( 'new_key' not in mme ) or ( mme[ 'new_key' ] != 3 ):
        log.fail( 'update' )

    # __str__
    log.put( str( mme ) )

    return True


#=============================================================================
def _test_ise( log ):
    """
    Tests the ImmutableSequenceEmulator.
    """

    log.put( 'ImmutableSequenceEmulator' )

    init_tuple = ( 1, 2, 3, 4 )

    ise = ImmutableSequenceEmulator( init_tuple )

    # __add__
    both = ise + ( 5, 6, 7, 8 )
    if len( both ) != ( 4 + len( init_tuple ) ):
        log.fail( '__add__' )

    # __cmp__
    if ise != init_tuple:
        log.fail( '__cmp__' )
    if ise == ( 4, 3, 2, 1 ):
        log.fail( '__cmp__' )
    if ise <= ( 0, 1, 2, 3 ):
        log.fail( '__cmp__' )
    if ise >= ( 2, 3, 4, 5 ):
        log.fail( '__cmp__' )

    # __contains__
    if 2 not in ise:
        log.fail( '__contains__' )

    # __getitem__
    two = ise[ 1 ]
    if two != 2:
        log.fail( '__getitem__' )
    twothree = ise[ 1 : 3 ]
    if len( twothree ) != 2:
        log.fail( '__getitem__' )
    if ( twothree[ 0 ] != 2 ) or ( twothree[ 1 ] != 3 ):
        log.fail( '__getitem__' )

    # __iter__
    for value in ise:
        if value not in init_tuple:
            log.fail( '__iter__' )

    # __len__
    if len( ise ) != len( init_tuple):
        log.fail( '__len__' )

    # __mul__
    tripled = ise * 3
    if len( tripled ) != ( 3 * len( init_tuple ) ):
        log.fail( '__mul__' )

    # __radd__
    rboth = ( -3, -2, -1, 0 ) + ise
    if len( rboth ) != ( 4 + len( init_tuple ) ):
        log.fail( '__radd__' )

    # __rmul__
    rtripled = 3 * ise
    if len( rtripled ) != ( 3 * len( init_tuple ) ):
        log.fail( '__rmul__' )

    # count
    num_twos = ise.count( 2 )
    if num_twos != 1:
        log.fail( 'count' )
    num_fives = ise.count( 5 )
    if num_fives != 0:
        log.fail( 'count' )

    # index
    try:
        index = ise.index( 2 )
    except:
        log.fail( 'index' )
    try:
        index = ise.index( 5 )
    except:
        pass
    else:
        log.fail( 'index' )

    # __str__
    log.put( str( ise ) )

    return True


#=============================================================================
def _test_mse( log ):
    """
    Tests the MutableSequenceEmulator.
    """

    log.put( 'MutableSequenceEmulator' )

    init_tuple = ( 1, 2, 3, 4 )

    # __delitem__
    mse = MutableSequenceEmulator( init_tuple )
    del mse[ 1 ]
    if len( mse ) != ( len( init_tuple ) - 1 ):
        log.fail( '__delitem__' )
    if 2 in mse:
        log.fail( '__delitem__' )

    # __iadd__
    mse = MutableSequenceEmulator( init_tuple )
    mse += ( 5, 6, 7, 8 )
    if len( mse ) != ( 4 + len( init_tuple ) ):
        log.fail( '__iadd__' )

    # __imul__
    mse = MutableSequenceEmulator( init_tuple )
    mse *= 2
    if len( mse ) != ( 2 * len( init_tuple ) ):
        log.fail( '__imul__' )

    # __setitem__
    mse = MutableSequenceEmulator( init_tuple )
    mse[ 1 ] = 42
    if 2 in mse:
        log.fail( '__setitem__' )
    if 42 not in mse:
        log.fail( '__setitem__' )

    # append
    mse = MutableSequenceEmulator( init_tuple )
    mse.append( 5 )
    if len( mse ) != ( len( init_tuple ) + 1 ):
        log.fail( 'append' )
    if mse[ -1 ] != 5:
        log.fail( 'append' )

    # extend
    mse = MutableSequenceEmulator( init_tuple )
    mse.extend( ( 5, 6, 7, 8 ) )
    if len( mse ) != ( 4 + len( init_tuple ) ):
        log.fail( 'extend' )

    # insert
    mse = MutableSequenceEmulator( init_tuple )
    mse.insert( 1, 42 )
    if len( mse ) != ( 1 + len( init_tuple ) ):
        log.fail( 'insert' )
    if mse[ 1 ] != 42:
        log.fail( 'insert' )
    if mse[ 2 ] != 2:
        log.fail( 'insert' )

    # pop
    mse = MutableSequenceEmulator( init_tuple )
    value = mse.pop()
    if len( mse ) != ( len( init_tuple ) - 1 ):
        log.fail( 'pop' )
    if value != init_tuple[ -1 ]:
        log.fail( 'pop' )
    if value in mse:
        log.fail( 'pop' )
    value = mse.pop( 0 )
    if len( mse ) != ( len( init_tuple ) - 2 ):
        log.fail( 'pop' )
    if value != init_tuple[ 0 ]:
        log.fail( 'pop' )
    if value in mse:
        log.fail( 'pop' )

    # remove
    mse = MutableSequenceEmulator( init_tuple )
    mse.remove( 2 )
    if len( mse ) != ( len( init_tuple ) - 1 ):
        log.fail( 'remove' )
    if 2 in mse:
        log.fail( 'remove' )

    # reverse
    mse = MutableSequenceEmulator( init_tuple )
    mse.reverse()
    num_values = len( init_tuple )
    for index in range( num_values ):
        if init_tuple[ index ] != mse[ num_values - 1 - index ]:
            log.fail( 'reverse' )

    # sort
    sort_tuple = ( 17, 13, 137, 71 )
    sorted_list = list( sort_tuple )
    sorted_list.sort()
    mse = MutableSequenceEmulator( sort_tuple )
    mse.sort()
    if mse != sorted_list:
        log.fail( 'sort' )

    # sort - using custom comparison function
    def sort_cmp( x, y ):
        if x == y:
            return 0
        return y - x
    mse.sort( sort_cmp )
    sorted_list.reverse()
    if mse != sorted_list:
        log.fail( 'sort' )
    mse = MutableSequenceEmulator( sort_tuple )

    # sort - using key extraction function
    def sort_key( v ):
        return v + 1
    sorted_list.sort( key = sort_key )
    mse.sort( key = sort_key )
    if mse != sorted_list:
        log.fail( 'sort' )

    # sort - reversing comparisons
    mse = MutableSequenceEmulator( sort_tuple )
    sorted_list.reverse()
    mse.sort( reverse = True )
    if mse != sorted_list:
        log.fail( 'sort' )

    # __str__
    mse = MutableSequenceEmulator( init_tuple )
    log.put( str( mse ) )

    return True


#=============================================================================
def _test():
    """
    Executes all module test functions.

    @return True if all tests pass, false if one fails.
    """

    # imports for testing only
    import inspect

    # set up a simple logging facility to capture or print test output
    class TestError( RuntimeError ):
        pass
    class TestLogger( object ):
        def fail( self, message ):
            caller = inspect.getframeinfo( inspect.stack()[ 1 ][ 0 ] )
            output = '## FAILED {}: {} ##'.format( caller.lineno, message )
            self.put( output )
            raise TestError( output )
        def put( self, message ):
            sys.stdout.write( '{}\n'.format( message ) )
    log = TestLogger()

    # list of all module members
    members = globals().copy()
    members.update( locals() )

    # iterate through module members
    for member in members:

        # check members for test functions
        if ( member[ : 6 ] == '_test_' ) and ( callable( members[ member ] ) ):

            # execute the test
            try:
                members[ member ]( log )

            # catch any errors in the test
            except TestError:

                # return failure to the user
                return False

    # if no test fails, send a helpful message
    log.put( '!! PASSED !!' )

    # return success to the user
    return True


#=============================================================================
def main( argv ):
    """
    Script execution entry point
    @param argv List of arguments passed to the script
    @return     Shell exit code (0 = success)
    """

    # imports when using this as a script
    import argparse

    # create and configure an argument parser
    parser = argparse.ArgumentParser(
        description = 'Base Class Templates for Creating Snippets',
        add_help    = False
    )
    parser.add_argument(
        '-h',
        '--help',
        default = False,
        help    = 'Display this help message and exit.',
        action  = 'help'
    )
    parser.add_argument(
        '-v',
        '--version',
        default = False,
        help    = 'Display script version and exit.',
        action  = 'version',
        version = __version__
    )
    parser.add_argument(
        '-t',
        '--test',
        default = False,
        help    = 'Execute built-in unit tests.',
        action  = 'store_true'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # user requests built-in unit tests
    if args.test != False:
        result = _test()
        if result == False:
            return os.EX_SOFTWARE
        return os.EX_OK

    # check args.* for script execution here
    else:
        print 'Module executed as script.'
        return os.EX_USAGE

    # return success
    return os.EX_OK


#=============================================================================
if __name__ == "__main__":
    import os
    import sys
    sys.exit( main( sys.argv ) )


