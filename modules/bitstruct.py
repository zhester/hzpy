#!/usr/bin/env python
##############################################################################
#
# bitstruct.py
#
# TODO:
#   - refactor implementation into bitsruct class, and keep functions as a
#       convenience interface
#   - optimize string spec parsing
#
##############################################################################

"""
Provides a uniform system for extracting sub-byte information from binary
data.  It is similar to the struct module in that it requires a format
specifier.  The format specifier can either be a string (format below) or a
list of tuples (structure below).  Everything is returned as its unsigned
integer representation.

String Specifiers
    These work by simply repeating an alpha character for each bit in a word.
    The characters you use are up to you.  Spaces are collapsed, so you can
    use them to visually break up sections.  The bit order is always MSbit to
    LSbit.

    Example:
        aabb bbcd
        --> yields 4 fields: one is two bits at bit position 6, second is 4
            bits at position 2, third is 1 bit at position 1, fourth is 1 bit
            at position 0.  Values are returned in a list something like this:
        [ 3, 12, 0, 1 ]

List Specifiers
    These are intended to simplify specifying things from an outside source.
    It can provide more information than the string specifier, and has the
    potential to be more concise--especially if you have fewer sub-fields.
    Unlike the string specifier, not every bit has to be defined in the
    specifier.

    Example:
        [ (6,2), (2,4), (1,1), (0,1) ]
        --> yields the same fields as the string example
            Each inner tuple is: (offset,length).

    The list can be in any bit order, and sub-fields may overlap or contain
    other sub-fields.  Note: When packing data from a specifier with
    overlapped/nested sub-fields, the later fields in the list will override
    data packed by earlier fields.

    Another feature you can use with list specifiers is to add a dictionary
    field key to each bit field.  Instead of receiving a list of values, you
    will then receive a dictionary with keys indexing each value.

    Example:
        [ (6,2,'I2C'), (2,4,'SPI'), (1,1,'LED1'), (0,1,'LED0') ]
        --> returns something like this:
        { 'I2C' : 3, 'SPI' : 12, 'LED1' : 0, 'LED0' : 1 }
"""


#=============================================================================
class bitstruct:
    """
    Improved performance version of bare module functions.
    This just does all the spec parsing/checking at once instead of every time
    one of the functions are called.
    In the future, this should contain the normal implementation, and the
    module functions will just create one of these on the fly, and invoke
    the appropriate method.
    """
    def __init__( self, spec ):
        if type( spec ) is str:
            spec = _spec_str_to_list( spec )
        self.spec = spec
        self.size = calcsize( spec )
    def calcsize( self ):
        return self.size
    def pack( self, values ):
        return pack( self.spec, values )
    def unpack( self, data ):
        return unpack( self.spec, data )


#=============================================================================
def calcsize( spec ):
    """
    Return the size (in number of bits) of the format specifier.
    """
    if type( spec ) is str:
        return len( spec.replace( ' ', '' ) )
    claimed = 0
    size = 0
    for field in spec:
        mask = _get_mask( field[ 0 ], field[ 1 ] )
        new_bits = mask & ~claimed
        claimed |= mask
        size += _count_set_bits( new_bits )
    return size


#=============================================================================
def pack( spec, values ):
    """
    Pack a list or dictionary of integer values into an integer according
    to the given format specifier.
    """
    if type( spec ) is str:
        spec = _spec_str_to_list( spec )
    data = 0
    if len( spec[ 0 ] ) >= 3:
        for field in spec:
            data |= ( values[ field[ 2 ] ] & _length_to_mask( field[ 1 ] ) ) \
                << field[ 0 ]
        return data
    for i in range( len( spec ) ):
        data |= ( values[ i ] & _length_to_mask( spec[ i ][ 1 ] ) ) \
            << spec[ i ][ 0 ]
    return data


#=============================================================================
def unpack( spec, data ):
    """
    Unpack an integer into a list or dictionary of integer values according
    to the given format specifier.
    """
    if type( spec ) is str:
        spec = _spec_str_to_list( spec )
    if len( spec[ 0 ] ) >= 3:
        values = {}
        for field in spec:
            values[ field[ 2 ] ] = ( data >> field[ 0 ] ) \
                & _length_to_mask( field[ 1 ] )
        return values
    values = []
    for field in spec:
        values.append( ( data >> field[ 0 ] ) & _length_to_mask( field[ 1 ] ) )
    return values


#=============================================================================
def _count_set_bits( data ):
    count = 0
    while data != 0:
        count += data & 1
        data >>= 1
    return count


#=============================================================================
def _get_mask( offset, length ):
    return _length_to_mask( length ) << offset


#=============================================================================
def _length_to_mask( length ):
    mask = 0
    for position in range( length ):
        mask |= ( 1 << position )
    return mask


#=============================================================================
def _spec_split( spec ):
    fields = []
    field  = ''
    prev   = None
    for i in range( len( spec ) ):
        if spec[ i ] == ' ':
            continue
        if spec[ i ] != prev:
            if len( field ):
                fields.append( field )
                field = ''
            prev = spec[ i ]
        field += spec[ i ]
    if len( field ):
        fields.append( field )
    return fields


#=============================================================================
def _spec_str_to_list( spec ):
    spec   = _spec_split( spec )
    index  = len( spec )
    fields = [ None ] * index
    index -= 1
    offset = 0
    while index >= 0:
        length = len( spec[ index ] )
        fields[ index ] = ( offset, length )
        offset += length
        index -= 1
    return fields


#=============================================================================
def main( argv ):
    """ Script execution entry point """

    # internal debug stuff
    example = ' aaa a b    bbbbbc deff f  '
    #print 'Split: ', _spec_split( example )
    #print 'To List: ', _spec_str_to_list( example )

    # formats and data for testing
    tests = [
        ( example, 0xA500BEEF ),
        ( [(24,8,'MSB'),(16,8,'2SB'),(8,8,'1SB'),(0,8,'LSB')], 0x100F0E0D ),
        ( [(0,16),(1,1),(2,2),(0,4)], 0x3210 )
    ]

    # test unpacking/packing data
    for test in tests:
        size   = calcsize( test[ 0 ] )
        values = unpack( test[ 0 ], test[ 1 ] )
        data   = pack( test[ 0 ], values )
        print '== Test Case =='
        print 'Format: ', test[ 0 ]
        print 'Size:    %d' % size
        print 'Data:    0x%X' % test[ 1 ]
        print 'Unpack: ', values
        print 'Pack:    0x%X' % data
        if ( test[ 1 ] & _length_to_mask( size ) ) == data:
            print 'Re-packed data matches original: PASSED'
        else:
            print 'Re-packed data matches original: FAILED'

    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
