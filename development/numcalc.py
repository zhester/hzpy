#!/usr/bin/env python
##############################################################################
#
# numcalc.py
#
# Numeric Format Calculator
#
##############################################################################


import os
import re
import struct
import Tkinter as tk
import ttk


#=============================================================================
class timecalc( ttk.Frame ):

    # application info
    _author  = 'Zac Hester <zac.hester@gmail.com>'
    _date    = '2013-08-27'
    _icon    = 'numcalc.ico'
    _title   = 'Numeric Format Calculator'
    _version = '0.0.0'

    # layout configs
    _gridcfg_label = {
        'padx'   : 4,
        'pady'   : 4,
        'sticky' : ( tk.E + tk.W )
    }
    _gridcfg_stick = {
        'sticky' : ( tk.N + tk.S + tk.E + tk.W )
    }
    _gridcfg_wpad = {
        'padx'   : 8,
        'pady'   : 8
    }


    #=========================================================================
    def __init__( self, parent = None ):
        """ Initializes frame instance """

        # call the parent constructor
        ttk.Frame.__init__( self, parent )

        # create a place to keep widget state
        self.wvars = {}

        # set the application-wide default icon
        if os.path.exists( timecalc._icon ):
            self.master.call(
                'wm',
                'iconbitmap',
                self.master._w,
                '-default',
                timecalc._icon
            )

        # set the application title
        self.master.title( timecalc._title )

        # this sets up the root frame to resize things
        #   any descendent widgets will also need to use _gridcfg_stick
        self.grid( **timecalc._gridcfg_stick )
        top = self.winfo_toplevel()
        top.rowconfigure( 0, weight = 1 )
        top.columnconfigure( 0, weight = 1 )
        self.rowconfigure( 0, weight = 1 )
        self.columnconfigure( 0, weight = 1 )

        # initialize the GUI's widgets
        self._create_widgets()


    #=========================================================================
    def _create_widgets( self ):
        """ Builds the root frame's interface """

        # ZIH - left off here
        pass



