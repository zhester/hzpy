#!/usr/bin/env python
##############################################################################
#
# tk.py -or- tk.pyw
#
# 1. Globally replace "MYAPP" with the symbol name of the new application.
# 2. Update "application info" at the top of MYAPP class.
#
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html
# http://effbot.org/tkinterbook/
#
# Todo:
#   - tk.Canvas, tk.Listbox, tk.Message, tk.OptionMenu, tk.Spinbox, tk.Text
#   - build a simple text editor with file handling
#   - implement some parameterized event handlers
#   + StatusBar.useWidget() to swap a label for a user's widget
#   - ttk.PanedWindow
#   - make an hztk.py module that provides an intermediate class that just
#     lets you start making a normal, native-looking GUI immediately
#
##############################################################################


import os
import Tkinter as tk
import tkMessageBox
import ttk


#=============================================================================
class MYAPP( ttk.Frame ):
    """ Application root frame """

    # application info
    _author  = 'Zac Hester <zac.hester@gmail.com>'
    _date    = '2013-06-28'
    _icon    = 'tk.ico'
    _title   = 'My Application'
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
        """ Initializes MYAPP instance """

        # call the parent constructor
        ttk.Frame.__init__( self, parent )

        # create a place to keep widget state
        self.wvars = {}

        # set the application-wide default icon
        if os.path.exists( 'tk.ico' ):
            self.master.call(
                'wm',
                'iconbitmap',
                self.master._w,
                '-default',
                MYAPP._icon
            )

        # set the application title
        self.master.title( MYAPP._title )

        # this sets up the root frame to resize things
        #   any descendent widgets will also need to use _gridcfg_stick
        self.grid( **MYAPP._gridcfg_stick )
        top = self.winfo_toplevel()
        top.rowconfigure( 0, weight = 1 )
        top.columnconfigure( 0, weight = 1 )
        self.rowconfigure( 0, weight = 1 )
        self.columnconfigure( 0, weight = 1 )

        # initialize the GUI's widgets
        self._create_widgets()

    #=========================================================================
    def _create_example_1( self, parent ):

        group = ttk.LabelFrame(
            parent,
            text = 'Group Name'
        )
        group.grid( **MYAPP._gridcfg_label )

        button = ttk.Button(
            group,
            text = 'Hello',
            command = self._cmd_hello
        )
        button.grid( row = 0, column = 0, **MYAPP._gridcfg_wpad )

        button = ttk.Button(
            group,
            text = 'Quit',
            command = self.quit
        )
        button.grid( row = 0, column = 1, **MYAPP._gridcfg_wpad )

    #=========================================================================
    def _create_example_2( self, parent ):

        cfg = MYAPP._gridcfg_wpad

        group = ttk.LabelFrame(
            parent,
            text = 'Basic Widgets'
        )
        group.grid( **MYAPP._gridcfg_label )

        # checkbox example
        self.wvars[ 'cbstate' ] = tk.IntVar()
        self.wvars[ 'cbstate' ].set( 0 )
        ttk.Checkbutton(
            group,
            text = 'Checkbutton',
            variable = self.wvars[ 'cbstate' ]
        ).grid( **cfg )

        # entry example
        self.wvars[ 'etext' ] = tk.StringVar()
        self.wvars[ 'etext' ].set( 'Entry' )
        ttk.Entry( group, textvariable = self.wvars[ 'etext' ] ).grid( **cfg )

        # label example
        ttk.Label( group, text = 'Label' ).grid( **cfg )

        # radio group example
        self.wvars[ 'radio' ] = tk.IntVar()
        ttk.Radiobutton(
            group,
            text = 'Radio 1',
            value = 1,
            variable = self.wvars[ 'radio' ]
        ).grid()
        ttk.Radiobutton(
            group,
            text = 'Radio 2',
            value = 2,
            variable = self.wvars[ 'radio' ]
        ).grid()
        ttk.Radiobutton(
            group,
            text = 'Radio 3',
            value = 3,
            variable = self.wvars[ 'radio' ]
        ).grid()

        group = ttk.LabelFrame(
            parent,
            text = 'Complex Widgets'
        )
        group.grid( **MYAPP._gridcfg_label )

        # combo box example
        cbox = ttk.Combobox(
            group,
            values = ( 'Option 1', 'Option 2', 'Option 3' )
        )
        cbox.set( 'Combobox' )
        cbox.grid( **cfg )

        # progress bar examples
        bar = ttk.Progressbar( group )
        bar.grid( **cfg )
        bar.start()
        # use .stop() to stop, and .step() to manually update
        bar = ttk.Progressbar( group, mode = 'indeterminate' )
        bar.grid( **cfg )
        bar.start()

        # scale example
        ttk.Scale( group ).grid( **cfg )

        # scroll bar example
        ttk.Scrollbar( group, orient = tk.HORIZONTAL ).grid( **cfg )

        # tree view example
        #tv = ttk.Treeview( group ).grid( **cfg )

    #=========================================================================
    def _create_menu( self ):

        self.menubar = tk.Menu( self )

        menu = tk.Menu( self.menubar, tearoff = 0 )
        self.menubar.add_cascade( label = 'File', menu = menu )
        menu.add_command( label = 'Hello', command = self._cmd_hello )

        menu = tk.Menu( self.menubar, tearoff = 0 )
        self.menubar.add_cascade( label = 'Help', menu = menu )
        menu.add_command( label = 'About', command = self._cmd_about )

        self.master.config( menu = self.menubar )

    #=========================================================================
    def _create_statusbar( self ):
        self.statusBar = StatusBar( self, 2, ( 'Status', 'Status 2' ) )
        self.statusBar.setStatus( 0, 'Status 1' )

    #=========================================================================
    def _create_tabs( self, parent ):

        #style = ttk.Style()
        #style.configure( 'Page.TFrame', background = 'white' )
        #style.configure( 'TLabelframe', background = 'white' )
        #style.configure( 'TLabelframe.Label', background = 'white' )

        book = ttk.Notebook( parent )
        book.columnconfigure( 0, weight = 1 )

        tab = ttk.Frame( parent, style = 'Page.TFrame' )
        tab.columnconfigure( 0, weight = 1 )
        self._create_example_1( tab )
        book.add( tab, text = 'Basic Tab' )

        tab = ttk.Frame( parent, style = 'Page.TFrame' )
        tab.columnconfigure( 0, weight = 1 )
        self._create_example_2( tab )
        book.add( tab, text = 'Demo Tab' )


        tab = ttk.Frame( parent, style = 'Page.TFrame' )
        tab.columnconfigure( 0, weight = 1 )
        t = Table( tab, rows = 8, columns = 4 )
        t.grid()
        t.set( 0, 0, '0,0' )
        t.set( 0, 1, '0,1' )
        t.set( 1, 4, '1,4' )
        t.set( 2, 7, '2,7' )
        t.set( 3, 0, 'a cell with a lot of text' )
        t.set( 3, 1, 'another cell with a lot of text' )
        book.add( tab, text = 'Table Tab' )


        tab = ttk.Frame( parent, style = 'Page.TFrame' )
        tab.columnconfigure( 0, weight = 1 )
        tv = ttk.Treeview( tab, columns = ( 'col1', 'col2' ) )
        tv.xview()
        tv.yview()
        tv.heading( '#0',  text = 'Col 0' )
        tv.heading( 'col1', text = 'Col 1' )
        tv.heading( 'col2', text = 'Col 2',
            command = lambda: sys.stdout.write('Sort by col2\n') )
        tv.column( '#0', stretch = False )
        tv.column( 'col1', stretch = True )
        tv.column( 'col2', stretch = False )
        tv.grid( **MYAPP._gridcfg_stick )
        tv.insert( '', 'end', 'r1_key', text = 'Row 1',
            values = ( 'Value 1,1', 'Value 1,2' ),
            tags = ( 'style_tag', 'behavior_tag' ) )
        tv.tag_configure( 'style_tag', background = '#EEEEEE' )
        tv.tag_bind( 'behavior_tag', '<1>',
            lambda e: sys.stdout.write('Clicked %s\n'%str(tv.focus())) )
        r2_id = tv.insert( '', 'end', 'r2_key', text = 'Row 2',
            values = ( 'Value 2,1', 'Value 2,2' ) )
        tv.insert( 'r2_key', 'end', text = 'Row 2 A' )
        tv.insert( r2_id, 'end', text = 'Row 2 B' )
        book.add( tab, text = 'Tree Tab' )
        scrollbar_howto = """
winDirSel = tk.Toplevel()
winDirSel.title('Select Test Directory...')
tvwDirSel = ttk.Treeview(winDirSel,
                         height=10,padding=3,
                         show='tree')
lblTestDir = tk.Label(winDirSel, relief=tk.SUNKEN,
                      justify=tk.LEFT, anchor=tk.W,
                      textvariable=ctrlTestDir,width=80)
scbHDirSel = ttk.Scrollbar(winDirSel,
                           orient=tk.HORIZONTAL,
                           command=tvwDirSel.xview)
scbVDirSel = ttk.Scrollbar(winDirSel,
                           orient=tk.VERTICAL,
                           command=tvwDirSel.yview)
tvwDirSel.configure(xscrollcommand=scbHDirSel.set,
                    yscrollcommand=scbVDirSel.set)
lblTestDir.grid(row=0,column=0,sticky=tk.EW)
tvwDirSel.grid(row=1,column=0,sticky=tk.NSEW)
scbVDirSel.grid(row=1,column=1,sticky=tk.NS)
scbHDirSel.grid(row=2,column=0,sticky=tk.EW)
winDirSel.rowconfigure(1,weight=1)
winDirSel.columnconfigure(0,weight=1)
        """


        book.grid( **MYAPP._gridcfg_stick )

    #=========================================================================
    def _create_widgets( self ):
        """ Builds the root frame's interface """
        self._create_menu()
        self._create_tabs( self )
        self._create_statusbar()

    #=========================================================================
    def _cmd_about( self ):
        """ Displays the application about info """
        tkMessageBox.showinfo(
            'About %s' % MYAPP._title,
            '%s\nVersion: %s\nDate: %s\nAuthor: %s' % (
                MYAPP._title,
                MYAPP._version,
                MYAPP._date,
                MYAPP._author
            )
        )

    #=========================================================================
    def _cmd_hello( self ):
        """ Example of using a message box """
        tkMessageBox.showinfo( 'Hello', 'Well, hello there!' )



