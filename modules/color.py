#!/usr/bin/env python


"""
Color Data Management
"""


import collections


__version__ = '0.0.0'


#=============================================================================
class _color_prop_proxy( object ):
    """
    Proxies properties for triggering updates to the host object.
    """

    #=========================================================================
    def __init__( self, name, doc = '' ):
        """
        Initializes a _color_prop_proxy object.

        @param name The name of the object's property
        @param doc  The property's docstring
        """
        self._name   = name
        self.__doc__ = doc


    #=========================================================================
    def __delete__( self, obj ):
        """
        Does not delete the described property from the object.

        @param obj The property's owner instance
        """
        raise NotImplementedError( 'Unable to delete property.' )


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
        setattr( obj, self._name, value )
        if self._name == '_value':
            obj._update_channels()
        else:
            obj._update_value()


#=============================================================================
class color( object ):
    """
    Local color management object.
    """

    #=========================================================================

    # arithmetic functions that can be passed between methods
    op_add = lambda x, y : x + y
    op_div = lambda x, y : int( round( x / float( y ) ) )
    op_mul = lambda x, y : int( round( x * float( y ) ) )
    op_sub = lambda x, y : x - y

    # channel property descriptors
    r = _color_prop_proxy( '_r', 'red channel' )
    g = _color_prop_proxy( '_g', 'green channel' )
    b = _color_prop_proxy( '_b', 'blue channel' )

    # numeric value property descriptor
    value = _color_prop_proxy( '_value', 'numeric value' )


    #=========================================================================
    def __init__( self, value, green = None, blue = None ):
        """
        Initializes a color object.

        @param value The numeric color value (24-bit RGB), or the red channel
                     value (8-bit R) if the green and blue values are given
        @param green Optional green channel value (8-bit G)
        @param blue  Optional blue channel value (8-bit B)
        """

        # detect RGB arguments
        if ( green is not None ) and ( blue is not None ):
            self._r = value
            self._g = green
            self._b = blue
            self._update_value()

        # assume integer argument
        else:
            self._value = value
            self._update_channels()


    #=========================================================================
    def __add__( self, other ):
        """
        Addition

        @param other The other color value or object to add
        @return      A color object that is the result of per-channel addition
        """
        return self._create_from_op( self.op_add, other )


    #=========================================================================
    def __div__( self, other ):
        """
        Division

        @param other The other color value or object to divide by
        @return      A color object that is the result of per-channel division
        """
        return self._create_from_op( self.op_div, other )


    #=========================================================================
    def __int__( self ):
        """
        Handles integer conversion.

        @return The integer representation of this color
        """
        return self._value


    #=========================================================================
    def __mul__( self, other ):
        """
        Multiplication

        @param other The other color value or object to divide by
        @return      A color object that is the result of per-channel division
        """
        return self._create_from_op( self.op_mul, other )


    #=========================================================================
    def __radd__( self, other ):
        """
        Reflected Addition

        @param other The other color value or object to add to
        @return      A color object that is the result of per-channel addition
        """
        return self._create_from_op( self.op_add, other, reverse = True )


    #=========================================================================
    def __rdiv__( self, other ):
        """
        Reflected Division

        @param other The other color value or object to divide into
        @return      A color object that is the result of per-channel division
        """
        return self._create_from_op( self.op_div, other, reverse = True )


    #=========================================================================
    def __rmul__( self, other ):
        """
        Reflected Multiplication

        @param other The other color value or object to multiply by
        @return      A color object that is the result of per-channel
                     multiplication
        """
        return self._create_from_op( self.op_mul, other, reverse = True )


    #=========================================================================
    def __rsub__( self, other ):
        """
        Reflected Subtraction

        @param other The other color value to subtract from
        @return      A color object that is the result of per-channel
                     subtraction
        """
        return self._create_from_op( self.op_sub, other, reverse = True )


    #=========================================================================
    def __str__( self ):
        """
        Represents the color as a string.

        @return A string representing the color as a hexadecimal literal
        """
        return '0x{:06X}'.format( self._value )


    #=========================================================================
    def __sub__( self, other ):
        """
        Subtraction

        @param other The other color value from which to subtract
        @return      A color object that is the result of per-channel
                     subtraction
        """
        return self._create_from_op( self.op_sub, other )


    #=========================================================================
    def _byte_op( self, op, left, right ):
        """
        Implements single-byte math for clipping.

        @param op    An operator function
        @param left  The left-hand-side argument (byte)
        @param right The left-hand-side argument (byte)
        @return      The result of the operation with possible clipping
        """
        value = op( left, right )
        if value > 0xFF:
            return 0xFF
        elif value < 0:
            return 0x00
        return value


    #=========================================================================
    def _create_from_op( self, op, other, reverse = False ):
        """
        Creates a new color object using an operator.

        @param op      An operator function
        @param other   The external color value or object
        @param reverse Set to reverse argument order in operator
        @return        A new color object that is the result of the operation
        """

        # integer from operator
        if type( other ) is int:
            target = color( other )

        # unknown something from operator
        elif isinstance( other, color ) == False:
            raise ValueError( 'Unsupported type for color operation.' )

        # color object from operator
        else:
            target = color( other.value )

        # check for reversed arguments
        if reverse == True:
            target._r = self._byte_op( op, other._r, self._r )
            target._g = self._byte_op( op, other._g, self._g )
            target._b = self._byte_op( op, other._b, self._b )

        # arguments are in normal order
        else:
            target._r = self._byte_op( op, self._r, other._r )
            target._g = self._byte_op( op, self._g, other._g )
            target._b = self._byte_op( op, self._b, other._b )

        # not using descriptors (in here), update value
        target._update_value()

        # return the new color object
        return target


    #=========================================================================
    def _update_channels( self ):
        """
        Updates the channel values from the internal numeric value.
        """
        self._r = ( self._value >> 16 ) & 0xFF
        self._g = ( self._value >>  8 ) & 0xFF
        self._b = ( self._value >>  0 ) & 0xFF


    #=========================================================================
    def _update_value( self ):
        """
        Updates the numeric value from the internal channel values.
        """
        self._value = ( ( self._r & 0xFF ) << 16 ) \
                    | ( ( self._g & 0xFF ) <<  8 ) \
                    | ( ( self._b & 0xFF ) <<  0 )


