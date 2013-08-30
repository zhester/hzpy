#!/usr/bin/env python
##############################################################################
#
# aptime.py
#
# Time Calculator
#
##############################################################################


import re


#=============================================================================
class aptime:
    """
    Arbitrary precision time representation.
    Specify any relative amount of time using a string.  Multiple formats can
    be detected and parsed.  aptime objects are capable of basic arithmetic.

    Acceptable human string formats:
        hhh:mm:ss.ffffff    hours, minutes, seconds, fractional seconds
        hhh:mm:ss           hours, minutes, seconds
        mm:ss.ffffff        minutes, seconds, fractional seconds
        mm:ss               minutes, seconds
        nnnn                seconds
        nnnn.ffffff         seconds, fractional seconds
    Hours and fractions of a second (f) can be specified as 1 or more digits.

    Unit suffixes can be used for long-string formats:
        d h m s ms us ns ps

    Epoch times (seconds since Unix epoch) can be used:
        nnnnnnnnnn u

    Fractional epoch times are okay, too:
        nnnnnnnnnn.fff u
    """

    #=========================================================================
    _units   = ( 'd',   'h',  'm', 's', 'ms',  'us', 'ns', 'ps'  )
    _seconds = ( 86400, 3600, 60,  1,   0.001, 1e-6, 1e-9, 1e-12 )

    #=========================================================================
    def __init__( self, user ):
        self.seconds = 0.0
        self.user    = None
        self.load( user )

    #=========================================================================
    def __cmp__( self, other ):
        return cmp( self.seconds, other.seconds )


    #=========================================================================
    #=========================================================================
    #=========================================================================
    #=========================================================================
    #=========================================================================
    #=========================================================================
    #=========================================================================
    #=========================================================================
    #=========================================================================
    #=========================================================================
    #=========================================================================
    #=========================================================================
    #=========================================================================
    #=========================================================================
    #=========================================================================
    #=========================================================================
    def load( self, user ):
        self.user = user

        # attempt to match a human-readable time string
        mo = re.match( r'(\d+):(\d\d)(:\d\d)?(\.\d+)?', self.user )
        if mo is not None:
            print '## human-readable string ##'
            return

        # set of characters may indicate long-format string with units
        mo = re.match( r'[dhmsunp]', self.user )
        if mo is not None:
            print '## string with unit characters ##'
            return

        # numeric only, assume seconds
        self.seconds = float( self.user )



def get_ms( data ):

    # try to match a human-formatted time
    rm = re.match( r'(\d+):(\d\d)(:\d\d)?(\.\d+)?', data )

    # see if time was entered as a wall-clock time
    if rm is not None:

        # default values
        h = 0
        m = 0
        s = 0
        f = 0

        # remove all unmatched group strings
        matches = rm.groups()
        matches = [ ma for ma in matches if ma is not None ]

        # h:mm:ss.fff
        if len( matches ) == 4:
            h = int( matches[ 0 ] )
            m = int( matches[ 1 ] )
            s = int( matches[ 2 ][ 1 : ] )  # slice off the :
            f = int( matches[ 3 ][ 1 : ] )  # slice off the .
            if f > 999:
                f = int( matches[ 3 ][ 1 : 4 ] )

        # h:mm:ss or m:ss.fff
        elif len( matches ) == 3:
            if matches[ 2 ][ 0 ] == '.':
                m = int( matches[ 0 ] )
                s = int( matches[ 1 ] )
                f = int( matches[ 2 ][ 1 : ] )
                if f > 999:
                    f = int( matches[ 2 ][ 1 : 4 ] )
            else:
                h = int( matches[ 0 ] )
                m = int( matches[ 1 ] )
                s = int( matches[ 2 ][ 1 : ] )  # slice off the :

        # m:ss
        elif len( matches ) == 2:
            m = int( matches[ 0 ] )
            s = int( matches[ 1 ] )

        return ( h * 3600000 ) + ( m * 60000 ) + ( s * 1000 ) + f

    # default: assume ms input
    return int( data )


def print_ms( ms ):
    # ZIH - yeah, this is messy
    h = 0
    m = 0
    s = 0
    f = 0
    if ms >= 3600000:
        h = ms / 3600000
        m = ( ms - ( h * 3600000 ) ) / 60000
        s = ( ms - ( h * 3600000 ) - ( m * 60000 ) ) / 1000
        f = ( ms - ( h * 3600000 ) - ( m * 60000 ) ) - ( s * 1000 )
    elif ms >= 60000:
        m = ms / 60000
        s = ( ms - ( m * 60000 ) ) / 1000
        f = ( ms - ( m * 60000 ) ) - ( s * 1000 )
    elif ms >= 1000:
        s = ms / 1000
        f = ms - ( s * 1000 )
    else:
        f = ms
    print '  %d ms == %d:%02d:%02d.%03d' % ( ms, h, m, s, f )



#=============================================================================
def main( argv ):
    """ Script execution entry point """

    # initialize and start the user interface
    #ui = timecalc()
    #ui.mainloop()


    if len( argv ) > 1:
        start = get_ms( argv[ 1 ] )
        if len( argv ) > 2:
            stop = get_ms( argv[ 2 ] )
            print 'Start:'
            print_ms( start )
            print 'Stop:'
            print_ms( stop )
            print 'Difference:'
            print_ms( stop - start )
        else:
            print_ms( start )


    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
