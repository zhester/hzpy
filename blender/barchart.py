#*******************************************************************************
# barchart.py
#
# Zac Hester <zac.hester@gmail.com>
# 2012-07-19
#
# Creates a 3D bar chart in Blender (http://blender.org/) using data sourced
# from a CSV file.
#
# Usage notes:
#   Global bar chart creation options can be found under:
#       Properties > Object > Bar Chart
#
#   Add a bar chart to the scene through either:
#       Add > Mesh > Bar Chart
#           or
#       [space] "bar chart"
#
#   This will prompt the user to select a file.  The data source must be a
#   CSV-format file (easily exported from most data, math, statistics, and
#   reporting applications).
#
#   The bar chart's origin is the current location of the cursor.
#
#*******************************************************************************

bl_info = {
    'name':        'Bar Chart',
    'author':      'Zac Hester',
    'version':     ( 0, 0 ),
    'blender':     ( 2, 6, 3 ),
    'location':    'Add > Mesh',
    'description': 'Creates a 3D bar chart using data sourced from a CSV file',
    'warning':     '',
    'wiki_url':    '',
    'tracker_url': '',
    'category':    'Data Visualization'
}

#-------------------------------------------------------------------------------
#                                   IMPORTS
#-------------------------------------------------------------------------------

import  bmesh
import  bpy
from    bpy.props       import ( BoolProperty,
                                 FloatProperty,
                                 FloatVectorProperty,
                                 StringProperty )
from    bpy_extras      import object_utils
import  csv


#-------------------------------------------------------------------------------
#                                   CLASSES
#-------------------------------------------------------------------------------


class PrepareBarChart( bpy.types.Panel ):
    """ Allow the user to prepare a bar chart """

    # Blender panel properties
    bl_label       = "Make Bar Chart"
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"


    def draw( self, context ):
        """ Draw the panel """

        # Assign shortcuts to the layout and scene.
        t = self.layout
        s = context.scene

        # Add property controls to the panel.
        for key in s.bcProps.keys():
            t.prop( s, key )

        # Add a button to use the operator.
        t.operator( "barchart.make" )



