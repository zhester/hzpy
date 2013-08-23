#!/usr/bin/env python
##############################################################################
#
# timecalc.py
#
# Time Calculator
#
##############################################################################


import os
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





#=============================================================================
def main( argv ):
    """ Script execution entry point """

    # initialize and start the user interface
    ui = timecalc()
    ui.mainloop()

    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
