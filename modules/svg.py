#!/usr/bin/env python
##############################################################################
#
# svg.py
#
# SVG document construction (and some drawing) library.
#
# Note: I'm well aware (and a big fan) of using several of Python's built-in
# DOM modules.  I don't need that kind of horsepower for generating such
# simple string outputs.
#
##############################################################################


import re


#=============================================================================
def get_tag( name, attributes = {}, data = None ):
    """
    Shortcut interface to constructing an XML element that is only created for
    the sole purpose of building a formatted output string.
    @param name The element's tag name
    @param attributes Dictionary of element attributes
    @param data List of elements and/or strings to use as child nodes.
        If an element in the list is a string, it is treated as a text node
        in the child list.
        If this parameter is a string, it is treated as literal content of
        the tag.  An empty string produces an open/close tag pair.
        The default (None) or an empty list produces a self-closing tag with
        no child nodes.
    """

    # create an element instance
    elem = element( name, attributes, data )

    # convert it to a string and return it
    return str( elem )


#=============================================================================
def path2attr( path, precision = 2 ):
    """
    Convert a list of SVG path command lists to a string suitable for use in
    an XML attribute.
    @param path A list composed of lists that describe the commands used to
        render a path.  Each element of the top-level list must be a list that
        begins with a command character (e.g. 'M', 'l', 'z'), and is followed
        by an even number of path coordinate values (the exact number of of
        coordinate values depends on the command [e.g. 'M' needs two, 'z'
        needs zero, and 'q' needs four]).
    @param precision Maximum output precision of fractional numbers.  If a
        coordinate value is fractional, this limits the precision copied to
        the string.  It also tries to strip trailing zeros after the decimal
        point.  Therefore, even if you ask for a precision of 2, you might get
        a precision of 1 if the value ended in a zero (e.g. 1.20 => 1.2).
    """

    # list of path commands
    commands = []

    # loop through each specified command
    for command in path:

        # copy the command character to the beginning of this command string
        cmdstr = command[ 0 ]

        # copy each pair of path coordinate values to the command string
        for i in range( ( len( command ) - 1 ) / 2 ):
            cmdstr += ' ' + format_coord(
                command[ ( 2 * i ) + 1 ],
                command[ ( 2 * i ) + 2 ],
                precision
            )

        # add this command string to the list of commands
        commands.append( cmdstr )

    # return a string of all the commands separated by a single space
    return ' '.join( commands )


#=============================================================================
def format_coord( x, y, precision = 2 ):
    """
    Formats a coordinate pair for use in a path attribute string.
    @param x The horizontal coordinate (int or float)
    @param y The vertical coordinate (int or float)
    @param precision Maximum output precision of fractional numbers
    """

    # return a formatted coordinate pair string
    return '%s,%s' % (
        format_value( x, precision ),
        format_value( y, precision )
    )


#=============================================================================
def format_value( value, precision = 2 ):
    """
    Formats a single coordinate value according to its type and the best use
    of string memory/storage for the given value and precision requirements.
    @param value The value to format (int or float)
    @param precision Maximum output precision of fractional numbers
    """

    # check for float formatting
    if type( value ) is float:

        # strip trailing zeros in the fractional part
        return re.sub( r'(\.0+|0+)$', '', ( '%%0.%df' % precision ) % value )

    # int (or convertable to int) formatting
    return '%d' % int( value )


