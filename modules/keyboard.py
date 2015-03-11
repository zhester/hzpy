#!/usr/bin/env python
##############################################################################
#
# keyboard.py
#
# Draws keyboards using SVG and CSS for illustration/keymap purposes.
#
##############################################################################


import xml.sax.saxutils


import css
import svg


#=============================================================================

# Keys are identified by their virtual key code (not scan codes).  Keep in
# mind, we only need to identify a physical key here.  State-derived output
# that requires a combination of key presses is not enumerated.
# Note: Keys that duplicate the same function can have varying virtual key
# codes in different environments.  The ones to watch for are:
#   Right Shift:     rsft  (MS: VK_RSHIFT)
#   Right Control:   rctl  (MS: VK_RCONTROL)
#   Right Alternate: ralt  (MS: VK_RMENU)
#   Numpad Enter:    nent  (MS: Unassigned)
# I have assigned these to codes that probably won't work in your environment.
# They are only used here to uniquely identify the relavent parts of the image
# data.

_key_list = [

    # 0 to 63
    None,   None,   None,   None,   None,   None,   None,   None,   #   0
    'bksp', 'tab',  None,   None,   None,   'entr', None,   None,   #   8
    'shft', 'ctrl', 'alt',  'paus', 'caps', None,   None,   None,   #  16
    None,   None,   None,   'esc',  None,   None,   None,   None,   #  24
    'spc',  'pgup', 'pgdn', 'end',  'home', 'ltar', 'upar', 'rtar', #  32
    'dnar', None,   None,   None,   'prnt', 'ins',  'del',  None,   #  40
    '0',    '1',    '2',    '3',    '4',    '5',    '6',    '7',    #  48
    '8',    '9',    None,   None,   None,   '=',    None,   ';',    #  56

    # 64 to 127
    None,   'a',    'b',    'c',    'd',    'e',    'f',    'g',    #  64
    'h',    'i',    'j',    'k',    'l',    'm',    'n',    'o',    #  72
    'p',    'q',    'r',    's',    't',    'u',    'v',    'w',    #  80
    'x',    'y',    'z',    'lsys', 'rsys', 'apps', None,   None,   #  88
    'n0',   'n1',   'n2',   'n3',   'n4',   'n5',   'n6',   'n7',   #  96
    'n8',   'n9',   'n*',   'n+',   None,   'n-',   'n.',   'n/',   # 104
    'f1',   'f2',   'f3',   'f4',   'f5',   'f6',   'f7',   'f8',   # 112
    'f9',   'f10',  'f11',  'f12',  None,   None,   None,   None,   # 120

    # 128 to 191
    None,   None,   None,   None,   None,   None,   None,   None,   # 128
    None,   None,   None,   None,   None,   None,   None,   None,   # 136
    'nmlk', 'sclk', None,   None,   None,   None,   None,   None,   # 144
    None,   None,   None,   None,   None,   None,   None,   None,   # 152
    None,   'rsft', None,   'rctl', None,   'ralt', None,   None,   # 160
    None,   None,   None,   None,   None,   '-',    None,   None,   # 168
    None,   None,   None,   None,   None,   None,   None,   None,   # 176
    None,   None,   None,   None,   ',',    None,   '.',    '/',    # 184

    # 192 to 255
    '`',    None,   None,   None,   None,   None,   None,   None,   # 192
    None,   None,   None,   None,   None,   None,   None,   None,   # 200
    None,   None,   None,   None,   None,   None,   None,   None,   # 208
    None,   None,   None,   '[',    '\\',   ']',    "'",    None,   # 216
    None,   None,   None,   None,   None,   None,   None,   None,   # 224
    'nent', None,   None,   None,   None,   None,   None,   None,   # 232
    None,   None,   None,   None,   None,   None,   None,   None,   # 240
    None,   None,   None,   None,   None,   None,   None,   None    # 248
]


#=============================================================================

# complete list of key shapes on a standard keyboard
# indexes into this list are used in the _key_data table
# this is a list of tuples where each tuple is ( width, height )

