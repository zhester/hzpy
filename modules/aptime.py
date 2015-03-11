#!/usr/bin/env python
##############################################################################
#
# aptime.py
#
# Arbitrary precision time representation, computation, and parsing.
#
# ZIH - looking to refactor as a subclass of numarb
#
##############################################################################


import math
import re


#=============================================================================
class aptime( object ):
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
        d h m s ms us ns ps tP
    """


    #=========================================================================
    # Indexes used to refer to units of time and precision cut-offs.
    P_DAY         = 0
    P_HOUR        = 1
    P_MINUTE      = 2
    P_SECOND      = 3
    P_MILLISECOND = 4
    P_MICROSECOND = 5
    P_NANOSECOND  = 6
    P_PICOSECOND  = 7
    P_PLANCKTIME  = 8


    #=========================================================================
    # Numeric conversions for output.
    R_FRACT = 0
    R_ROUND = 1
    R_FLOOR = 2
    R_CEIL  = 3


    #=========================================================================
    # SI time symbols and unit values.
    _symbols = ( 'd',   'h',  'm', 's', 'ms',  'us', 'ns', 'ps',  'tP'     )
    _units   = ( 86400, 3600, 60,  1,   0.001, 1e-6, 1e-9, 1e-12, 5.39e-44 )
    _pnames  = ( 'days', 'hours', 'minutes', 'seconds', 'milliseconds',
        'microseconds', 'nanoseconds', 'picoseconds', 'tPlanck' )


    #=========================================================================
    def __init__(
        self,
        user      = '0',
        precision = P_SECOND,
        output    = R_ROUND
    ):
        """
        Initialize an aptime instance.
        @param user Initial user input string (or number)
        @param precision Maximum precision needed
        """

        self._seconds  = 0.0
        self.output    = output
        self.precision = precision
        self.user      = None
        self.load( user )


    #=========================================================================
    def __add__( self, other ):
        """
        """
        ## ZIH - if we can switch to normalized type casting (not sure),
        ##   we could avoid the isinstance() check, and just run a
        ##   float() type cast on the other object (regardless of type)

        if isinstance( other, ( int, float ) ) == True:
            return self._sdup( self._seconds + other )
        return self._sdup( self._seconds + other._seconds )


    #=========================================================================
    def __cmp__( self, other ):
        """
        Time comparison magic method.
        """

        psecs = aptime._units[ self.precision ]
        upper_limit = self._seconds + psecs
        lower_limit = self._seconds - psecs
        if other._seconds < lower_limit:
            return -1
        if other._seconds > upper_limit:
            return 1
        return 0


    #=========================================================================
    def __div__( self, other ):
        """
        """

        if isinstance( other, ( int, float ) ) == True:
            return self._sdup( self._seconds / other )
        return self._sdup( self._seconds / other._seconds )


    #=========================================================================
    def __float__( self ):
        """
        """

        return self._seconds / aptime._units[ self.precision ]


    #=========================================================================
    def __getattr__( self, name ):
        """
        """

        if name in aptime._pnames:
            return self.getn( aptime._pnames.index( name ) )
        if name in aptime._symbols:
            return self.getn( aptime._symbols.index( name ) )
        return self._seconds


    #=========================================================================
    def __int__( self ):
        """
        """

        value = self._seconds / aptime._units[ self.precision ]
        if self.output == aptime.R_FLOOR:
            return int( math.floor( value ) )
        elif self.output == aptime.R_CEIL:
            return int( math.ceil( value ) )
        return int( round( value ) )


    #=========================================================================
    def __mul__( self, other ):
        """
        """

        if isinstance( other, ( int, float ) ) == True:
            return self._sdup( self._seconds * other )
        return self._sdup( self._seconds * other._seconds )


    #=========================================================================
    def __radd__( self, other ):
        """
        """

        return self.__add__( other )


    #=========================================================================
    def __rdiv__( self, other ):
        """
        """

        if isinstance( other, ( int, float ) ) == True:
            return self._sdup( other / self._seconds )
        return self._sdup( other._seconds / self._seconds )


    #=========================================================================
    def __rmul__( self, other ):
        """
        """

        return self.__mul__( other )


    #=========================================================================
    def __rsub__( self, other ):
        """
        """

        if isinstance( other, ( int, float ) ) == True:
            return self._sdup( other - self._seconds )
        return self._sdup( other._seconds - self._seconds )


    #=========================================================================
    def __sub__( self, other ):
        """
        """

        if isinstance( other, ( int, float ) ) == True:
            return self._sdup( self._seconds - other )
        return self._sdup( self._seconds - other._seconds )


    #=========================================================================
    def getn( self, precision = None, output = None ):
        """
        """

        if precision is None:
            precision = self.precision
        if output is None:
            output = self.output

        value = self._seconds / aptime._units[ precision ]

        if output == aptime.R_ROUND:
            return int( round( value ) )
        elif output == aptime.R_FLOOR:
            return int( math.floor( value ) )
        elif output == aptime.R_CEIL:
            return int( math.ceil( value ) )
        return value


    #=========================================================================
    def load( self, user ):
        """
        Load just about any string that describes an amount of time.
        @param user The user-specified string
        """

        # store the original, specified string/value
        self.user = user

        # no need to parse numbers
        if type( self.user ) is int:
            self._seconds = float( self.user )
            return
        elif type( self.user ) is float:
            self._seconds = self.user
            return

        # attempt to match a human-readable time string
        match = re.match( r'(\d+):(\d\d)(:\d\d)?(\.\d+)?', self.user )
        if match is not None:
            if self._load_readable( match ) == True:
                return

        # set of characters may indicate long-format string with units
        chars = set( ''.join( aptime._symbols ) )
        match = re.match( r'[' + chars + ']', self.user )
        if match is not None:
            if self._load_symbols( match ) == True:
                return

        # numeric only, assume seconds
        self._seconds = float( self.user )


    #=========================================================================
    def _sdup( self, seconds ):
        """
        Duplicate object with a new time value.
        """
        return aptime( seconds, self.precision, self.output )


    #=========================================================================
    def _load_readable( self, match ):
        """
        Load time into object from a simple, human-readable time string.
        @param match The MatchObject generated by parsing
        """

        # default time values
        times = [ 0 ] * len( aptime._units )

        # remove all unmatched group strings
        matches = match.groups()
        matches = [ m for m in matches if m is not None ]

        # note: slicing below removes initial : from matching groups

        # matched hhh:mm:ss.fff
        if len( matches ) == 4:
            times[ aptime.P_HOUR ]   = int( matches[ 0 ] )
            times[ aptime.P_MINUTE ] = int( matches[ 1 ] )
            times[ aptime.P_SECOND ] = \
                float( matches[ 2 ][ 1 : ] ) + float( matches[ 3 ] )

        # matched hhh:mm:ss or mm:ss.fff
        elif len( matches ) == 3:

            # matched mm:ss.fff
            if matches[ 2 ][ 0 ] == '.':
                times[ aptime.P_MINUTE ] = int( matches[ 0 ] )
                times[ aptime.P_SECOND ] = \
                    float( matches[ 1 ] ) + float( matches[ 2 ] )

            # hhh:mm:ss
            else:
                times[ aptime.P_HOUR ]   = int( matches[ 0 ] )
                times[ aptime.P_MINUTE ] = int( matches[ 1 ] )
                times[ aptime.P_SECOND ] = int( matches[ 2 ][ 1 : ] )

        # matched mm:ss
        elif len( matches ) == 2:
            times[ aptime.P_MINUTE ] = int( matches[ 0 ] )
            times[ aptime.P_SECOND ] = int( matches[ 1 ] )

        # use the times list to set the seconds value
        self._seconds = self._times2s( times )

        # default indicates a valid time string was processed
        return True


    #=========================================================================
    def _load_symbols( self, match ):
        """
        Load time into object from a symbolic time string.
        @param match The MatchObject generated by parsing
        """

        # break into time specification tokens
        tokens = re.split( r'\s+', match.string )

        # token patterns
        s_pat = r'(' + '|'.join( aptime._symbols ) + ')'
        v_pat = r'(\d*\.?\d*)'
        s_re = re.compile( s_pat )
        t_re = re.compile( v_pat + r'\s*' + s_pat )
        v_re = re.compile( v_pat )

        # reset the number of seconds
        self._seconds = 0.0

        # last token was a numeric value string
        last_value = None

        # scan the tokens
        for t in tokens:

            # check for a symbol token
            m = re.match( s_re, t )
            if ( m is not None ) and ( last_value is not None ):
                self._seconds += self._sym2s( last_value, t )
                last_value = None
                continue

            # check for easy tokens
            m = re.match( t_re, t )
            if m is not None:
                self._seconds += self._sym2s( m.group( 0 ), m.group( 1 ) )
                continue

            # check for a value token
            m = re.match( v_re, t )
            if m is not None:
                last_value = m.group( 0 )

        # default indicates a valid time string was processed
        return True


    #=========================================================================
    def _sym2s( self, value, symbol ):
        """
        """
        sym_i = aptime._symbols.index( symbol )
        return float( value ) * aptime._units[ sym_i ]


    #=========================================================================
    def _times2s( self, times ):
        """
        """
        s = 0.0
        for i in range( len( aptime._units ) ):
            s += times[ i ] * aptime._units[ i ]
        return s



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

    off = '''
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
            print_ms( start )'''

    user = '1:23:45.6789' if len( argv ) < 2 else argv[ 1 ]

    t = aptime( user, output = aptime.R_FRACT )

    print t.seconds
    print t.hours
    print t.picoseconds

    t.output = aptime.R_ROUND

    print t.seconds
    print t.hours
    print t.picoseconds

    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
