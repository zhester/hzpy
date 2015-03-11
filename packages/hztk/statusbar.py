#!/usr/bin/env python

"""
Status Bar

The status bar is a pre-built ttk.Frame object that manages a set of child
widgets.  The intent is to provide the traditional application status area at
the bottom of the top-level frame.  This simplifies the process of creating
and updating the status area.
"""


import Tkinter as tk
import ttk


#=============================================================================
class StatusBar( ttk.Frame ):
    """
    A specialized frame for displaying a status bar
    """


    #=========================================================================
    def __init__( self, master, initial = None, grip = True, **kwargs ):
        """
        Initializes the status bar widget.
        """

        # call the parent constructor
        apply( ttk.Frame.__init__, ( self, master ), kwargs )

        # check for an unspecified list of fields
        if initial is None:
            initial = ( '', )

        # initialize some internal state
        self.fields = []
        self.values = []

        # set the current column in the grid
        grid_column = 0

        # build the status bar label fields
        num_fields = len( initial )
        for index in range( num_fields ):

            # insert separators between label fields
            if index > 0:
                ttk.Separator( self, orient = tk.VERTICAL ).grid(
                    row    = 0,
                    column = grid_column,
                    padx   = 0,
                    pady   = 2,
                    sticky = ( tk.N + tk.S )
                )
                grid_column += 1

            # create a modifiable text variable for this label
            tvar = tk.StringVar()
            tvar.set( initial[ index ] )
            self.values.append( tvar )

            # create a standard label to display the status
            label = ttk.Label( self, textvariable = tvar )
            label.grid(
                row    = 0,
                column = grid_column,
                padx   = 4,
                pady   = 2,
                sticky = ( tk.N + tk.E + tk.S + tk.W )
            )
            self.columnconfigure( grid_column, weight = 1 )
            self.fields.append( label )
            grid_column += 1

        # add a size grip area to the corner
        if grip == True:
            ttk.Sizegrip( self ).grid(
                row    = 0,
                column = ( grid_column - 1 ),
                sticky = tk.SE
            )


    #=========================================================================
    def __getitem__( self, index ):
        """
        Provides index-style access to retrieve each status field.
        """
        if ( type( index ) is not int ) or ( index >= len( self.values ) ):
            raise IndexError(
                'Invalid index "{}" in status bar labels.'.format( index )
            )
        return self.values[ index ].get()


    #=========================================================================
    def __setitem__( self, index, value ):
        """
        Provides index-style access to update each status field.
        """
        if ( type( index ) is not int ) or ( index >= len( self.values ) ):
            raise IndexError(
                'Invalid index "{}" in status bar labels.'.format( index )
            )
        self.values[ index ].set( value )


#=============================================================================
if __name__ == "__main__":

    # dependencies only needed for testing
    import sys
    import tkMessageBox

    import util

    # create a test handler in a closer
    def make_test1( bar ):

        # demonstrate updating a field
        def test():
            bar[ 0 ] = 'Greetings'
        return test

    # create a test handler in a closer
    def make_test2( bar ):

        # demonstrate retrieving a field
        def test():
            tkMessageBox.showinfo( 'Who?', bar[ 1 ] )
        return test

    # create the application frame and some widgets
    frame   = util.TestApp()
    bar     = StatusBar( frame, ( 'Hello', 'World' ) )
    button1 = ttk.Button( frame, text = 'Greet', command = make_test1( bar ) )
    button2 = ttk.Button( frame, text = 'Who?',  command = make_test2( bar ) )

    # lay out the application
    button1.grid( row = 0, column = 0, padx = 5, pady = 5 )
    button2.grid( row = 0, column = 1, padx = 5, pady = 5 )
    bar.grid( columnspan = 2, sticky = ( tk.E + tk.W ) )

    # display the application
    frame.master.title( 'StatusBar Demo' )
    frame.mainloop()
    sys.exit( 0 )

