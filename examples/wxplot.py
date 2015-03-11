#*******************************************************************************
# wxplot.py
# Zac Hester <zac.hester@gmail.com>
# 2012-08-10
#
# Experimental numpy/matplotlib plotting within wxPython.
#
#*******************************************************************************

#-------------------------------------------------------------------------------
#                                   IMPORTS
#-------------------------------------------------------------------------------

import  math
import  numpy
import  sys
import  wx

# Special-case importing of parts of matplotlib
import  matplotlib
matplotlib.use( 'WXAgg' )
from    matplotlib.figure                   import Figure
from    matplotlib.backends.backend_wxagg   import FigureCanvasWxAgg

#-------------------------------------------------------------------------------
#                                  VARIABLES
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#                                   CLASSES
#-------------------------------------------------------------------------------


#===============================================================================
class PlotPanel( FigureCanvasWxAgg ):
    """ wx panel for plotting """


    #===========================================================================
    def __init__( self, parent, id = wx.ID_ANY, *args, **kwargs ):
        self.figure = Figure( ( 4.0, 3.0 ), dpi = 100 )
        super( PlotPanel, self ).__init__( parent,
                                           id,
                                           self.figure,
                                           *args,
                                           **kwargs )
        self.plot = self.figure.add_subplot( 1, 1, 1 )
        self.pick_radius = 5
        self.mpl_connect( 'pick_event', self.handlePick )


    #===========================================================================
    def render( self ):
        """ renders/redraws the plot """
        self.plot.clear()

        #### replace with real source of data
        y = [ math.sin( ( float( i ) / 63.0 ) * 2.0 * 3.14159 )
                   for i in range( 64 ) ]
        x = [ float( i ) / 63.0 for i in range( 64 ) ]

        self.plot.plot( x, y, picker = self.pick_radius )
        self.draw()


    #===========================================================================
    def setSize( self, width, height ):
        """ resizes the figure """
        self.figure.set_size_inches( ( float( width )
                                       / float( self.figure.dpi ) ),
                                     ( float( height )
                                       / float( self.figure.dpi ) ) )


    #===========================================================================
    def handlePick( self, event ):

        # Picker events should include an artist attribute.
        if not hasattr( event, 'artist' ):
            print 'Pick event for event without artist: %s' \
                  % event.__class__.__name__

        # Check for pick events without mouse events.
        elif not hasattr( event, 'mouseevent' ):
            print 'Pick event for event without mouseevent: %s' \
                  % event.__class__.__name__

        # Check for Line2D objects selected by the picker.
        elif isinstance( event.artist, matplotlib.lines.Line2D ):
            xdata = event.artist.get_xdata()
            ydata = event.artist.get_ydata()
            # Default to the first/only data point index.
            index = event.ind[ 0 ]
            # Check for multiple points inside the picker hit region, and that
            #   the pick event populated mouse coordinates.
            if ( ( len( event.ind ) > 1 )
               and ( event.mouseevent.xdata is not None ) ):
                # Set a tuple for the mouse data coordinates.
                mdcoord  = ( event.mouseevent.xdata,
                             event.mouseevent.ydata )
                # Set an excessive radius between data points in the same
                #   picker hit region.
                mpradius = self.pick_radius + 1.0
                # Check the distances between all included data points and
                #   the coordinate where the mouse was clicked.
                for i in event.ind:
                    r = self.getRadius( mdcoord,
                                        ( xdata[ i ], ydata[ i ] ) )
                    # Try to select the data point closest to the click.
                    if r < mpradius:
                        mpradius = r
                        index    = i
            print 'Line2D pick: %f %f' % ( xdata[ index ], ydata[ index ] )

        # Check for Rectangle objects selected by the picker.
        elif isinstance( event.artist, matplotlib.patches.Rectangle ):
            print 'Rectangle pick: ', event.artist.patch.get_path()

        # Check for Text objects selected by the picker.
        elif isinstance( event.artist, matplotlib.text.Text ):
            print 'Text pick: ', event.artist.text.get_text()

        # This is an artist not supported by this pick handler.
        else:
            print 'Pick event for unsupported artist: %s' \
                  % event.artist.__class__.__name__


    #===========================================================================
    def getRadius( self, a, b ):
        """ calculate the distance between two points (array-like x,y) """
        return numpy.sqrt( ( ( b[ 0 ] - a[ 0 ] ) ** 2 )
                         + ( ( b[ 1 ] - a[ 1 ] ) ** 2 ) )


#===============================================================================
class PlotFrame( wx.Frame ):
    """ wx frame for plotting """


    #===========================================================================
    def __init__( self, parent, id, title ):
        """ instantiate the frame object """

        # Call the parent constructor.
        super( PlotFrame, self ).__init__( parent, id, title )

        # Create a new plot panel.
        self.plot = PlotPanel( self )

        ### testing
        #self.plot.setSize( 640, 480 )

        # Run the first render of the plot.
        self.plot.render()

        # Attach it to the layout.
        vbox = wx.BoxSizer( wx.VERTICAL )
        vbox.Add( self.plot, flag = wx.EXPAND )
        hbox = wx.BoxSizer( wx.HORIZONTAL )
        hbox.Add( vbox, flag = wx.EXPAND )
        self.SetAutoLayout( True )
        self.SetSizer( hbox )

        # Tell the sizer to resize the frame to fit its minimum dimension.
        hbox.Fit( self )

        # Make sure the frame was drawn the layout at least once.
        self.Layout()



#===============================================================================
class PlotApp( wx.App ):
    """ wx plotting application """


    #===========================================================================
    def OnInit( self ):
        """ handle application initialization events """

        # Create the top-level frame for the application.
        frame = PlotFrame( None, wx.ID_ANY, "wxPlot" )

        # Ask the window manager to display it.
        frame.Show( True )

        # Set the frame as the application's top frame.
        self.SetTopWindow( frame )

        # Return success.
        return True


#-------------------------------------------------------------------------------
#                                  FUNCTIONS
#-------------------------------------------------------------------------------


#===============================================================================
def main( argv ):
    """ Script execution entry point """

    # Create the application (put stdout/stderr on the shell).
    app = PlotApp( False )

    # Run the application loop.
    app.MainLoop()

    # Return success.
    return 0


#===============================================================================
if __name__ == '__main__':
    sys.exit( main( sys.argv ) )