_key_shapes = [
    ( 1.00, 1.00 ), # 0
    ( 1.25, 1.00 ), # 1
    ( 1.50, 1.00 ), # 2
    ( 1.75, 1.00 ), # 3
    ( 2.00, 1.00 ), # 4
    ( 2.25, 1.00 ), # 5
    ( 2.75, 1.00 ), # 6
    ( 6.25, 1.00 ), # 7
    ( 1.00, 2.00 )  # 8
]

# display each row at the following key unit offsets
# indexes into this list are used in the _key_data table

_row_offsets = [
    0.00,
    1.50,
    2.50,
    3.50,
    4.50,
    5.50
]


#=============================================================================

# index lookup table of columns in key data table below

_key_data_keys = {
    'code'   : 0,                   # virtual key code
    'name'   : 1,                   # human-friendly name
    'label'  : 2,                   # default display label
    'shift'  : 3,                   # shift state display label
    'offset' : 4,                   # horizontal offset in row
    'row'    : 5,                   # row index (0 to 5)
    'shape'  : 6                    # shape index (0 to 8)
}

# table of descriptive information about the ISO standard US keyboard
# Assumptions:
#   - Most keys are "unit" keys (1.0 units by 1.0 units).
#   - Keys that are different sizes are multiples of the unit keys.
#   - A keyboard has 6, vertically-aligned rows.
#   - Vendor-specific keys are avoided (except the ubiquitous "win" keys).
#   - The dimensions do not account for ergonomic features.
#   - Enter keys are NEVER backwards-L-shaped.

