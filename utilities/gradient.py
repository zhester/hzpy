#!/usr/bin/env python


"""
Generates Gradient PNGs
=======================

Dependencies
------------

Relies on the PyPNG library for writing PNG files:

    https://github.com/drj11/pypng

If the PyPNG library is not found via the usual methods, this script will
attempt to automatically download the all-in-one module.
"""


import csv
import os
import re
import sys
import urllib2

sys.path.append( '.' )

# Magical PyPNG import
try:
    import png
except ImportError as ie:
    try:
        module = urllib2.urlopen(
            'https://raw.github.com/drj11/pypng/master/code/png.py'
        )
    except URLError as ue:
        print 'Failed to download PyPNG: ' + ue.reason
        sys.exit( os.EX_UNAVAILABLE )
    else:
        with open( 'png.py', 'w' ) as pfh:
            pfh.write( module.read() )
        import png


__version__ = '0.0.0'


#=============================================================================

# default values for things that are not specified
defaults = [ 'a.png', 0x000000, 0xFFFFFF, 1920, 1080 ]

# input limits
limits = { 'width' : 3840, 'height' : 2160 }


#=============================================================================
def batch( filename ):
    """
    Generates multiple gradient images from a CSV batch file.

    The batch file should have, at least, one column uniquely naming the
    gradient.  Each row should contain the positional arguments to the
    `vertgrad()` function: name, start, stop, width, height.

    @param filename The name of the batch file
    """

    # open the batch file
    with open( filename, 'r' ) as bfh:

        # read it as CSV
        reader = csv.reader( bfh )

        # toss the headings row
        headings = reader.next()

        # column converters
        conv = [ None, get_color, get_color, int, int ]

        # iterate through each gradient row
        for row in reader:

            # make sure the first column looks like a PNG file name
            if row[ 0 ][ : -4 ] != '.png':
                row[ 0 ] = row[ 0 ] + '.png'

            # convert strings to integers
            for i in range( 1, 5 ):
                if len( row ) > i:
                    if len( row[ i ] ) == 0:
                        row[ i ] = defaults[ i ]
                    else:
                        row[ i ] = conv[ i ]( row[ i ] )

            # human-friendly output
            print 'Generating {}.'.format( row[ 0 ] )

            # call the gradient-making-function-thing
            vertgrad( *row )


#=============================================================================
def get_color( string ):
    """
    Parses color strings into numbers.

    @param string A string representing a 24-bit RGB color:
                    Hex literal: 0x123456
                    CSS-style:   #123456
                    CSS-abbr:    #A5B or 0xA5B
                    Octet:       #a5  or 0xa5
                    Octet-abbr:  #a   or 0xa
                    RGB decimal: rgb(127,0,255)
    @return       The integer value
    """

    # look for hex strings as either #123456 or 0x123456
    match = re.match( r'^(?:#|0(?:x|X))([0-9a-fA-F]+)', string )
    if match is not None:

        # strip off the '#' or '0x' prefix
        string = match.group( 1 )

    # this doesn't have a hex prefix, check for 'rgb( r, g, b )' string
    else:
        octet = r'\s*(\d{1,3})\s*'
        pattern = r'rgb\(' + ','.join( [ octet ] * 3 ) + r'\)'
        match = re.match( pattern, string )
        if match is not None:
            c = [ int( o ) for o in match.groups()[ 1 : ] ]
            return ( c[ 0 ] << 16 ) | ( c[ 1 ] << 8 ) | c[ 2 ]

    # assume string is hex digits
    length = len( string )

    # expand a single hex digit to six of the same
    #   'a' => 'aaaaaa'
    if length == 1:
        string = string * 6

    # expand two hex digits to three octets of the same
    #   'a5' => 'a5a5a5'
    elif length == 2:
        string = string * 3

    # expand three hex digits to three octets, each repeating one digit
    #   'a5b' => 'aa55bb'
    elif length == 3:
        string = ''.join( c * 2 for c in string )

    # convert hex string to native integer
    return int( string, 16 )


