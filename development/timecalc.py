#!/usr/bin/env python
##############################################################################
#
# timecalc.py
#
# Time Calculator
#
##############################################################################


import os
import re
import Tkinter as tk
import ttk


#=============================================================================
class timecalc( ttk.Frame ):

    # application info
    _author  = 'Zac Hester <zac.hester@gmail.com>'
    _date    = '2013-08-23'
    _icon    = 'timecalc.ico'
    _title   = 'Time Calculator'
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



def get_ms( data ):

    # ZIH - need to add support for mm:ss.fff pattern
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

        # h:mm:ss
        elif len( matches ) == 3:
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
