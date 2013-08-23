#*******************************************************************************
# scripting.py
#
# Zac Hester <zac.hester@gmail.com>
# 2012-07-19
#
# Blender addon development template.
#
#*******************************************************************************

bl_info = {
    'name'        : 'Addon Template',
    'author'      : 'Zac Hester',
    'version'     : ( 0, 0 ),
    'blender'     : ( 2, 6, 3 ),
    'location'    : 'Add > Mesh',
    'description' : 'Creates a mesh, and adds it to the scene as an object.',
    'warning'     : '',
    'wiki_url'    : '',
    'tracker_url' : '',
    'category'    : 'Add Mesh'
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

#-------------------------------------------------------------------------------
#                                   CLASSES
#-------------------------------------------------------------------------------


class PropertyPanel( bpy.types.Panel ):
    """ Adjust properties at the scene level """

    # Blender panel properties
    bl_label       = "Example Property Panel"
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "scene"


    def draw( self, context ):
        """ Draw the panel """

        # Set shortcuts to the layout and scene.
        t = self.layout
        s = context.scene

        # Add property controls to the panel.
        for key in s.userProperties.keys():
            t.prop( s, key )

        # Add a button to use the operator.
        t.operator( "example.add" )



class AddMeshOperator( bpy.types.Operator ):
    """ Create a mesh as an object in the scene """

    # Blender operator properties
    bl_idname = "example.add"
    bl_label  = "Add Example Mesh"

    # Properties used for operator transforms.
    view_align = BoolProperty( name    = "Align to View",
                               default = False )
    location   = FloatVectorProperty( name    = "Location",
                                      subtype = "TRANSLATION" )
    rotation   = FloatVectorProperty( name    = "Rotation",
                                      subtype = "EULER" )


    def addMesh( self, context ):
        """ Add the example mesh """

        # Set a shortcut to the scene.
        s = context.scene

        # Create the mesh data.
        bm = self.createMesh( s.propX, s.propY, s.propZ )

        # Create the mesh instance.
        mesh = bpy.data.meshes.new( "Example Mesh" )

        # Import mesh data into mesh instance.
        bm.to_mesh( mesh )
        mesh.update()

        # Add the mesh to the scene as an object.
        self.addObject( context, mesh )


    def addObject( self, context, mesh ):
        """ Add a mesh to the scene as an object """

        # Use the object utilities method to add the object.
        object_utils.object_data_add( context, mesh, operator = self )


    def createMesh( self, w, h, d ):
        """ Separate mesh generation from operator logic """

        # Create a blender mesh.
        b = bmesh.new()

        # Add the bottom vertices, and the face.
        b.verts.new( ( 0, 0, 0 ) )
        b.verts.new( ( w, 0, 0 ) )
        b.verts.new( ( w, d, 0 ) )
        b.verts.new( ( 0, d, 0 ) )
        b.faces.new( [ b.verts[ i ] for i in range( 0, 4 ) ] )

        # Add the top vertices, and the face.
        b.verts.new( ( 0, 0, h ) )
        b.verts.new( ( w, 0, h ) )
        b.verts.new( ( w, d, h ) )
        b.verts.new( ( 0, d, h ) )
        b.faces.new( [ b.verts[ i ] for i in range( 4, 8 ) ] )

        # Add the side faces.
        b.faces.new( [ b.verts[ i ] for i in [ 0, 1, 5, 4 ] ] )
        b.faces.new( [ b.verts[ i ] for i in [ 1, 2, 6, 5 ] ] )
        b.faces.new( [ b.verts[ i ] for i in [ 2, 3, 7, 6 ] ] )
        b.faces.new( [ b.verts[ i ] for i in [ 3, 0, 4, 7 ] ] )

        # Return the constructed mesh.
        return b


    def execute( self, context ):
        """ Run the operator """

        # Set a shortcut to the scene.
        s = context.scene

        # Add the mesh.
        self.addMesh( context )

        # Inform the caller the operator finished successfully.
        return { 'FINISHED' }


#-------------------------------------------------------------------------------
#                                  FUNCTIONS
#-------------------------------------------------------------------------------


def main()
    """ Script development entry point """

    # Unregister the previous version of the addon.
    unregister()

    # Register the new version of the addon.
    register()


def menu_func( menu, context ):
    """ Addon menu function """

    # Show the operator in the menu.
    menu.layout.operator( AddMeshOperator.bl_idname, icon = 'MESH_CUBE' )


def register():
    """ Register the bar chart addon """

    # Assign a shortcut to the scene class.
    s = bpy.types.Scene

    # Create a dictionary of user-definable properties.
    s.userProperties = {
        'propX': FloatProperty( name        = "Property X",
                                description = "X-dimension property.",
                                min         = 0.1,
                                max         = 100.0,
                                default     = 1.0 ),
        'propY': FloatProperty( name        = "Property Y",
                                description = "Y-dimension property.",
                                min         = 0.1,
                                max         = 100.0,
                                default     = 1.0 ),
        'propZ': FloatProperty( name        = "Property Z",
                                description = "Z-dimension property.",
                                min         = 0.1,
                                max         = 100.0,
                                default     = 1.0 )
    }

    # Add properties directly to the scene class.
    for key, prop in s.userProperties.items():
        setattr( s, key, prop )

    # Register the operator and panel.
    bpy.utils.register_class( PropertyPanel )
    bpy.utils.register_class( AddMeshOperator )
    bpy.types.INFO_MT_mesh_add.append( menu_func )


def unregister():
    """ Unregister the bar chart addon """

    # Unregister the operator and panel.
    bpy.utils.unregister_class( PropertyPanel )
    bpy.utils.unregister_class( AddMeshOperator )
    bpy.types.INFO_MT_mesh_add.remove( menu_func )


#-------------------------------------------------------------------------------
#                                  PROCEDURE
#-------------------------------------------------------------------------------

if __name__ == "__main__":

    # If executed directly, attempt to run from the main entry point.
    main()
