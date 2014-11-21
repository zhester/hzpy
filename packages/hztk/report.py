#!/usr/bin/env python


"""
Report Table Widget

This creates a composite widget designed to display tabular data.
"""


import Tkinter as tk
import tkFont
import ttk


# ZIH - temp
style = ttk.Style()
#style.configure( '.', relief = 'flat', borderwidth = 0 )
#style.layout( 'Treeview', [ ( 'Treeview.treearea', { 'sticky' : 'nswe' } ) ] )


#=============================================================================
class Data( ttk.Treeview ):
    """
    Models the data displayed by a report.
    """

    #=========================================================================
    def __init__( self, master, **kwargs ):
        """
        Initializes a Data object.
        """

        # initialize the parent frame
        apply( ttk.Treeview.__init__, ( self, master ), kwargs )

        # ZIH - left off setting up columns/headings here


    #=========================================================================
    def append( self, record ):
        """
        Appends a record to the report.
        """
        self.insert(
            '',                     # empty string signifies root item ID
            'end',                  # "end" = insertion at end of list
            text   = record[ 0 ],   # item text label
            values = record[ 1 : ]  # additional text labels in columns
        )


#=============================================================================
class Report( ttk.Frame ):
    """
    Report container widget

    The report widget is made up of several internal widgets that use a grid
    for layout control.

    The "data" widget is used to manage and display the data in the report.
    There are two scrollbar widgets that are connected to the data widget.
    """

    #=========================================================================
    def __init__( self, master, **kwargs ):
        """
        Initializes a Report object.
        """

        # initialize the parent frame
        apply( ttk.Frame.__init__, ( self, master ), kwargs )

        # set up resizable layout
        self.columnconfigure( 0, weight = 1 )
        self.rowconfigure( 0, weight = 1 )

        # create the data representation widget
        self.data = ReportData( self )

        # add the data widget to the report
        self.data.grid(
            row    = 0,
            column = 0,
            sticky = ( tk.N + tk.S + tk.E + tk.W )
        )

        # add a vertical scrollbar to the report widget
        self.vertical_scrollbar = ttk.Scrollbar(
            self,
            orient = 'vertical',
            command = self.data.yview
        )

        # add a horizontal scrollbar to the report widget
        self.horizontal_scrollbar = ttk.Scrollbar(
            self,
            orient = 'horizontal',
            command = self.data.xview
        )

        # attach the scrollbar inputs to the data widget's outputs
        self.data.configure(
            yscrollcommand = self.vertical_scrollbar.set,
            xscrollcommand = self.horizontal_scrollbar.set
        )

        # lay out the scrollbars
        self.vertical_scrollbar.grid(
            row    = 0,
            column = 1,
            sticky = ( tk.N + tk.S )
        )
        self.horizontal_scrollbar.grid(
            row    = 1,
            column = 0,
            sticky = ( tk.E + tk.W )
        )


#=============================================================================
class ReportColumn( object ):
    """
    Models a column in the report.  There is no visual component to this,
    it's only used to handle data and utility methods.
    """

    #=========================================================================
    def __init__( self, report, label = '', name = None ):
        """
        Initializes a ReportColumn object.
        """

        self.report = report
        self.label  = label
        self.font   = tkFont.Font()
        self.width  = 0
        if name is None:
            self.name = label
        else:
            self.name = name

        report.heading( self.name, text = self.label )
## ZIH - temp - add this to heading setup
#,                command = functools.partial( self._cmd_sort, c )
        self.fitWidth()


    #=========================================================================
    def fitWidth( self, text = None ):
        ## ZIH -
        # font measurement is off.  error aggregates with more characters.
        # short strings (2-ish characters) measure smaller than rendered.
        # long strings (10+ characters) measure larger than rendered.
        # consider implementing a curved adjustment to sizes based on
        # number of characters (piecewise linear curve)
        # a global "ui scale" factor could be added to the user's config
        # that would multiply the end measurement for odd situations
        ## ZIH - suspect Tkinter isn't actually measuring crap... it's
        # probably making up some generic em width, and multiplying by the
        # length of the string
        if text is None:
            text_size = self.font.measure( self.label )
            self.report.column( self.name, minwidth = ( self.width + 5 ) )
        else:
            text_size = self.font.measure( text )
        if self.width < text_size:
            self.width = text_size
            self.report.column( self.name, width = ( self.width + 5 ) )


#=============================================================================
class ReportData( ttk.Treeview ):
    """
    Represents the data contained in a report.
    """

    #=========================================================================
    def __init__( self, master, **kwargs ):
        """
        Initializes a ReportData object.
        """

        # initialize the parent Treeview widget
        apply( ttk.Treeview.__init__, ( self, master ), kwargs )

        # start the widget with a minimum height
        self.configure( height = 20 )

        # create storage for the report columns
        self._columns = []


    #=========================================================================
    def append( self, record ):
        """
        Appends a record to the report.
        """

        # insert the record in the tree view
        self.insert( '', 'end', text = record[ 0 ], values = record[ 1 : ] )

        # check for changes in column sizes
        num_fields = len( record )
        for i in range( num_fields ):
            self._columns[ i ].fitWidth( record[ i ] )


    #=========================================================================
    def clear( self ):
        """
        Removes all records from the report.
        """
        for record_id in self.get_children():
            self.delete( record_id )


    #=========================================================================
    def set_columns( self, columns ):
        """
        Sets the column names for the report.
        """

        # delete all the existing column handling objects
        num_columns = len( self._columns )
        for i in range( num_columns ):
            c = self._columns.pop()
            del c
        self._columns = []

        # count the total number of columns to display
        num_columns = len( columns )

        # build reproducable column names for future reference
        names = [ 'col_%02d' % c for c in range( num_columns ) ]

        # set the special column name (always refers to the first column)
        names[ 0 ] = '#0'

        # reassign the "extra" columns list in the control
        self[ 'columns' ] = tuple( names[ 1 : ] )

        # set up each column's display/behavior in the control
        for c in range( num_columns ):

            # create a column handling object (performs widget setup)
            self._columns.append(
                ReportColumn( self, label = columns[ c ], name = names[ c ] )
            )


    #=========================================================================
    def _cmd_sort( self, column_index ):
        ## ZIH - temp
        print 'Hey!  Sort by column %d' % column_index


#=============================================================================
if __name__ == "__main__":

    # dependencies only needed for testing
    import sys

    import util

    # some test data for testing reports
    test_data = [
        [ 0, 'Baker',   200 ],
        [ 1, 'Charlie', 100 ],
        [ 2, 'Adam',     42 ]
    ]

    # create a simple test application
    app = util.TestApp()
    app.master.title( 'Report Test Application' )
    app.master.geometry( '480x320' )

    # create a bare data listing widget
    bare_data = util.create_wrapped( Data, app, row = 0 )

    # put data in the widget
    for r in test_data:
        bare_data.append( r )

    # create a report, and set up the widget layout
    #rep = util.create_wrapped( Report, app, row = 1 )

    # put data in the report
    #rep.data.set_columns( [ 'A', 'B', 'C' ] )
    #for r in test_data:
    #    rep.data.append( r )

    # run the test application
    app.mainloop()

    # return to the shell
    sys.exit( 0 )