#=============================================================================
class Table( ttk.Frame ):

    # anything that needs to be extra sticky can use this
    _gcfg_stick = {
        'sticky' : ( tk.N + tk.E + tk.S + tk.W )
    }

    #=========================================================================
    def __init__( self, parent, rows = 2, columns = 2 ):
        """ Initializes the table widget """

        # call the parent constructor
        ttk.Frame.__init__( self, parent )

        # create a style for the labels used to display text in a cell
        style = ttk.Style()
        style.configure(
            'TableCell.TLabel',
            background = 'white',
            padding    = 1
        )

        # create the table widgets
        self.matrix = self._create_table( self, rows, columns )

    #=========================================================================
    def set( self, x, y, value ):
        """ Sets the string of a given table cell """
        self.matrix[ y ][ x ].label.configure( text = value )

    #=========================================================================
    def _create_table( self, parent, rows, columns ):
        row_list = []
        row = 0
        for rindex in range( rows ):
            ref = self._create_row( parent, row, columns )
            row_list.append( ref )
            row += 1
        return row_list

    #=========================================================================
    def _create_row( self, parent, row, columns ):
        cell_list = []
        column = 0
        for cindex in range( columns ):
            cell = self._create_cell( parent )
            cell.grid( row = row, column = column, **Table._gcfg_stick )
            cell_list.append( cell )
            column += 1
        return cell_list

    #=========================================================================
    def _create_cell( self, parent ):
        frame = ttk.Frame(
            parent,
            padding = ( 0, 0, 1, 1 )
        )
        frame.label = ttk.Label(
            frame,
            style = 'TableCell.TLabel'
        )
        frame.label.grid( **Table._gcfg_stick )
        frame.columnconfigure( 0, weight = 1 )
        return frame


