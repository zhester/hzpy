#!/usr/bin/env python


"""
Simulation of Simple LCD/TFT Hardware Displays
"""


import Tkinter as tk
import tkMessageBox
import ttk


__version__ = '0.0.0'


#=============================================================================
#class ui( ttk.Frame ):
class ui( tk.Tk ):
    """
    Display Simulation User Interface
    """

    #=========================================================================
    def __init__( self, width = 128, height = 128, *args, **kwargs ):
        """
        Initializes a ui object.
        """
        ### ZIH - works with old Tk, not with ttk
        # part of this might be because ttk doesn't use fg/bg?
        #ttk.Frame.__init__( self, *args, **kwargs )
        tk.Tk.__init__( self, *args, **kwargs )
        self.config( padx = 0, pady = 0 )
        self.canvas = tk.Canvas(
            self,
            width  = width,
            height = height,
            bg     = 'black'
        )
        self.canvas.pack( ipadx = 0, ipady = 0, padx = 0, pady = 0 )
        self.raster = tk.PhotoImage( width = width, height = height )
        self.canvas.create_image(
            ### ZIH - why do i need this 2 pixel offset to position the
            # image?  there also seems to be a superfluous 2 pixel padding
            # around the canvas
            #( ( ( width >> 1 ) + 2 ), ( ( height >> 1 ) + 2 ) ),
            ( 2, 2 ),
            anchor   = tk.NW,
            image    = self.raster,
            #state    = 'normal' ### see if tk.NORMAL works
            state    = tk.NORMAL
        )

    #=========================================================================
    def pixel( self, x, y, c = '#ffffff' ):
        """
        Draws single pixel on the canvas.
        """
        self.raster.put( c, ( x, y ) )


#=============================================================================
def start_sim():
    """
    Starts a Simulation
    """
    sim = ui()
    for y in range( 128 ):
        for x in range( 128 ):
            sim.pixel( x, y, '#FF0000' )

    for y in range( 128 ):
        sim.pixel( 0, y, '#0000FF' )

    sim.mainloop()


#=============================================================================
def main( argv ):
    """
    Script execution entry point
    @param argv         Arguments passed to the script
    @return             Exit code (0 = success)
    """

    # imports when using this as a script
    import argparse

    # create and configure an argument parser
    parser = argparse.ArgumentParser(
        description = 'Simulation of Simple LCD/TFT Hardware Displays',
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
    start_sim()

    # return success
    return 0


#=============================================================================
if __name__ == "__main__":
    import os
    import sys
    sys.exit( main( sys.argv ) )


