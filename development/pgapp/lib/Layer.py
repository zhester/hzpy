"""
pygame Layer Base Model

Presents a unified interface for managing rendering layers.  A layer may be
used on its own, but is more typically used as the parent class for a more
specialized type of rendering layer.
"""


import pygame


#=============================================================================
class Layer( object ):
    """
    Models a rendering layer in the scene.
    """


    #=========================================================================
    def __init__( self, context, surface = None, **kwargs ):
        """
        Initializes a Layer object.

        @param context  The rendering context
        @param surface  Optional initial surface instance for rendering
        @param kwargs   Keyword arguments:
            rect        Override auto-created surface dimensions
            transparent Set to False to use context's background, otherwise
                        the layer is assumed to be transparent (True)
        """

        # Set the rendering context for configuration information.
        self.context = context

        # Check for transparent layer.
        self.transparent = kwargs.get( 'transparent', True )
        if self.transparent:
            self.fill = ( 0, 0, 0, 0 )
        else:
            self.fill = self.context.styles[ 'background-color' ]

        # Check for automatic surface creation.
        if surface is None:

            # Look for automatic surface dimension determination.
            if 'rect' not in kwargs:

                # Create the new surface to cover the current context.
                size = self.context.conf[ 'size' ]
                self.rect = pygame.Rect( ( 0, 0 ), size )

            # Use specified surface dimensions.
            else:
                self.rect = kwargs[ 'rect' ]

            # Create a new surface.
            self.surface = pygame.Surface(
                ( self.rect.w, self.rect.h ),
                flags = pygame.SRCALPHA,
                depth = self.context.conf[ 'depth' ]
            )

            # Initialize the surface.
            self.surface.fill( self.fill )

        # Use a given surface.
        else:
            self.surface = surface
            self.rect    = surface.get_rect()


    #=========================================================================
    def blit( self, surface ):
        """
        Blits this layer onto the given destination surface.  This saves the
        user from having to specify the source rectangle dimensions.

        @param surface The destination surface of the blit operation
        """

        # The destination surface will receive this surface's pixel data.
        surface.blit( self.surface, self.rect )

