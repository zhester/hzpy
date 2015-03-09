#!/usr/bin/env python


"""
Development on Sample/Image Dithering
"""


import os
import random
import sys
import urllib2

# Magical PyPNG import
sys.path.append( '.' )
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

# hzpy libraries
sys.path.append( '../modules' )
import color


__version__ = '0.0.0'


#=============================================================================
def generate_samples():
    """
    Generates the sample images for review.
    """

    # set image dimensions
    width  = 512
    height = 1024

    # set the base gradient start and stop colors
    start = color.color( 0x001620 )
    stop  = color.color( 0x08262A )

    # create the base gradient with noticeable "banding"
    make_image(
        'base.png',
        width,
        height,
        make_base( start, stop, width, height )
    )

    # create a gradient with some noise applied to it
    make_image(
        'noise.png',
        width,
        height,
        make_dith_noise( start, stop, width, height )
    )


#=============================================================================
def make_image( filename, width, height, generator ):
    """
    Makes a PNG image.
    """

    # write to the requested file name
    with open( filename, 'wb' ) as image_file:

        # create the PNG writer object
        png_writer = png.Writer( width, height )

        # use the requested pixel data generator
        png_writer.write( image_file, generator() )


#=============================================================================
def make_base( start, stop, cols, rows ):
    """
    Creates a row generator for a base gradient without dithering.
    """
    grad = color.gradient( rows, start, stop )
    def closure( cols = cols, grad = grad ):
        for row in grad:
            yield [ row.r, row.g, row.b ] * cols
    return closure


#=============================================================================
def make_dith_noise( start, stop, cols, rows ):
    """
    Creates a row generator for simple noise dithering.
    """
    grad = color.gradient( rows, start, stop )
    def closure( cols = cols, grad = grad ):
        jmin = -2
        jmax = 2
        for row in grad:
            this_row = [ row.r, row.g, row.b ] * cols
            for p in range( cols ):
                p_offset = p * 3
                for c_index in range( 3 ):
                    index = p_offset + c_index
                    jitter = random.randint( jmin, jmax )
                    this_row[ index ] += jitter
                    if this_row[ index ] < 0:
                        this_row[ index ] = 0
                    elif this_row[ index ] > 255:
                        this_row[ index ] = 255
            yield this_row
    return closure


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
        description = 'Development on Sample/Image Dithering',
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

    # check args.* for script execution here
    #print 'Template code executed.  Replace with real code.'
    generate_samples()

    # return success
    return os.EX_OK


#=============================================================================
if __name__ == "__main__":
    sys.exit( main( sys.argv ) )