#=============================================================================
class gradient( object ):
    """
    Provides a common interface to generating colors for gradients.
    """

    #=========================================================================

    # structure to manage non-color multi-channel information
    channel = collections.namedtuple( 'channel', 'r g b' )


    #=========================================================================
    def __init__( self, divisions = 256, start = None, stop = None ):
        """
        Initializes a gradient object.

        @param divisions The number of divisions this gradient should cover
        @param start     The start color
        @param stop      The stop color
        """

        # initialize object state
        self.divisions = divisions
        self.start     = start if start is not None else color( 0x000000 )
        self.stop      = stop  if stop  is not None else color( 0xFFFFFF )

        # compute total channel delta values
        self.deltas = self.channel(
            ( stop.r - start.r ),
            ( stop.g - start.g ),
            ( stop.b - start.b )
        )

        # compute per-channel step increments
        self.steps = self.channel(
            self.deltas.r / float( divisions ),
            self.deltas.g / float( divisions ),
            self.deltas.b / float( divisions )
        )

        # property to track iteration
        self._position = -1


    #=========================================================================
    def __getitem__( self, position ):
        """
        Retrieves a color for any position in the gradient.

        @param position The position in the gradient.  If given an integer,
                        the color represents the value at an exact division.
                        If given a float, the position is treated as a
                        percentage (0.0 to 1.0) between the start and stop
                        colors.
        @return         The color at the requested position
        @throws         IndexError if the position is invalid
        """

        # percentage positions
        if type( position ) is float:

            # the color that will be reported
            report = color( self.start.value )

            # calculate the absolute channel value
            report.r += int( round( self.deltas.r * position ) )
            report.g += int( round( self.deltas.g * position ) )
            report.b += int( round( self.deltas.b * position ) )

            # return the reported color
            return report

        # integer step positions
        elif type( position ) is int:

            # check index
            if ( position < 0 ) or ( position >= self.divisions ):
                raise IndexError(
                    'Invalid index into gradient: {}'.format( position )
                )

            # the color that will be reported
            report = color( self.start.value )

            # calculate the absolute channel value
            report.r += int( round( self.steps.r * position ) )
            report.g += int( round( self.steps.g * position ) )
            report.b += int( round( self.steps.b * position ) )

            # return the reported color
            return report

        # unsupported position
        raise IndexError( 'Unsupported index type into gradient.' )


    #=========================================================================
    def __iter__( self ):
        """
        Supports iteration.

        @return The iterable object for the gradient
        """
        self._position = 0
        return self


    #=========================================================================
    def __len__( self ):
        """
        Length of gradient (number of divisions).

        @return The length of the gradient (number of divisions)
        """
        return self.divisions


    #=========================================================================
    def __str__( self ):
        """
        Represent the gradient as a string.

        @return A string representation of the gradient
        """
        return '[{},{},{}]'.format( self.divisions, self.start, self.stop )


    #=========================================================================
    def next( self ):
        """
        Retrieves the next color in the gradient.

        @return The next color needed to produce the gradient.
        """

        # bounds check
        if self._position >= self.divisions:
            raise StopIteration()

        # create the color at the current position in the gradient
        current = self.__getitem__( self._position )

        # increment to next position
        self._position += 1

        # return the current color
        return current


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
        description = 'Color Data Management',
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

