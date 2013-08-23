#!/usr/bin/env python
##############################################################################
#
# css.py
#
# CSS document construction library.
#
##############################################################################


#=============================================================================
class styleset( dict ):
    """
    Extends the basic dictionary to format the key-value pairs into a valid
    CSS string representing the style rules.
    """

    #=========================================================================
    def __init__( self, *args, **kwargs ):
        """
        Initialize a styleset instance.
        Arguments are passed through to the dict constructor.
        """

        # call the parent constructor
        super( styleset, self ).__init__( *args, **kwargs )

        # define a custom value to use for indentation formatting
        self.indent = 1

    #=========================================================================
    def __str__( self ):
        """
        Convert the dictionary into a CSS string.
        """

        # set up a list of rules
        rules = []

        # iterate through the style set
        for ( style, value ) in self.items():

            # format the style string
            rules.append( '%s%s: %s;' % (
                ( '  ' * self.indent ),
                style,
                value
            ) )

        # return one style per line
        return '\n'.join( rules )


#=============================================================================
class document( dict ):
    """
    Extends the basic dictionary to model a CSS document.  Key-value pairs
    represent a selector and its set of style rules.
    """

    #=========================================================================
    def __init__( self, *args, **kwargs ):
        """
        Initialize a CSS document instance.
        Arguments are passed through to the dict constructor.
        """

        # call the parent constructor
        super( document, self ).__init__( *args, **kwargs )

        # define a custom value to specify that the CSS will be used inline
        self.inline = False

    #=========================================================================
    def __str__( self ):
        """
        Convert the dictionary into a CSS string.
        """

        # set up a list of document chunks
        chunks = []

        # when used inline, prepend CDATA open tag
        if self.inline == True:
            chunks.append( '<![CDATA[' )

        # iterate through the selectors
        for ( selector, styles ) in self.items():

            # auto-promote nested dicts to styleset instances
            if isinstance( styles, styleset ) == False:
                self[ selector ] = styles = styleset( styles )

            # format each selector and its styles
            chunks.append( '%s {\n%s\n}' % ( selector, str( styles ) ) )

        # when used inline, append CDATA close tag
        if self.inline == True:
            chunks.append( ']]>' )

        # return all chunks separated by a new line
        return '\n'.join( chunks )


#=============================================================================
def main( argv ):
    """ Script execution entry point """

    doc = document( {
        'selector'  : { 'style' : 'value' },
        'div#ident' : {
            'font-size' : '140%',
            'font-weight' : 'bold'
        }
    } )

    doc.inline = True

    print str( doc )

    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