class number( object ):

    FMT_CHAR     = 0
    FMT_SHORT    = 1
    FMT_LONG     = 2
    FMT_LONGLONG = 3
    FMT_FLOAT    = 4
    FMT_DOUBLE   = 5

    _pstrs_s = ( 'b', 'h', 'l', 'q', 'f', 'd' )
    _pstrs_u = ( 'B', 'H', 'L', 'Q', 'f', 'd' )

    _limits_u = (
        ( 2 **  8 ) - 1,
        ( 2 ** 16 ) - 1,
        ( 2 ** 32 ) - 1,
        ( 2 ** 64 ) - 1
    )

    fmt_display = (
        'char', 'short', 'long', 'long long', 'float', 'double'
    )

    def __init__( self, data = None ):
        self.idata  = None
        self.interp = ''
        self.itype  = None
        self.nbytes = 0
        self.p_fmt  = number.FMT_CHAR
        self.packed = ''
        self.signed = False
        self.value  = 0
        self.set_value( data )

    def __nonzero__( self ):
        return 0 if self.value == 0 else 1

    def __int__( self ):
        return self.value

    def __float__( self ):
        if self.nbytes != 4:
            return float( self.value )
        return struct.unpack( '<f', self.packed )[ 0 ]

    def __hex__( self ):
        return hex( self.value )

    def __index__( self ):
        return self.value

    def __oct__( self ):
        return oct( self.value )

    def __sizeof__( self ):
        return self.nbytes

    def __str__( self ):
        return self.packed

    def format( self, format = None, precision = 2 ):
        """
        todo:
            return these types of formats automatically:
                0x01234567 (zero-padded, hex)
                003 (zero-padded, oct)
                0001 1010 0010 1100 (zero-padded, nibble-separated binary)
                66 AA 55 99 (zero-padded, octet-separated hex)
                1.2.3.255 (octet-separated dec)
        """
        off = '''
        if format is None:
            format = self.p_fmt
        if ( format == number.FMT_FLOAT ) or ( format == number.FMT_DOUBLE ):
            return ( '%%.%df' % precision ) % self.__float__()
        elif format == number.FMT_CHAR:
            return '%02d' % ( self.value & 0xFF )
        elif format == number.FMT_SHORT:
            return '%04d' % ( self.value & 0xFFFF )'''
        #############
        pass

    def get_zeros( self, base = 16 ):
        if base == 2:
            #############
            pass
        elif base == 8:
            #############
            pass
        elif base == 10:
            #############
            pass
        return self.nbytes


    def set_value( self, data ):

        # record the input data information
        self.idata = data
        self.itype = type( data )

        # data is given as a string
        if type( data ) is str:
            self._set_string( data )

        # data is given as a floating-point number
        elif type( data ) is float:
            self._set_float( data )

        # data is given as something I hope I can use
        else:
            self._set_integer( int( data ) )


    def _pstr( self, format = None ):
        if format is None:
            format = self.p_fmt
        if self.signed == True:
            return '<%s' % number._pstrs_s[ format ]
        return '<%s' % number._pstrs_u[ format ]

    def _set_float( self, value ):
        self.nbytes = 4
        self.p_fmt  = number.FMT_LONG
        self.packed = struct.pack( '<f', value )
        self.signed = True
        self.value  = struct.unpack( '<I', self.packed )[ 0 ]

    def _set_integer( self, value ):
        self.p_fmt = number.FMT_CHAR
        for limit in number._limits_u:
            if value <= limit:
                break
            self.p_fmt += 1
        self.nbytes = 2 ** self.p_fmt
        self.packed = struct.pack( self._pstr(), value )
        ## ZIH - add support for signed numbers
        self.signed = False
        self.value  = value

    def _set_string( self, data ):

        # check if a long, space-separated binary number is given
        m = re.match( r'[01]{4}( [01]{4}){1,7}', data )
        if m is not None:
            nibbles = data.split( ' ' )
            data = '0b' + ''.join( nibbles )

        # check if separated into octets (e.g. from a hex editor)
        elif data.find( ' ' ) != -1:
            octets = data.split( ' ' )
            octets.reverse()
            data = '0x' + ''.join( octets )

        # check if separated into octets (e.g. octet trees or IP addresses)
        else:
            m = re.match( r'\d{1,3}(\.\d{1,3}){3,7}', data )
            octets = data.split( '.' )
            ## ZIH - it's kinda confusing when this is ID'd as a string:hex
            data = '0x' + ''.join( [ ( '%X' % int( i ) ) for i in octets ] )

        # string contains a decimal (floating-point number)
        if data.find( '.' ) != -1:
            self.interp = 'string:float'
            self._set_float( float( data ) )

        # string begins with hexadecimal literal prefix
        elif re.match( r'^\s*0(x|X)[0-9a-fA-F]+', data ) is not None:
            self.interp = 'string:hex'
            self._set_integer( int( data, 16 ) )

        # string begins with hex color prefix
        elif re.match( r'^#[0-9a-fA-F]+', data ) is not None:
            self.interp = 'string:hex-color'
            # abbreviate hex color
            if len( data ) == 4:
                data = '#%s%s%s' % ( data[1] * 2, data[2] * 2, data[3] * 2 )
            self._set_integer( int( data[ 1 : ], 16 ) )

        # string begins with octal literal prefix
        elif re.match( r'^\s*0[0-7]+', data ) is not None:
            self.interp = 'string:oct'
            self._set_integer( int( data, 8 ) )

        # string begins with binary literal prefix
        elif re.match( r'^\s*0b(0|1)+', data ) is not None:
            self.interp = 'string:bin'
            self._set_integer( int( data, 2 ) )

        # string provides no hints to content
        else:
            self.interp = 'string:dec'
            self._set_integer( int( data ) )



#=============================================================================
def main( argv ):
    """ Script execution entry point """

    # initialize and start the user interface
    #ui = timecalc()
    #ui.mainloop()

    if len( argv ) > 1:
        if len( argv ) == 5:
            arg = ' '.join( argv[ 1 : ] )
        else:
            arg = argv[ 1 ]
        num = number( arg )
        print '%s (%s)\n  dec: %d  hex: 0x%X  oct: 0%o  flt: %f\n  bin: %s' % (
            arg,
            num.interp,
            int( num ),
            int( num ),
            int( num ),
            float( num ),
            bin( num )
        )

    else:
        print 'give me a number, any number, any format'

    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