#=============================================================================
class element( object ):
    """
    Models an SVG/XML element.  Provides attribute and child node management
    interfaces.  Designed for easy conversion from object instance to string
    representation (just convert an object to a string).
    """

    #=========================================================================
    def __init__( self, name, attributes = {}, data = None ):
        """
        Initialize an element instance.
        @param name The element's tag name
        @param attributes Dictionary of element attributes
        @param data List of elements and/or strings to use as child nodes.
            If an element in the list is a string, it is treated as a text
            node in the child list.
            If this parameter is a string, it is treated as literal content of
            the tag.  An empty string produces an open/close tag pair.
            The default (None) or an empty list produces a self-closing tag
            with no child nodes.
        """

        # set/default element properties
        self.name       = name
        self.attributes = attributes
        self.data       = data if data is not None else []

    #=========================================================================
    def __str__( self ):
        """
        Convert an instance to a tag as a string.
        """

        # start of tag
        tag = '<%s' % self.name

        # attribute list (if given)
        for ( key, value ) in self.attributes.items():
            if value is not None:
                tag += ' %s="%s"' % ( key, str( value ) )

        # plain string descendents
        if type( self.data ) is str:
            tag += '>%s</%s>' % ( self.data, self.name )

        # list of child element descendents
        elif ( type( self.data ) is list ) and ( len( self.data ) > 0 ):
            tag += '>\n%s\n</%s>' % (
                '\n'.join( [ str( d ) for d in self.data ] ),
                self.name
            )

        # no descendents
        else:
            tag += '/>'

        # final string representing element
        return tag

    #=========================================================================
    def append_child( self, child ):
        """
        Append an element object as a child of the current object.
        @param child The child element to append
        """

        # if we are managing a list of children, append it to the list
        if type( self.data ) is list:
            self.data.append( child )

        # if we are managing string contents, append it to the string
        elif type( self.data ) is str:
            self.data += str( child )

        # ZIH - might want to toss an exception here
        #   but, it might not be the user's fault the node list went crazy

    #=========================================================================
    def set_attributes( self, attributes ):
        """
        Set/update all attributes using a dictionary of attributes.
        @param attributes Dictionary of attribute key/value pairs
        """

        # set/update each specified attribute in this element
        for ( key, value ) in attributes.items():
            self.attributes[ key ] = value


#=============================================================================
class path( element ):

    #=========================================================================
    def __init__( self, attributes ):
        if ( 'd' in attributes ) and ( type( attributes[ 'd' ] ) is list ):
            attributes[ 'd' ] = path2attr( attributes[ 'd' ] )
        super( path, self ).__init__( 'path', attributes )


#=============================================================================
class document( element ):

    #=========================================================================
    def __init__( self, width = 640, height = 480, title = None ):
        super( document, self ).__init__(
            'svg',
            {
                'xmlns'       : 'http://www.w3.org/2000/svg',
                'xmlns:xlink' : 'http://www.w3.org/1999/xlink',
                'version'     : '1.1',
                'width'       : width,
                'height'      : height,
                'viewBox'     : '0 0 %d %d' % ( width, height )
            },
            [
                element( 'title', data = title )
            ]
        )

    #=========================================================================
    def __str__( self ):
        return '<?xml version="1.0" encoding="utf-8"?>\n' \
            + super( document, self ).__str__()


#=============================================================================
def create_image( width = 640, height = 480, title = None, data = None ):
    doc = document( width, height, title )
    if type( data ) is list:
        for d in data:
            doc.append_child( d )
    elif data is not None:
        doc.append_child( data )
    return doc


#=============================================================================
def main( argv ):
    """ Script execution entry point """

    size   = 50
    r      = 10
    s      = size - ( 2 * r )
    half_s = s / 2

    paths = [
        path( {
            'd' : [
                [ 'M', r, 0 ],
                [ 'l', s, 0 ],
                [ 'q', r, 0, r, r ],
                [ 'l', 0, s ],
                [ 'q', 0, r, -r, r ],
                [ 'l', -s, 0 ],
                [ 'q', -r, 0, -r, -r ],
                [ 'l', 0, -s ],
                [ 'q', 0, -r, r, -r ],
                [ 'z' ]
            ]
        } ),
        path( {
            'd' : [
                [ 'M', r, 0 ],
                [ 'l', s, 0 ],
                [ 'q', r, 0, r, r ],
                [ 'l', 0, half_s ],
                [ 'l', -size, 0 ],
                [ 'l', 0, -half_s ],
                [ 'q', 0, -r, r, -r ],
                [ 'z' ]
            ]
        } ),
        path( {
            'd' : [
                [ 'M', 0, half_s ],
                [ 'l', size, 0 ],
                [ 'l', 0, half_s ],
                [ 'q', 0, r, -r, r ],
                [ 'l', -s, 0 ],
                [ 'q', -r, 0, -r, -r ],
                [ 'l', 0, -half_s ],
                [ 'z' ]
            ]
        } )
    ]

    if len( argv ) > 1:
        handle = open( argv[ 1 ], 'wb' )
    else:
        handle = sys.stdout

    handle.write( str( create_image( title = 'Test', data = paths ) ) )

    if len( argv ) > 1:
        handle.close()
        print 'SVG output written to %s.' % argv[ 1 ]

    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
