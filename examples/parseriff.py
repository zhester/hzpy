#!/usr/bin/env python

"""
Example RIFF (WAV contents) Data Parser

Sample data is written to a CSV file for analysis.
If matplotlib and numpy are available, signal plots (DFTs) are generated.
"""


import math
import os
import struct
import wave

try:
    import matplotlib.pyplot as plot
    import numpy
    import numpy.fft as fft
except ImportError:
    numeric_packages = False
else:
    numeric_packages = True


#=============================================================================
def frame2mag( frame ):
    ( i, q ) = struct.unpack( '<BB', frame )
    return math.sqrt( ( i ** 2 ) + ( q ** 2 ) )


#=============================================================================
def main( argv ):
    """ Script execution entry point """

    # check usage
    if len( argv ) < 2:
        print 'You must specify at least an input file.'
        return 0

    # start and length
    start = 0
    length = 1024
    if len( argv ) > 2:
        start = int( argv[ 2 ] )
    if len( argv ) > 3:
        length = int( argv[ 3 ] )

    # open file using wave module
    wfile = wave.open( argv[ 1 ], 'rb' )

    # print file info
    print 'Channels: %d\nSample width: %d\nFrame rate: %d\nFrames: %d' % (
        wfile.getnchannels(),
        wfile.getsampwidth(),
        wfile.getframerate(),
        wfile.getnframes()
    )

    # check for starting offset
    if start > 0:
        junk = wfile.readframes( start )

    # read frames
    frames = wfile.readframes( length )
    samples = []
    for i in range( length ):
        index = i * 2
        samples.append( frame2mag( frames[ index : ( index + 2 ) ] ) )

    # close wave file
    wfile.close()

    # plot
    if numeric_packages == True:
        fft_data = fft.fft( samples[ : 1024 ] )
        mags = numpy.absolute( fft_data )
        mags_db = [ 20 * numpy.log10( mag ) for mag in mags ]
        plot.figure( 1 )
        plot.plot( samples )
        plot.figure( 2 )
        plot.plot( mags_db )
        plot.show()

    # output
    oname = argv[ 1 ].replace( '.wav', '.csv' )
    ofile = open( oname, 'wb' )
    for sample in samples:
        ofile.write( '%d\n' % sample )
    ofile.close()

    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )

