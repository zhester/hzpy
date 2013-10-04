#*******************************************************************************
# pyplot.py
#
# Zac Hester <zac.hester@gmail.com>
# 2012-07-31
#
# Plot/analysis example using numpy and matplotlib
#
#*******************************************************************************


import  math
import  matplotlib
import  matplotlib.pyplot           as pyplot
import  numpy
import  numpy.fft                   as fft
import  numpy.random                as random


def main( argv ):
    """ script entry point """

    # Number of samples to generate.
    num_samples    = 2048

    # Generate some noise to distort the data.
    noise_strength = 0.05
    noise          = random.uniform( ( -1.0 * noise_strength ),
                                     (  1.0 * noise_strength ),
                                     num_samples )

    # Set the cycle frequencies of three sinusoids.
    cycle_a        = 16.000 * 2.0 * 3.14159 / float( num_samples - 1 )
    cycle_b        = 414.51 * 2.0 * 3.14159 / float( num_samples - 1 )
    cycle_c        = 1117.3 * 2.0 * 3.14159 / float( num_samples - 1 )

    # Set the amplitude of three sinusoids.
    amp_a          = 1.000
    amp_b          = 0.150
    amp_c          = 0.062

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

    # Compute the FFT.
    fft_data = fft.fft( data )

    # Compute magnitudes for lower-half of spectrum.
    mags = numpy.absolute( fft_data[ : ( num_samples >> 1 ) ] )

    # Convert frequency data to log scale.
    mags_db = [ 20 * numpy.log10( mag ) for mag in mags ]

    # Add some "height" space to allow both subplots to display titles.
    pyplot.subplots_adjust( hspace = 0.55 )

    # Plot the signal amplitude per sample.
    pyplot.subplot( 3, 1, 1 )
    pyplot.plot( data )
    pyplot.xlim( ( 0, num_samples ) )
    pyplot.title( 'Signal' )
    pyplot.xlabel( 'samples' )
    pyplot.ylabel( 'amplitude' )

    # Plot the frequency magnitude per bin.
    pyplot.subplot( 3, 1, 2 )
    pyplot.plot( mags )
    pyplot.xlim( ( 0, num_samples >> 1 ) )
    pyplot.title( 'Frequency' )
    pyplot.xlabel( 'bins' )
    pyplot.ylabel( 'magnitude' )

    # Plot the frequency magnitude (dB) per bin.
    pyplot.subplot( 3, 1, 3 )
    pyplot.plot( mags_db )
    pyplot.xlim( ( 0, num_samples >> 1 ) )
    pyplot.title( 'Frequency' )
    pyplot.xlabel( 'bins' )
    pyplot.ylabel( 'magnitude (dB)' )

    # Check for a user-specified image file.
    if len( argv ) > 1:
        filename = argv[ 1 ]
    else:
        filename = 'pyplot.png'

    # Save the plots to an image file.
    pyplot.savefig( filename, dpi = 90 )


if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
