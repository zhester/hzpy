#!/usr/bin/env python
##############################################################################
#
# bitbang.py
#
##############################################################################


import struct


#=============================================================================
class bitbang:
    """
    Provides a mechanism for bit-bang decoding of RS-232 data.
    This implementation assumes 1 start bit, 8 data bits, no parity bit, and
    1 stop bit.  This also assumes front-end level shifting has normalized
    sample levels such that a sampled "0" corresponds to a "0" symbol.
    Sequence framing is outside of the scope of this decoder.
    """

    #=========================================================================
    def __init__( self, bitrate, samplerate ):
        """
        Initialize bitbang object.
        @param bitrate The RS-232 bit rate (Hz) (e.g. 9600, 115200, etc)
        @param samplerate The rate at which the serial line was sampled (Hz)
        """

        # set samples per bit timing value
        self.sperb = float( samplerate ) / float( bitrate )

        # initialize object state
        self.reset()

    #=========================================================================
    def get_data( self, get_list = False ):
        """
        Retrieve all sampled bytes since last reset.
        @param get_list Return a list of integers instead of a binary string
        @return Binary string (or list) of sampled data
        """
        if get_list == True:
            return self.data
        return struct.pack( ( '<%dB' % len( self.data ) ), *self.data )

    #=========================================================================
    def put_sample( self, sample ):
        """
        Add an input level sample to the serial stream.
        @param sample The sampled input level (0 or 1)
        """

        # detect front edge of start bit
        if ( self.idle == True ) and ( sample == 0 ):

            # start the sample timer ahead half a bit width so when it expires
            # the timer will be in the middle of the first data bit
            self.timer = 0.5 * self.sperb
            self.idle  = False

        # check for non-idle sample time
        elif self.idle == False:

            # check for an expired sample timer
            if self.timer > self.sperb:

                # reset sample timer
                self.timer = 0.0

                # see if we've already clocked in enough bits
                if self.bits == 8:

                    # store the captured byte
                    self.data.append( self.byte )

                    # reset internal state
                    self._reset()

                # all other sample times are during data bits
                else:
                    self.byte |= sample << self.bits
                    self.bits += 1

            # sample timer still counting up
            else:
                self.timer += 1.0

    #=========================================================================
    def reset( self ):
        """
        Reset object to begin a fresh acquisition.
        """
        self._reset()
        self.data = []

    #=========================================================================
    def _reset( self ):
        self.bits  = 0
        self.byte  = 0
        self.idle  = True
        self.timer = 0.0


#=============================================================================
class bitbang_test:
    def __init__( self, bb ):
        self.bb   = bb
        self.time = 0
    def put_bit( self, level ):
        bit_time = self.time
        while ( self.time - bit_time ) < self.bb.sperb:
            self.bb.put_sample( level )
            self.time += 1


#=============================================================================
def main( argv ):
    """ Script execution entry point """

    # initialize a bit bang decoder
    bb = bitbang( 115200, 2000000 )

    # set up a test simulating sampling at 2 MHz
    test = bitbang_test( bb )
    test_byte = 0xA9

    # start bit
    test.put_bit( 0 )

    # shift in data bits
    for i in range( 8 ):
        test.put_bit( ( test_byte >> i ) & 1 )

    # stop bit
    test.put_bit( 1 )

    # retrieve the data as it was sampled
    data = bb.get_data()

    # test successful decoding
    byte = struct.unpack( '<B', data )[ 0 ]
    if byte == test_byte:
        print 'Decoded test byte successfully.'
    else:
        print 'Failed to decode data: 0x%02X != 0x%02X.' % ( byte, test_byte )

    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
