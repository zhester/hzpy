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
        'shift' : { 'type' : 'motion', 'text' : 'end' }
    },
    '5' : {
        'default' : { 'type' : 'extra' },
        'shift' : { 'type' : 'motion', 'text' : 'goto match' }
    },
    '6' : {
        'default' : { 'type' : 'extra' },
        'shift' : { 'type' : 'motion', 'text' : '"soft" home' }
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
        'default' : { 'type' : 'motion', 'text' : '"hard" home' },
        'shift' : { 'type' : 'motion', 'text' : 'end sentence' }
    },
    '-' : {
        'default' : { 'type' : 'motion', 'text' : 'prev line' },
        'shift' : { 'type' : 'motion', 'text' : '"soft" home down' }
    },
    '=' : {
        'default' : { 'type' : 'operator', 'text' : 'auto format' },
        'shift' : { 'type' : 'motion', 'text' : 'next line' }
    },

    #-- row 1 ----------------------------------------------------------------
    'q' : {
        'default' : { 'type' : 'command', 'text' : 'record macro' },
        'shift' : { 'type' : 'command', 'text' : 'ex mode' }
    },
    'w' : {
        'default' : { 'type' : 'motion', 'text' : 'next word' },
        'shift' : { 'type' : 'motion', 'text' : 'next WORD' }
    },
    'e' : {
        'default' : { 'type' : 'motion', 'text' : 'end word' },
        'shift' : { 'type' : 'motion', 'text' : 'end WORD' }
    },
    'r' : {
        'default' : { 'type' : 'command', 'text' : 'replace char' },
        'shift' : { 'type' : 'insert', 'text' : 'replace mode' }
    },
    't' : {
        'default' : { 'type' : 'motion', 'text' : '\'till' },
        'shift' : { 'type' : 'motion', 'text' : '\'till' }
    },
    'y' : {
        'default' : { 'type' : 'command', 'text' : 'yank' },
        'shift' : { 'type' : 'command', 'text' : 'yank line' }
    },
    'u' : {
        'default' : { 'type' : 'command', 'text' : 'undo' },
        'shift' : { 'type' : 'command', 'text' : 'undo line' }
    },
    'i' : {
        'default' : { 'type' : 'insert', 'text' : 'insert mode' },
        'shift' : { 'type' : 'insert', 'text' : 'insert (home)' }
    },
    'o' : {
        'default' : { 'type' : 'insert', 'text' : 'open below' },
        'shift' : { 'type' : 'insert', 'text' : 'open above' }
    },
    'p' : {
        'default' : { 'type' : 'command', 'text' : 'paste after' },
        'shift' : { 'type' : 'command', 'text' : 'paste before' }
    },
    '[' : {
        'default' : { 'type' : 'motion', 'text' : 'misc' },
        'shift' : { 'type' : 'motion', 'text' : 'begin para' }
    },
    ']' : {
        'default' : { 'type' : 'motion', 'text' : 'misc' },
        'shift' : { 'type' : 'motion', 'text' : 'end para' }
    },
    '\\' : {
        'default' : { 'type' : 'extra', 'text' : '(unused)' },
        'shift' : { 'type' : 'motion', 'text' : 'home' }
    },

    #-- row 2 ----------------------------------------------------------------
    'a' : {
        'default' : { 'type' : 'insert', 'text' : 'append' },
        'shift' : { 'type' : 'insert', 'text' : 'append (end)' }
    },
    's' : {
        'default' : { 'type' : 'command', 'text' : 'subst char' },
        'shift' : { 'type' : 'command', 'text' : 'subst line' }
    },
    'd' : {
        'default' : { 'type' : 'operator', 'text' : 'delete' },
        'shift' : { 'type' : 'command', 'text' : 'delete to end' }
    },
    'f' : {
        'default' : { 'type' : 'motion', 'text' : 'find char' },
        'shift' : { 'type' : 'motion', 'text' : 'find char' }
    },
    'g' : {
        'default' : { 'type' : 'extra', 'text' : 'extra' },
        'shift' : { 'type' : 'motion', 'text' : 'goto line' }
    },
    'h' : {
        'default' : { 'type' : 'motion', 'text' : 'left' },
        'shift' : { 'type' : 'motion', 'text' : 'screen top' }
    },
    'j' : {
        'default' : { 'type' : 'motion', 'text' : 'down' },
        'shift' : { 'type' : 'command', 'text' : 'join lines' }
    },
    'k' : {
        'default' : { 'type' : 'motion', 'text' : 'up' },
        'shift' : { 'type' : 'command', 'text' : 'help' }
    },
    'l' : {
        'default' : { 'type' : 'motion', 'text' : 'right' },
        'shift' : { 'type' : 'motion', 'text' : 'screen bottom' }
    },
    ';' : {
        'default' : { 'type' : 'motion', 'text' : 'repeat t/T/f/F' },
        'shift' : { 'type' : 'command', 'text' : 'command line' }
    },
    '\'' : {
        'default' : { 'type' : 'motion', 'text' : 'goto mark' },
        'shift' : { 'type' : 'extra', 'text' : 'register' }
    },

    #-- row 3 ----------------------------------------------------------------
    'z' : {
        'default' : { 'type' : 'extra', 'text' : 'extra' },
        'shift' : { 'type' : 'extra', 'text' : 'quit' }
    },
    'x' : {
        'default' : { 'type' : 'command', 'text' : 'delete' },
        'shift' : { 'type' : 'command', 'text' : 'delete' }
    },
    'c' : {
        'default' : { 'type' : 'operator', 'text' : 'change' },
        'shift' : { 'type' : 'command', 'text' : 'change (end)' }
    },
    'v' : {
        'default' : { 'type' : 'command', 'text' : 'visual mode' },
        'shift' : { 'type' : 'command', 'text' : 'visual lines' }
    },
    'b' : {
        'default' : { 'type' : 'motion', 'text' : 'prev word' },
        'shift' : { 'type' : 'motion', 'text' : 'prev WORD' }
    },
    'n' : {
        'default' : { 'type' : 'motion', 'text' : 'prev' },
        'shift' : { 'type' : 'motion', 'text' : 'next' }
    },
    'm' : {
        'default' : { 'type' : 'command', 'text' : 'set mark' },
        'shift' : { 'type' : 'motion', 'text' : 'screen mid' }
    },
    ',' : {
        'default' : { 'type' : 'motion', 'text' : 'reverse t/T/f/F' },
        'shift' : { 'type' : 'motion', 'operator' : 'unindent' }
    },
    '.' : {
        'default' : { 'type' : 'command', 'text' : 'repeat' },
        'shift' : { 'type' : 'operator', 'text' : 'indent' }
    },
    '/' : {
        'default' : { 'type' : 'motion', 'text' : 'find' },
        'shift' : { 'type' : 'motion', 'text' : 'find' }
    }

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

    kb = keyboard.keyboard( xscale = 80, yscale = 80 )

    for ( k, s ) in key_styles.items():
        kb.style[ k ] = s

    for ( key_id, info ) in _info.items():
        k = keyboard.create_key( key_id )
        k.flags |= keyboard.key.SHIFT
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