_key_data = {

    'bksp' : [   8, 'Backspace',    'Bksp',  None,   13.00, 1, 4 ],
    'tab'  : [   9, 'Tab',          'Tab',   'LTab',  0.00, 2, 2 ],
    'entr' : [  13, 'Enter',        'Enter', None,   12.75, 3, 5 ],
    'shft' : [  16, 'Shift',        'Shift', None,    0.00, 4, 5 ],
    'ctrl' : [  17, 'Control',      'Ctrl',  None,    0.00, 5, 1 ],
    'alt'  : [  18, 'Alternate',    'Alt',   None,    2.50, 5, 1 ],
    'paus' : [  19, 'Pause/Break',  'Pause', None,   22.00, 0    ],
    'caps' : [  20, 'Caps Lock',    'Caps',  None,    0.00, 3, 3 ],
    'esc'  : [  27, 'Escape',       'Esc',   None,    0.00, 0    ],
    'spc'  : [  32, 'Space',        'Space', None,    3.75, 5, 7 ],
    'pgup' : [  33, 'Page Up',      'PgUp',  None,   17.50, 1    ],
    'pgdn' : [  34, 'Page Down',    'PgDn',  None,   17.50, 2    ],
    'end'  : [  35, 'End',          'End',   None,   16.50, 2    ],
    'home' : [  36, 'Home',         'Home',  None,   16.50, 1    ],
    'ltar' : [  37, 'Left Arrow',   'Left',  None,   15.50, 5    ],
    'upar' : [  38, 'Up Arrow',     'Up',    None,   16.50, 4    ],
    'rtar' : [  39, 'Right Arrow',  'Right', None,   17.50, 5    ],
    'dnar' : [  40, 'Down Arrow',   'Down',  None,   16.50, 5    ],
    'prnt' : [  44, 'Print Screen', 'Print', None,   20.00, 0    ],
    'ins'  : [  45, 'Insert',       'Ins',   None,   15.50, 1    ],
    'del'  : [  46, 'Delete',       'Del',   None,   15.50, 2    ],

    '0'    : [  48, '0', '0', ')', 10.00, 1 ],
    '1'    : [  49, '1', '1', '!',  1.00, 1 ],
    '2'    : [  50, '2', '2', '@',  2.00, 1 ],
    '3'    : [  51, '3', '3', '#',  3.00, 1 ],
    '4'    : [  52, '4', '4', '$',  4.00, 1 ],
    '5'    : [  53, '5', '5', '%',  5.00, 1 ],
    '6'    : [  54, '6', '6', '^',  6.00, 1 ],
    '7'    : [  55, '7', '7', '&',  7.00, 1 ],
    '8'    : [  56, '8', '8', '*',  8.00, 1 ],
    '9'    : [  57, '9', '9', '(',  9.00, 1 ],

    '='    : [  61, '=', '=', '+', 12.00, 1 ],
    ';'    : [  63, ';', ';', ':', 10.75, 3 ],

    'a'    : [  65, 'a', 'a', 'A',  1.75, 3 ],
    'b'    : [  66, 'b', 'b', 'B',  6.25, 4 ],
    'c'    : [  67, 'c', 'c', 'C',  4.25, 4 ],
    'd'    : [  68, 'd', 'd', 'D',  3.75, 3 ],
    'e'    : [  69, 'e', 'e', 'E',  3.50, 2 ],
    'f'    : [  70, 'f', 'f', 'F',  4.75, 3 ],
    'g'    : [  71, 'g', 'g', 'G',  5.75, 3 ],
    'h'    : [  72, 'h', 'h', 'H',  6.75, 3 ],
    'i'    : [  73, 'i', 'i', 'I',  8.50, 2 ],
    'j'    : [  74, 'j', 'j', 'J',  7.75, 3 ],
    'k'    : [  75, 'k', 'k', 'K',  8.75, 3 ],
    'l'    : [  76, 'l', 'l', 'L',  9.75, 3 ],
    'm'    : [  77, 'm', 'm', 'M',  8.25, 4 ],
    'n'    : [  78, 'n', 'n', 'N',  7.25, 4 ],
    'o'    : [  79, 'o', 'o', 'O',  9.50, 2 ],
    'p'    : [  80, 'p', 'p', 'P', 10.50, 2 ],
    'q'    : [  81, 'q', 'q', 'Q',  1.50, 2 ],
    'r'    : [  82, 'r', 'r', 'R',  4.50, 2 ],
    's'    : [  83, 's', 's', 'S',  2.75, 3 ],
    't'    : [  84, 't', 't', 'T',  5.50, 2 ],
    'u'    : [  85, 'u', 'u', 'U',  7.50, 2 ],
    'v'    : [  86, 'v', 'v', 'V',  5.25, 4 ],
    'w'    : [  87, 'w', 'w', 'W',  2.50, 2 ],
    'x'    : [  88, 'x', 'x', 'X',  3.25, 4 ],
    'y'    : [  89, 'y', 'y', 'Y',  6.50, 2 ],
    'z'    : [  90, 'z', 'z', 'Z',  2.25, 4 ],

    'lsys' : [  91, 'Left System',  'Sys',  None,  1.25, 5, 1 ],
    'rsys' : [  92, 'Right System', 'Sys',  None, 11.24, 5, 1 ],
    'apps' : [  93, 'Applications', 'Apps', None, 12.50, 5, 1 ],

    'n0'   : [  96, 'Numpad 0', '0', 'Ins',   19.00, 5, 4 ],
    'n1'   : [  97, 'Numpad 1', '1', 'End',   19.00, 4    ],
    'n2'   : [  98, 'Numpad 2', '2', 'Down',  20.00, 4    ],
    'n3'   : [  99, 'Numpad 3', '3', 'PgDn',  21.00, 4    ],
    'n4'   : [ 100, 'Numpad 4', '4', 'Left',  19.00, 3    ],
    'n5'   : [ 101, 'Numpad 5', '5', None,    20.00, 3    ],
    'n6'   : [ 102, 'Numpad 6', '6', 'Right', 21.00, 3    ],
    'n7'   : [ 103, 'Numpad 7', '7', 'Home',  19.00, 2    ],
    'n8'   : [ 104, 'Numpad 8', '8', 'Up',    20.00, 2    ],
    'n9'   : [ 105, 'Numpad 9', '9', 'PgUp',  21.00, 2    ],
    'n*'   : [ 106, 'Numpad *', '*', None,    21.00, 1    ],
    'n+'   : [ 107, 'Numpad +', '+', None,    22.00, 2, 8 ],
    'n-'   : [ 109, 'Numpad -', '-', None,    22.00, 1    ],
    'n.'   : [ 110, 'Numpad .', '.', None,    21.00, 5    ],
    'n/'   : [ 111, 'Numpad /', '/', None,    20.00, 1    ],

    'f1'   : [ 112, 'F1',  'F1',  None,  2.00, 0 ],
    'f2'   : [ 113, 'F2',  'F2',  None,  3.00, 0 ],
    'f3'   : [ 114, 'F3',  'F3',  None,  4.00, 0 ],
    'f4'   : [ 115, 'F4',  'F4',  None,  5.00, 0 ],
    'f5'   : [ 116, 'F5',  'F5',  None,  6.50, 0 ],
    'f6'   : [ 117, 'F6',  'F6',  None,  7.50, 0 ],
    'f7'   : [ 118, 'F7',  'F7',  None,  8.50, 0 ],
    'f8'   : [ 119, 'F8',  'F8',  None,  9.50, 0 ],
    'f9'   : [ 120, 'F9',  'F9',  None, 11.00, 0 ],
    'f10'  : [ 121, 'F10', 'F10', None, 12.00, 0 ],
    'f11'  : [ 122, 'F11', 'F11', None, 13.00, 0 ],
    'f12'  : [ 123, 'F12', 'F12', None, 14.00, 0 ],

    'nmlk' : [ 144, 'Num Lock',        'Num',    None, 19.00, 1    ],
    'sclk' : [ 145, 'Scroll Lock',     'Scroll', None, 21.00, 0    ],
    'rsft' : [ 161, 'Right Shift',     'Shift',  None, 12.25, 4, 6 ],
    'rctl' : [ 163, 'Right Control',   'Ctrl',   None, 13.75, 5, 1 ],
    'ralt' : [ 165, 'Right Alternate', 'Alt',    None, 10.00, 5, 1 ],

    '-'    : [ 173, '-',  '-',  '_', 11.00, 1    ],
    ','    : [ 188, ',',  ',',  '<',  9.25, 4    ],
    '.'    : [ 190, '.',  '.',  '>', 10.25, 4    ],
    '/'    : [ 191, '/',  '/',  '?', 11.25, 4    ],
    '`'    : [ 192, '`',  '`',  '~',  0.00, 1    ],
    '['    : [ 219, '[',  '[',  '{', 11.50, 2    ],
    '\\'   : [ 220, '\\', '\\', '|', 13.50, 2, 2 ],
    ']'    : [ 221, ']',  ']',  '}', 12.50, 2    ],
    "'"    : [ 223, "'",  "'",  '"', 11.75, 3    ],

    'nent' : [ 232, 'Numpad Enter', 'Enter', None, 22.00, 4, 8 ]
}



