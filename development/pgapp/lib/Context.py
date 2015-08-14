"""
Intended to provide a consistent interface to a "root" rendering context.
This allows abstraction from an application-wide state manager to something
that can be more granular (e.g. multiple rendering areas within the same
program).
"""


#=============================================================================
class Context( object ):
    """
    Rendering context interface.
    """


    #=========================================================================
    @staticmethod
    def create_root( conf = None, styles = None ):
        """
        Creates a root context.

        @param conf   Application configuration dictionary
        @param styles Context rendering styles
        """

        # Create the root context instance.
        context = Context()

        # Define a minimally-functional configuration.
        context._conf = {
            'size'  : ( 640, 480 ),
            'depth' : 32
        }

        # Define basic styles.
        context._styles = {
            'foreground-color' : (  48,  48,  48 ),
            'background-color' : ( 200, 200, 200 ),
            'font-face'        : 'Courier New',
            'font-size'        : 16
        }

        # Add/modify additional configuration information.
        if conf is not None:
            context._conf.update( conf )

        # Add/modify additional style information.
        if styles is not None:
            context._styles.update( styles )

        # Return the generated context.
        return context


    #=========================================================================
    def __init__( self, context = None ):
        """
        Initializes a Context object.

        @param context The parent context
        """

        # Set the parent rendering context.
        self.parent = context


    #=========================================================================
    def __getattr__( self, key ):
        """
        Safely retrieves the correct attribute from the context.

        @param key The name of the attribute to retrieve
        @return    The requested attribute
        @throws    AttributeError if the attribute is not available
        """

        # Allow access to the configuration, styles, and target layer.
        if key in ( 'conf', 'styles' ):

            # The root context maintains the data.
            if self.parent is None:
                return getattr( self, ( '_' + key ) )

            # Not a root context, request parent's data.
            return getattr( self.parent, key )

        # Access not allowed to undefined attribute.
        raise AttributeError(
            "Context instance has no attribute '{}'".format( key )
        )


    #=========================================================================
    def create( self ):
        """
        Creates a descendant context.

        @return A new context that is a descendant of the current context
        """

        # Initialize a new context using the current object as its parent.
        return Context( self )