class MakeBarChart( bpy.types.Operator ):
    """ Create a bar chart object """

    # Blender operator properties
    bl_idname = "barchart.make"
    bl_label  = "Bar Chart"

    # Properties used for operator transforms.
    view_align = BoolProperty( name    = "Align to View",
                               default = False )
    location   = FloatVectorProperty( name    = "Location",
                                      subtype = "TRANSLATION" )
    rotation   = FloatVectorProperty( name    = "Rotation",
                                      subtype = "EULER" )

    # Set the magical "filepath" property for file selection.
    filepath = StringProperty( name        = "Data Source",
                               description = "Select a CSV data file.",
                               subtype     = "FILE_PATH" )

    # Debugging flag.
    debug = True


    def invoke( self, context, event ):
        """ Invoke the operator """

        # Allow the user to select a data file.
        context.window_manager.fileselect_add( self )

        # Inform the caller the operator is waiting on the user.
        return { 'RUNNING_MODAL' }


    def execute( self, context ):
        """ Run the operator """

        # Assign a shortcut to the scene.
        s = context.scene

        # Display some debugging output on the console.
        if self.debug:
            print( "Making bar chart..." )
            print( "X: %f, Y: %f, S: %f" % ( s.barX, s.barY, s.barS ) )
            print( "Data File: %s" % self.filepath )

        # Build the bar chart object, and add it to the scene.
        self.addBarChart( context )

        # Inform the caller the operator finished successfully.
        return { 'FINISHED' }


    def addBarChart( self, context ):
        """ Build the bar chart mesh, and add it to the scene """

        # Set a shortcut to the scene.
        s = context.scene

        # Load the chart data.
        data = self.loadData( self.filepath )

        # Data series stepping variable.
        yStep = 0

        # Iterate over each series in the data.
        for series in data:

            # Data point stepping variable.
            xStep = 0

            # Iterate over each data point in the series.
            for point in series:

                # Create a bar for this point.
                b = self.createBar( ( xStep * s.barS ),
                                    ( yStep * s.barS ),
                                    point,
                                    s.barX,
                                    s.barY )

                # Create a new mesh instance, and load the mesh data.
                m = bpy.data.meshes.new( "Bar_%d_%d" % ( xStep, yStep ) )
                b.to_mesh( m )
                m.update()

                # Add it to the scene.
                object_utils.object_data_add( context, m, operator = self )

                # Advance the X-direction step.
                xStep += 1

            # Advance the Y-direction step.
            yStep += 1


    def createBar( self, x, y, h, w, d ):
        """ Construct the mesh for a single bar """

        # Create a blender mesh.
        b = bmesh.new()

        # Add the base vertices, and the face.
        b.verts.new( ( x,         y,         0 ) )
        b.verts.new( ( ( x + w ), y,         0 ) )
        b.verts.new( ( ( x + w ), ( y + d ), 0 ) )
        b.verts.new( ( x,         ( y + d ), 0 ) )
        b.faces.new( [ b.verts[ i ] for i in range( 0, 4 ) ] )

        # Add the top vertices, and the face.
        b.verts.new( ( x,         y,         h ) )
        b.verts.new( ( ( x + w ), y,         h ) )
        b.verts.new( ( ( x + w ), ( y + d ), h ) )
        b.verts.new( ( x,         ( y + d ), h ) )
        b.faces.new( [ b.verts[ i ] for i in range( 4, 8 ) ] )

        # Add the walls.
        b.faces.new( [ b.verts[ i ] for i in [ 0, 1, 5, 4 ] ] )
        b.faces.new( [ b.verts[ i ] for i in [ 1, 2, 6, 5 ] ] )
        b.faces.new( [ b.verts[ i ] for i in [ 2, 3, 7, 6 ] ] )
        b.faces.new( [ b.verts[ i ] for i in [ 3, 0, 4, 7 ] ] )

        # Return the blender mesh.
        return b


    def loadData( self, filename, rotate = True ):
        """ Load data from a CSV file """

        # Open the input file for reading (as CSV data).
        csv_file = csv.reader( open( filename ) )

        # Buffer the data from the CSV file.
        row_data = []
        for row in csv_file:
            rec = []
            for cell in row:
                cell = cell.strip()
                if len( cell ) > 0:
                    rec.append( float( cell ) )
                else:
                    rec.append( 0.0 )
            row_data.append( rec )

        # Rotate the data so we can loop through each related set.
        if rotate:

            # Return column-oriented data.
            return [ [ row[ i ] for row in row_data ]
                     for i in range( len( row_data[ 0 ] ) ) ]

        # Return row-oriented data.
        return row_data


def menu_func( self, context ):
    """ Addon menu function """

    # Show the operator in the menu.
    self.layout.operator( MakeBarChart.bl_idname, icon = 'MESH_CUBE' )


def register():
    """ Register the bar chart addon """

    # Assign a shortcut to the scene class.
    s = bpy.types.Scene

    # Create a dictionary of bar chart properties.
    s.bcProps = {
        'barX': FloatProperty( name        = "Bar Width",
                               description = "X-dimension length of bars.",
                               min         = 0.1,
                               max         = 100.0,
                               default     = 1.0 ),

        'barY': FloatProperty( name        = "Bar Depth",
                               description = "Y-dimension length of bars.",
                               min         = 0.1,
                               max         = 100.0,
                               default     = 1.0 ),

        'barS': FloatProperty( name        = "Bar Spacing",
                               description = ( "Distance between common"
                                             + " points of two adjacent"
                                             + " bars." ),
                               min         = 0.0,
                               max         = 200.0,
                               default     = 1.5 )
    }

    # Add properties directly to the scene class.
    for key, prop in s.bcProps.items():
        setattr( s, key, prop )

    # Register the operator, panel, and menu UI.
    bpy.utils.register_class( MakeBarChart )
    bpy.utils.register_class( PrepareBarChart )
    bpy.types.INFO_MT_mesh_add.append( menu_func )


def unregister():
    """ Unregister the bar chart addon """

    # Unregister the operator, panel, and menu UI.
    bpy.utils.unregister_class( MakeBarChart )
    bpy.utils.unregister_class( PrepareBarChart )
    bpy.types.INFO_MT_mesh_add.remove( menu_func )


#---------------------------------------------------------------------
# Script entry point
#---------------------------------------------------------------------
if __name__ == "__main__":
    register()
