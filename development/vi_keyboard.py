#!/usr/bin/env python
##############################################################################
#
# vi_keyboard.py
#
# Sometimes it's easier to draw in code.
#
##############################################################################


import sys
sys.path.append( '../modules' )


import keyboard


#=============================================================================

# information needed for the vi keyboard

_info = {

    #-- row 0 ----------------------------------------------------------------
    'esc' : {
        'default' : { 'type' : 'command', 'text' : 'normal mode' }
    },
    '`' : {
        'default' : { 'type' : 'motion', 'text' : 'goto mark' },
        'shift' : { 'type' : 'command', 'text' : 'toggle case' }
    },
    '1' : {
        'default' : { 'type' : 'extra' },
        'shift' : { 'type' : 'operator', 'text' : 'external filter' }
    },
    '2' : {
        'default' : { 'type' : 'extra' },
        'shift' : { 'type' : 'command', 'text' : 'play macro' }
    },
    '3' : {
        'default' : { 'type' : 'extra' },
        'shift' : { 'type' : 'motion', 'text' : 'prev ident' }
    },
    '4' : {
        'default' : { 'type' : 'extra' },
        'shift' : { 'type' : 'motion', 'text' : 'eol' }
    },
    '5' : {
        'default' : { 'type' : 'extra' },
        'shift' : { 'type' : 'motion', 'text' : 'goto match' }
    },
    '6' : {
        'default' : { 'type' : 'extra' },
        'shift' : { 'type' : 'motion', 'text' : '"soft" bol' }
    },
    '7' : {
        'default' : { 'type' : 'extra' },
        'shift' : { 'type' : 'command', 'text' : 'repeat :s' }
    },
    '8' : {
        'default' : { 'type' : 'extra' },
        'shift' : { 'type' : 'motion', 'text' : 'next ident' }
    },
    '9' : {
        'default' : { 'type' : 'extra' },
        'shift' : { 'type' : 'motion', 'text' : 'begin sentence' }
    },
    '0' : {
        'default' : { 'type' : 'motion', 'text' : '"hard" bol' },
        'shift' : { 'type' : 'motion', 'text' : 'end sentence' }
    },
    '-' : {
        'default' : { 'type' : 'motion', 'text' : 'prev line' },
        'shift' : { 'type' : 'motion', 'text' : '"soft" bol down' }
    },
    '=' : {
        'default' : { 'type' : 'operator', 'text' : 'auto format' },
        'shift' : { 'type' : 'motion', 'text' : 'next line' }
    }

    #-- row 1 ----------------------------------------------------------------

    #-- row 2 ----------------------------------------------------------------

    #-- row 3 ----------------------------------------------------------------

    #-- row 4 ----------------------------------------------------------------

    #-- row 5 ----------------------------------------------------------------

}


#=============================================================================
def main( argv ):
    """ Script execution entry point """

    handle = open( 'keyboard.svg', 'wb' )

    key_styles = {
        '.k_motion' : {
            'fill' : '#78AC66',
            'fill-opacity' : '0.5'
        },
        '.k_command' : {
            'fill' : '#66A3AC',
            'fill-opacity' : '0.5'
        },
        '.k_insert' : {
            'fill' : '#E3972F',
            'fill-opacity' : '0.5'
        },
        '.k_operation' : {
            'fill' : '#B968EB',
            'fill-opacity' : '0.5'
        },
        '.k_extra' : {
            'fill' : '#D6D6D6',
            'fill-opacity' : '0.5'
        },
        '.k_test .key_top' : {
            'fill' : '#FF0000'
        }
    }

    kb = keyboard.keyboard( xscale = 80, yscale = 40 )

    for ( k, s ) in key_styles.items():
        kb.style[ k ] = s

    for ( key_id, info ) in _info.items():
        k = keyboard.create_key( key_id )
        if ( 'default' in info ) and ( 'text' in info[ 'default' ] ):
            k.add_label( 30, 33, info[ 'default' ][ 'text' ] )
        if ( 'shift' in info ) and ( 'text' in info[ 'shift' ] ):
            k.add_label( 30, 15, info[ 'shift' ][ 'text' ] )
        #k.set_attributes( { 'class' : 'k_test' } )
        kb.add_key( k )

    # ZIH - not set on how styling each part of each key works
    #  there will be lots of CSS rules this way
    ## -> will have to have a deeper method to set the class on each part
    #  of the key (top and bottom)

    # ZIH - text elements for additional labels should have their own
    #  class for easier selection in style sheet
    ## -> should also have a method to automatically position two additional
    #  labels (top and bottom) without specifying coordinates

    # ZIH - the image is drawn as if all 23 unit columns are always required
    ## -> the keyboard module should detect the number of columns in the keys
    #  list, and grow the image as it is adding key elements

    handle.write( str( kb ) )

    handle.close()

    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    sys.exit( main( sys.argv ) )
