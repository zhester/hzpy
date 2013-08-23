#*******************************************************************************
# plot.py
#
# Zac Hester <zac.hester@gmail.com>
# 2012-07-27
#
# Minimal plotting reference using numpy + matplotlib
#
#*******************************************************************************


import  matplotlib
import  matplotlib.pyplot           as pyplot


class Plot( object ):
    """ handles basic data plotting """

    property_list = [ 'title', 'xlabel', 'ylabel' ]


    def __init__( self, num_samples = None ):
        """ initialize a Plot instance """

        self.N          = None
        self.marker     = None

        self.setN( num_samples )


    def qp1( self, y, x = None, f = None, **kwargs ):
        """ quick plot a single data series """

        size = len( y )

        if x is None:
            x = range( size )

        if size > 256:
            marker = None
        else:
            marker = 'o'

        pyplot.plot( x, y, marker = marker )

        for arg in self.property_list:
            if arg in kwargs:
                getattr( pyplot, arg )( kwargs[ arg ] )

        if f is not None:
            pyplot.savefig( f )
            print 'Plot saved to %s' % f
        else:
            pyplot.show()


    def addSeries( self, y ):
        """ add a series to the plot session """

        self.setN( len( y ) )

        pyplot.plot( range( self.N ), y, marker = self.marker )


    def renderPlot( self, filename = None ):
        """ render the plot in its current state """

        if filename is not None:
            pyplot.savefig( filename )
        else:
            pyplot.show()


    def setN( self, num_samples ):
        """ set the number of samples for the plot """

        if self.N == None or num_samples != self.N:
            self.N = num_samples
            if self.N > 256:
                self.marker = None
            else:
                self.marker = 'o'


    def setProperty( self, key, value ):
        """ set a property of the plot """

        if key in self.property_list:
            getattr( pyplot, key )( value )



def main( argv ):
    """ example of how to use the Plot class """
    import  math
    import  numpy
    import  numpy.fft                   as fft
    import  numpy.random                as random

    # Number of samples to generate.
    num_samples    = 2048

    # Generate some noise to distort the data.
    noise_strength = 0.2
    noise          = random.uniform( ( -1.0 * noise_strength ),
                                     (  1.0 * noise_strength ),
                                     num_samples )

    # Set the cycle frequencies of three sinusoids.
    cycle_a        = 8.00 * 2.0 * 3.14159 / float( num_samples - 1 )
    cycle_b        = 2.51 * 2.0 * 3.14159 / float( num_samples - 1 )
    cycle_c        = 17.3 * 2.0 * 3.14159 / float( num_samples - 1 )

    # Set the amplitude of three sinusoids.
    amp_a          = 1.000
    amp_b          = 0.250
    amp_c          = 0.125

    # Determine the maximum envelope of the combined signals.
    max_amp        = amp_a + amp_b + amp_c + noise_strength

    # Create a buffer for the generated data.
    data           = []

    # Synthesize some natural-looking oscillating samples.
    for i in range( num_samples ):

        # Compute a magnitude for the current sample.
        sample = ( amp_a * math.sin( float( i ) * cycle_a ) ) \
               + ( amp_b * math.sin( float( i ) * cycle_b ) ) \
               + ( amp_c * math.sin( float( i ) * cycle_c ) ) \
               + noise[ i ]

        # Normalize the magnitude to unitize the sample set.
        sample /= max_amp

        # Add the sample to the buffer.
        data.append( sample )

    # Compute the FFT magnitudes.
    mags = numpy.absolute( fft.fft( data ) )

    # Convert frequency data to log scale.
    mags = [ 20 * numpy.log10( mag ) for mag in mags ]

    # Normalize.
    max_mag = numpy.max( mags )
    mags = [ mag / max_mag for mag in mags ]

    # Create a plot object.
    p = Plot( num_samples )

    # Example of a well-documented plot.
    if len( argv ) > 2:
        """
        p.qp1( y      = data,
               x      = range( num_samples ),
               f      = argv[ 1 ],
               title  = argv[ 2 ],
               xlabel = 'Samples',
               ylabel = 'Amplitude' )
        """
        p.addSeries( data )
        p.addSeries( mags )
        p.setProperty( 'title', argv[ 2 ] )
        p.setProperty( 'xlabel', 'Samples & Bins' )
        p.setProperty( 'ylabel', 'Amplitude & Magnitude' )
        p.renderPlot( argv[ 1 ] )

    # Plot to a PNG.
    elif len( argv ) > 1:
        p.qp1( data, None, argv[ 1 ] )

    # Plot to the pyplot interactive viewer.
    else:
        p.qp1( data )

    # Done.
    return 0


if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