#=============================================================================
class StatusBar( ttk.Frame ):
    """ A specialized frame for displaying a status bar """

    #=========================================================================
    def __init__( self, parent, count = 1, initial = () ):
        """ Initializes the status bar widget """

        # call the parent constructor
        ttk.Frame.__init__( self, parent )

        # initialize some internal memory
        self.fields = []
        self.values = []

        # build the status bar label fields
        column = 0
        for index in range( count ):

            # insert separators between label fields
            if index > 0:
                ttk.Separator( self, orient = tk.VERTICAL ).grid(
                    row = 0,
                    column = column,
                    sticky = ( tk.N + tk.S )
                )
                column += 1

            # create a modifiable text variable for this label
            tvar = tk.StringVar()
            if len( initial ) > index:
                tvar.set( initial[ index ] )
            self.values.append( tvar )

            # create a standard label to display the status
            label = ttk.Label( self, textvariable = tvar )
            label.grid( row = 0, column = column, padx = 4, pady = 2 )
            self.fields.append( label )
            column += 1

        # add a size grip area to the corner
        if count > 0:
            column = count + ( count - 1 )
        else:
            column = 0
        ttk.Sizegrip( self ).grid( row = 0, column = column, sticky = tk.SE )
        self.columnconfigure( column, weight = 1 )

        # make sure the widget fills the column
        self.grid( sticky = ( tk.E + tk.W ) )

    #=========================================================================
    def setStatus( self, index, text ):
        """ Sets the text displayed in a status bar field """

        # check the requested index
        if index < len( self.values ):

            # set the text in the label
            self.values[ index ].set( text )

            # return success
            return True

        # no field available for the requested index
        return False


#=============================================================================
def main( argv ):
    """ script execution entry point """

    # initialize and start the user interface
    ui = MYAPP()
    ui.mainloop()

    # return success
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