#=============================================================================
def _make_key_paths( width = 50, height = 50, radius = 4 ):

    w  = float( width )             # bounding-box horizontal dimension
    wh = w / 2.0                    # half of that dimension

    h  = float( height )            # bounding-box vertical dimension
    hh = h / 2.0                    # half of that dimension

    r  = float( radius )            # corner radius
    b  = r / 2.0                    # apparent border
    bh = b / 2.0                    # half of that dimension

    xd  = w - ( 2.0 * r )           # horizontal dimension between radii
    xdh = xd / 2.0                  # half of that dimension
    yd  = h - ( 2.0 * r )           # vertical dimension between radii
    ydh = yd / 2.0                  # half of that dimension

    return [
        svg.path( {
            'd' : [
                [ 'M', r, 0 ],
                [ 'l', xd, 0 ],
                [ 'q', r, 0, r, r ],
                [ 'l', 0, yd ],
                [ 'q', 0, r, -r, r ],
                [ 'l', -xd, 0 ],
                [ 'q', -r, 0, -r, -r ],
                [ 'l', 0, -yd ],
                [ 'q', 0, -r, r, -r ],
                [ 'z' ]
            ],
            'class' : 'key_back'
        } ),
        svg.path( {
            'd' : [
                [ 'M', r, b ],
                [ 'l', xd, 0 ],
                [ 'q', b, 0, b, b ],
                [ 'l', 0, ydh ],
                [ 'l', -( w - r ), 0 ],
                [ 'l', 0, -ydh ],
                [ 'q', 0, -b, b, -b ],
                [ 'z' ]
            ],
            'class' : 'key_top'
        } ),
        svg.path( {
            'd' : [
                [ 'M', b, hh ],
                [ 'l', ( w - r ), 0 ],
                [ 'l', 0, ydh ],
                [ 'q', 0, b, -b, b ],
                [ 'l', -xd, 0 ],
                [ 'q', -b, 0, -b, -b ],
                [ 'l', 0, -ydh ],
                [ 'z' ]
            ],
            'class' : 'key_bottom'
        } )
    ]


