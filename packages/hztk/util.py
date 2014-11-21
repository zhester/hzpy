#!/usr/bin/env python


"""
Various Utilities
"""


import Tkinter as tk
import ttk


#=============================================================================

# commonly-used values for setting up widgets in grid layouts
STICK_ALL  = tk.N + tk.E + tk.S + tk.W
STICK_HORZ = tk.E + tk.W
STICK_VERT = tk.N + tk.S


#=============================================================================
def create_wrapped(
    widget,             # widget class
    master   = None,    # parent widget
    row      = 0,       # row in the grid
    column   = 0,       # column in the grid
    grid     = None,    # dictionary of extra grid options
    **kwargs            # keyword arguments passed to widget initializer
):
    """
    Creates any widget "wrapped" in its parent.

    This is merely a convenience function, but the code is commonly repeated
    all over grid layouts that need to be resizeable.
    """

    # create the widget
    w = widget( master, **kwargs )

    # check for grid overrides
    if grid is not None:
        if 'sticky' not in grid:
            grid[ 'sticky' ] = STICK_ALL
    else:
        grid = { 'sticky' : STICK_ALL }

    # set the widget's layout in the grid
    w.grid( **grid )

    # set the positional grid configuration
    w.columnconfigure( column, weight = 1 )
    w.rowconfigure(    row,    weight = 1 )

    # return the constructed widget
    return w


#=============================================================================
class TestApp( ttk.Frame ):
    """
    Basic testing application.
    """

    #=========================================================================
    def __init__( self, master = None, **kwargs ):
        """
        Initializes a TestApp object.
        """

        # initialize the application's frame
        apply( ttk.Frame.__init__, ( self, master ), kwargs )

        # set the application title
        self.master.title( 'TestApp' )

        # set up the root frames for resizing
        self.grid( sticky = STICK_ALL )
        top = self.winfo_toplevel()
        top.columnconfigure( 0, weight = 1 )
        top.rowconfigure( 0, weight = 1 )
        self.columnconfigure( 0, weight = 1 )
        self.rowconfigure( 0, weight = 1 )


#=============================================================================
if __name__ == "__main__":

    # dependencies only used for testing
    import sys
    import tkMessageBox

    # create a basic test application
    app = TestApp()

    # test command handler
    def test():
        tkMessageBox.showinfo( 'Greetings', 'Hello World!' )

    # add something to display
    button = ttk.Button( app, text = 'Greet', command = test )
    button.grid( padx = 5, pady = 5 )

    # run the test application
    app.mainloop()

    # return to shell
    sys.exit( 0 )