#=============================================================================
def vertgrad(
    filename = defaults[ 0 ],
    start    = defaults[ 1 ],
    stop     = defaults[ 2 ],
    width    = defaults[ 3 ],
    height   = defaults[ 4 ]
):
    """
    Generate a gradient, and store it in a PNG image file.

    @param filename Output file name
    @param start    Start color (24-bit RGB)
    @param stop     Stop color (24-bit RGB)
    @param width    Image width (pixels)
    @param height   Image height (pixels)
    """

    # write to the requested file name
    with open( filename, 'wb' ) as image_file:

        # create the PNG writer object
        png_writer = png.Writer( width, height )

        # use the gradient generator directly
        png_writer.write(
            image_file,
            _vert_grad_gen( width, height, start, stop )
        )

    # diagnostic logging
    if False:
        with open( ( filename[ : -4 ] + '.log' ), 'w' ) as log_file:
            row_num = 0
            for row in _vert_grad_gen( 1, height, start, stop ):
                digits = [ '{:02X}'.format( c ) for c in row ]
                digits.insert( 0, row_num )
                log_file.write( '{:04}: {} {} {}\n'.format( *digits ) )
                row_num += 1


#=============================================================================
def _vert_grad_gen( columns, rows, start, stop ):
    """
    Generate vertical gradient pixel data for a PNG.

    @param columns Number of columns per row to generate
    @param rows    Numebr of rows to generate
    @param start   Start color (top) of gradient
    @param stop    Stop color (bottom) of gradient
    """

    # check usage
    if ( rows <= 0 ) or ( columns <= 0 ):
        raise RuntimeError( 'Invalid number of rows or columns.' )

    # pre-calculate per-channel step increments
    red_start   = ( start >> 16 ) & 0xFF
    red_stop    = ( stop  >> 16 ) & 0xFF
    red_step    = ( red_stop - red_start ) / float( rows )
    green_start = ( start >>  8 ) & 0xFF
    green_stop  = ( stop  >>  8 ) & 0xFF
    green_step  = ( green_stop - green_start ) / float( rows )
    blue_start  = ( start >>  0 ) & 0xFF
    blue_stop   = ( stop  >>  0 ) & 0xFF
    blue_step   = ( blue_stop - blue_start ) / float( rows )

    # generate the requested number of rows
    for row in range( rows ):

        # ensure float math
        row = float( row )

        # get channel values for this row
        red   = red_start   + int( round( red_step   * row ) )
        green = green_start + int( round( green_step * row ) )
        blue  = blue_start  + int( round( blue_step  * row ) )

        # yield a row of pixels (one byte per channel)
        yield [ red, green, blue ] * columns


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
        description = 'Generates Gradient PNGs',
        add_help    = False
    )
    parser.add_argument(
        '-b',
        '--batch',
        default = False,
        help    = 'Batch-generate multiple images from CSV file.'
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
        'filename',
        nargs   = '?',
        default = defaults[ 0 ],
        help    = 'PNG image file name'
    )

    class color_arg_action( argparse.Action ):
        def __call__( self, parser, namespace, value, option_string = None ):
            setattr( namespace, self.dest, get_color( value ) )

    parser.add_argument(
        'start',
        nargs   = '?',
        default = '0x{:06X}'.format( defaults[ 1 ] ),
        help    = 'Starting color value (24-bit RGB hex string)',
        action  = color_arg_action
    )
    parser.add_argument(
        'stop',
        nargs   = '?',
        default = '0x{:06X}'.format( defaults[ 2 ] ),
        help    = 'Stoping color value (24-bit RGB hex string)',
        action  = color_arg_action
    )

    class length_arg_action( argparse.Action ):
        def __call__( self, parser, namespace, value, option_string = None ):
            if ( option_string in limits ) \
                and ( value > limits[ option_string ] ):
                value = limits[ option_string ]
            setattr( namespace, self.dest, value )

    parser.add_argument(
        'width',
        nargs   = '?',
        default = defaults[ 3 ],
        help    = 'Width of output image (pixels)',
        action  = length_arg_action
    )
    parser.add_argument(
        'height',
        nargs   = '?',
        default = defaults[ 4 ],
        help    = 'Height of output image (pixels)',
        action  = length_arg_action
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # check for batch request
    if args.batch:
        batch( args.batch )

    # generate a vertical gradient
    else:
        vertgrad(
            args.filename,
            args.start,
            args.stop,
            args.width,
            args.height
        )

    # return success
    return os.EX_OK


#=============================================================================
if __name__ == "__main__":
    sys.exit( main( sys.argv ) )

