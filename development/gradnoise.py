#!/usr/bin/env python
#=============================================================================
#
# Gradient Noise Generation
#
# TODO:
#
#   Add a more intelligent noise filter that is aware of the number of samples
#   needed between the gradient positions, and expands the filter envelope to
#   more evenly (Gaussian) distribute the noise between samples.
#
#=============================================================================

"""
Gradient Noise Generation
=========================

Low-delta gradients cause stair-step transitions (banding).  The typical
solution to hide the banding is to introduce general-purpose dithering of the
entire image space.  This is an attempt to see if a special-purpose gradient
noise function can produce good-enough results.
"""


import logging
import random
import sys


import mpng


__version__ = '0.0.0'



#=============================================================================
class Gradient( object ):
    """
    Gradient objects.
    """

    #=========================================================================
    def __init__( self, start_color = 0x000000FF, end_color = 0xFFFFFFFF ):
        """
        Initializes a Gradient object.
        """
        self.stops = []
        self.add_stop( start_color, 0.0 )
        self.add_stop( end_color, 1.0 )
        self.channel_filter = round

    #=========================================================================
    def add_stop( self, color, position ):
        """
        Add new color stop to gradient.
        """
        self.stops.append( Stop( color, position ) )
        self.stops.sort( key = lambda o : o.position )

    #=========================================================================
    def get( self, position = 0.5 ):
        """
        Retrieves a color value at a position along the gradient.

        Note: Does not currently support gradient extrapolation.
        Note: Does not currently support gradient clipping.
        """

        # don't mess around with non-float positions
        position = float( position )

        # start of gradient
        if position <= 0.0:
            return self.stops[ 0 ].color

        # end of gradient
        elif position >= 1.0:
            return self.stops[ -1 ].color

        # set last stop
        last_stop = self.stops[ 0 ]

        # scan stops in gradient
        for stop in self.stops:

            # check for the first stop past the requested position
            if stop.position > position:
                break

            # update last stop
            last_stop = stop

        # determine localized position between stops
        delta = stop.position - last_stop.position
        if delta > 0:
            position = ( position - last_stop.position ) / delta
        else:
            position = 0.0

        # compute color channel deltas
        ar = float( ( last_stop.color >> 24 ) & 0xFF )
        ag = float( ( last_stop.color >> 16 ) & 0xFF )
        ab = float( ( last_stop.color >>  8 ) & 0xFF )
        aa = float( ( last_stop.color >>  0 ) & 0xFF )
        br = float( (      stop.color >> 24 ) & 0xFF )
        bg = float( (      stop.color >> 16 ) & 0xFF )
        bb = float( (      stop.color >>  8 ) & 0xFF )
        ba = float( (      stop.color >>  0 ) & 0xFF )
        dr = br - ar
        dg = bg - ag
        db = bb - ab
        da = ba - aa

        # compute channel values at this position
        gr = ar + ( dr * position )
        gg = ag + ( dg * position )
        gb = ab + ( db * position )
        ga = aa + ( da * position )

        # filter each channel
        fr = int( self.channel_filter( gr ) )
        fg = int( self.channel_filter( gg ) )
        fb = int( self.channel_filter( gb ) )
        fa = int( self.channel_filter( ga ) )

        # test filter output for issues
        if fr > 255:
            logging.warn( 'Exceeded 8-bit channel value: R={}'.format( fr ) )
        if fg > 255:
            logging.warn( 'Exceeded 8-bit channel value: G={}'.format( fg ) )
        if fb > 255:
            logging.warn( 'Exceeded 8-bit channel value: B={}'.format( fb ) )
        if fa > 255:
            logging.warn( 'Exceeded 8-bit channel value: A={}'.format( fa ) )

        # construct the color output value
        cr = ( fr & 0xFF ) << 24
        cg = ( fg & 0xFF ) << 16
        cb = ( fb & 0xFF ) <<  8
        ca = ( fa & 0xFF ) <<  0
        color = cr | cg | cb | ca

        # return the color value
        return color


#=============================================================================
class Stop( object ):
    """
    Gradient stop objects.
    """

    #=========================================================================
    def __init__( self, color, position ):
        """
        Initializes a Stop object.
        """
        self.color    = color
        self.position = position


#=============================================================================
def simple_random_filter( value ):
    """
    Simple channel randomization filter.
    """

    # how much relative noise to introduce
    jitter = 0.2

    # window potentially clipped noise (ZIH - not sure I like this yet)
    #min_value = value - jitter
    #max_value = value + jitter
    #if min_value < 0.0:
    #    value -= min_value
    #elif max_value > 1.0:
    #    value -= 1.0 - max_value

    # make some noise centered around a central value
    noise = ( jitter * random.random() ) - ( jitter / 2.0 )

    # add the noise to the input to generate the output
    output = value + noise

    # the value should be pushed to the nearest integer
    return round( output )


#=============================================================================
def test_simple():
    """
    Tests simple gradient noise.
    """
    w = 320
    h = 1024
    start = 0x08262AFF
    stop  = 0x001620FF

    ### DEBUGGING
    dfh = open( 'dbg.csv', 'w' )

    # generate the pixel data for the simple gradient noise
    def gen_simple( w, h ):

        # create some low-delta gradients
        rg = Gradient( start, stop )
        ng = Gradient( start, stop )
        ng.channel_filter = simple_random_filter

        # create a row of pixels
        for row in range( h ):

            # list of pixel channel value in this row
            pixels = []
            if row == 0:
                position = 1.0
            elif row >= ( h - 1 ):
                position = 0.0
            else:
                position = ( h - row ) / float( h )

            ### DEBUGGING
            dbg = [ '{:03},{:1.4f}'.format( row, position ) ]

            # reference gradient
            color = rg.get( position )
            values = [
                ( ( color >> 24 ) & 0xFF ),
                ( ( color >> 16 ) & 0xFF ),
                ( ( color >>  8 ) & 0xFF )
            ]
            pixels.extend( values * ( w // 2 ) )
            dbg.append( '{:08X}'.format( color ) )

            # noise gradient
            for col in range( w // 2, w ):
                color = ng.get( position )
                values = [
                    ( ( color >> 24 ) & 0xFF ),
                    ( ( color >> 16 ) & 0xFF ),
                    ( ( color >>  8 ) & 0xFF )
                ]
                pixels.extend( values )
                if col % 32 == 0:
                    dbg.append( '{:08X}'.format( color ) )
            dfh.write( '{}\n'.format( ','.join( dbg ) ) )

            # yield a full row of pixel data
            yield pixels

    # generate the test image
    with open( 'test_simple.png', 'wb' ) as ifh:
        png_writer = mpng.Writer( w, h )
        png_writer.write( ifh, gen_simple( w, h ) )

    ### DEBUGGING
    dfh.close()


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
        description = 'Gradient Noise Generation',
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

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # run the simple test
    test_simple()

    # return success
    return 0


#=============================================================================
if __name__ == "__main__":
    sys.exit( main( sys.argv ) )

