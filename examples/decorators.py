#!/usr/bin/env python


"""
Example of Decorator Usage
"""


__version__ = '0.0.0'


#=============================================================================
def basic_wrapper( function ):
    """
    Simple decorating wrapper function.
    """

    #=========================================================================
    def callback( context ):
        """
        The callback function with a single call-time context argument.
        """
        return '<tag>{}</tag>'.format( function( context ) )
    return callback


#=============================================================================
@basic_wrapper
def plain_text( argument ):
    """
    Example of a function that attempts to convert anything to a string.
    """
    return str( argument )


#=============================================================================
class class_wrapper( object ):
    """
    Using a class method as a wrapper.
    """

    #=========================================================================
    @classmethod
    def wrap( cls, function ):
        def callback( context ):
            return '<class>{}</class>'.format( function( context ) )
        return callback


#=============================================================================
@class_wrapper.wrap
def plain_text_two( argument ):
    return '`{}`'.format( argument )


#=============================================================================
class registration( object ):
    """
    Interface registration example.
    """
    #=========================================================================
    def __init__( self ):
        self.handlers = {}

    #=========================================================================
    def bind( self, key ):
        def set_handler( function ):
            def callback( *args, **kwargs ):
                return '(start){}(end)'.format( function( *args, **kwargs ) )
            self.handlers[ key ] = callback
            return callback
        return set_handler

    #=========================================================================
    def trigger( self, key, *args, **kwargs ):
        if key in self.handlers:
            return self.handlers[ key ]( *args, **kwargs )
        return 'Trigger failed to find {} handler.'.format( key )


#=============================================================================
reg = registration()
@reg.bind( 'make_ints' )
def num_list( limit ):
    return ','.join( str( n ) for n in range( limit ) )


#=============================================================================
def demo():
    """
    Runs the demonstration code.
    """

    print( 'Converting integer to plain text, then decorating with a tag.' )
    print( plain_text( 42 ) )

    print( 'Wraps converted thing in back-ticks and a tag.' )
    print( plain_text_two( 42 ) )

    print( 'Register a callback with an interface.' )
    print( reg.trigger( 'make_ints', 7 ) )


#=============================================================================
def main( argv ):
    """
    Script execution entry point
    @param argv List of arguments passed to the script
    @return     Shell exit code (0 = success)
    """

    # imports when using this as a script
    import argparse

    # create and configure an argument parser
    parser = argparse.ArgumentParser(
        description = 'A Shell Script',
        add_help    = False
    )
    parser.add_argument(
        '-h',
        '--help',
        default = False,
        help    = 'Display this help message and exit.',
        action  = 'help'
    )
    parser.add_argument(
        '-v',
        '--version',
        default = False,
        help    = 'Display script version and exit.',
        action  = 'version',
        version = __version__
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # check args.* for script execution here
    demo()

    # return success
    return os.EX_OK


#=============================================================================
if __name__ == "__main__":
    import os
    import sys
    sys.exit( main( sys.argv ) )