#=============================================================================
def create_key( key_id ):
    """
    Convenience function to create any key in the local key data table.
    @param key_id The key's unique string ID
    """
    return key( *_key_data[ key_id ] )


#=============================================================================
class key( dict ):


    #=========================================================================
    LABEL = 1
    SHIFT = 2


    #=========================================================================
    def __init__(
        self,
        code   = 0,                 # virtual key code
        name   = 'UNK',             # human-friendly name
        label  = None,              # default display label
        shift  = None,              # shift state display label
        offset = 0.0,               # horizontal offset in row
        row    = 0,                 # row index (0 to 5)
        shape  = 0                  # shape index (0 to 8)
    ):
        arguments   = locals()
        self.flags  = key.LABEL
        self.labels = []
        for ( k, v ) in arguments.items():
            self[ k ] = v
        self.attributes = {}


    #=========================================================================
    def __str__( self ):
        return str( self.create_svg() )


    #=========================================================================
    def add_label( self, x, y, text ):
        self.labels.append( locals() )


    #=========================================================================
    def create_svg( self, xscale = 42.0, yscale = 42.0, radius = 4 ):

        # determine position in the layout
        xpos = self[ 'offset' ] * xscale
        ypos = _row_offsets[ self[ 'row' ] ] * yscale

        # set the transform attribute for the group to position the key
        self.attributes[ 'transform' ] = \
            'translate(%s)' % svg.format_coord( xpos, ypos )

        # create a group to display the key
        group = svg.element( 'g', self.attributes )

        # create a use element to "clone" the appropriate shape
        group.append_child(
            svg.element(
                'use',
                { 'xlink:href' : ( '#key_%d' % self[ 'shape' ] ) }
            )
        )

        # create a sub-group to contain/limit descendents
        subgroup = svg.element(
            'g',
            { 'clip-path' : ( 'url(#clip_%d)' % self[ 'shape' ] ) }
        )

        # find the height of this key
        height = _key_shapes[ self[ 'shape' ] ][ 1 ] * yscale

        # determine text baseline position values
        edge  = radius / 2.0
        xpad  = svg.format_value( edge + 1 )
        y0pad = svg.format_value( height - ( edge + 2 ) )
        y1pad = svg.format_value( ( height / 2.0 ) - ( edge + 1 ) )

        # see if the user wants to see the default label
        if ( self.flags & key.LABEL ) == key.LABEL:

            # create and position the key label
            subgroup.append_child(
                svg.element(
                    'text',
                    { 'x' : xpad, 'y' : y0pad },
                    xml.sax.saxutils.escape( self[ 'label' ] )
                )
            )

        # see if the user wants to see the shift label (if it exists)
        if ( self[ 'shift' ] is not None ) \
            and ( ( self.flags & key.SHIFT ) == key.SHIFT ):

            # create and position the shift label
            subgroup.append_child(
                svg.element(
                    'text',
                    { 'x' : xpad, 'y' : y1pad },
                    xml.sax.saxutils.escape( self[ 'shift' ] )
                )
            )

        # display any other labels
        for label in self.labels:

            # create and position this label
            subgroup.append_child(
                svg.element(
                    'text',
                    {
                        'x' : svg.format_value( label[ 'x' ] ),
                        'y' : svg.format_value( label[ 'y' ] )
                    },
                    xml.sax.saxutils.escape( label[ 'text' ] )
                )
            )

        # append the container group
        group.append_child( subgroup )

        # return the group element
        return group


    #=========================================================================
    def set_attributes( self, attributes ):
        for ( k, v ) in attributes.items():
            self.attributes[ k ] = v


