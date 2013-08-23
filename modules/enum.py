##############################################################################
#
#   enum.py - Enumeration System
#
##############################################################################


#=============================================================================
def enum( *sequential, **named ):
    """
    Sequential Enumeration
    @param *sequential 
    @param **named 
    @return Enumerator type object
    """
    enums = dict( zip( sequential, range( len( sequential ) ) ), **named )
    return type( 'Enum', (), enums )


#=============================================================================
def enuma( **enums ):
    """
    Assigned Enumeration
    @param **enums Named parameter argument list (e.g. seven = 7, eight = 8)
    @return Enumerator type object
    """
    return type( 'Enum', (), enums )


#=============================================================================
def main( argv ):
    """ Test script execution entry point """

    e0 = enum( 'zero', 'one', 'two', 'three' )

    print 'Sequential Enumeration'
    print '   zero: %d == %d' % ( e0.zero,  0 )
    print '    one: %d == %d' % ( e0.one,   1 )
    print '    two: %d == %d' % ( e0.two,   2 )
    print '  three: %d == %d' % ( e0.three, 3 )

    e1 = enuma( four = 4, five = 5, six = 6, seven = 7  )

    print 'Assigned Enumeration'
    print '   four: %d == %d' % ( e1.four,  4 )
    print '   five: %d == %d' % ( e1.five,  5 )
    print '    six: %d == %d' % ( e1.six,   6 )
    print '  seven: %d == %d' % ( e1.seven, 7 )


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