#=============================================================================
class keyboard( object ):


    #=========================================================================
    _unit_columns = 23.0


    #=========================================================================
    def __init__(
        self,
        xscale   = 42.0,
        yscale   = 42.0,
        radius   = 4
    ):
        self.xscale = xscale
        self.yscale = yscale
        self.radius = radius
        self.keys   = []
        self.style  = self._create_style()


    #=========================================================================
    def __str__( self ):
        return str( self.create_svg() )


    #=========================================================================
    def add_key( self, k ):
        self.keys.append( k )


    #=========================================================================
    def create_svg( self, title = 'keyboard' ):

        width  = self.xscale * keyboard._unit_columns
        height = self.yscale * ( _row_offsets[ -1 ] + 1.0 )

        image = svg.create_image( width, height, title )

        image.append_child(
            svg.element(
                'link',
                {
                    'rel' : 'icon', 'href' : '#key_0',
                    'xmlns' : 'http://www.w3.org/1999/xhtml'
                }
            )
        )

        image.append_child(
            svg.element( 'style', { 'type' : 'text/css' }, str( self.style ) )
        )

        image.append_child( self._create_key_shapes() )

        image.append_child( self._create_clip_paths() )

        image.append_child( self._create_layout() )

        return image


    #=========================================================================
    def load_keys( self ):

        # iterate through all the keys
        for ( name, record ) in _key_data.items():

            # create the requested key
            k = key( *record )

            # convenience method does this by default
            k.flags |= key.SHIFT

            # add to list of keys
            self.add_key( k )


    #=========================================================================
    def _create_clip_paths( self ):
        paths = svg.element( 'g', { 'class' : 'clip_paths' } )

        key_edge = self.radius / 2
        edge = svg.format_value( key_edge )

        for ( index, shape ) in enumerate( _key_shapes ):
            key_width  = self.xscale * shape[ 0 ]
            key_height = self.yscale * shape[ 1 ]
            width  = svg.format_value( key_width  - ( 2 * key_edge ) )
            height = svg.format_value( key_height - ( 2 * key_edge ) )
            paths.append_child(
                svg.element(
                    'clipPath',
                    { 'id' : ( 'clip_%d' % index ) },
                    [
                        # ZIH - messy since it depends on _make_key_paths()
                        svg.element(
                            'rect',
                            {
                                'x'      : edge,
                                'y'      : edge,
                                'rx'     : edge,
                                'ry'     : edge,
                                'width'  : width,
                                'height' : height
                            }
                        )
                    ]
                )
            )

        return paths


    #=========================================================================
    def _create_key_shapes( self ):

        shapes = svg.element( 'g', { 'class' : 'key_shapes' } )

        for ( index, shape ) in enumerate( _key_shapes ):
            shapes.append_child(
                svg.element(
                    'g',
                    {
                        'id' : ( 'key_%d' % index )
                    },
                    _make_key_paths(
                        ( shape[ 0 ] * self.xscale ),
                        ( shape[ 1 ] * self.yscale ),
                        self.radius
                    )
                )
            )

        return shapes


    #=========================================================================
    def _create_layout( self ):

        # generate a group of key display groups
        keyboard = svg.element( 'g', { 'class' : 'layout' } )

        # iterate through each key requested for rendering
        for k in self.keys:

            # add its SVG representation to the layout
            keyboard.append_child(
                k.create_svg( self.xscale, self.yscale, self.radius )
            )

        # return the constructed layout
        return keyboard


    #=========================================================================
    def _create_style( self ):
        style = css.document( {
            'text' : {
                'fill'        : '#333333',
                'font-size'   : '12px',
                'font-family' : 'Arial,Sans,sans-serif'
            },
            '.key_shapes' : {
                'display' : 'none'
            },
            '.key_back' : {
                'fill'   : '#BBBBBB',
                'stroke' : 'none'
            },
            '.key_top' : {
                'fill' : '#E8E8E8',
                'stroke' : 'none'
            },
            '.key_bottom' : {
                'fill' : '#EFEFEF',
                'stroke' : 'none'
            }
        } )
        style.inline = True
        return style


#=============================================================================
def main( argv ):
    """ Script execution entry point """

    # create a keyboard object
    kb = keyboard()

    # load all the keys
    kb.load_keys()

    # write it to a file
    handle = open( 'keyboard.svg', 'wb' )
    handle.write( str( kb ) )
    handle.close()

    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
