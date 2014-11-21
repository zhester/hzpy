#!/usr/bin/env python


"""
Module Shell Script Example

This example demonstrates a simple way to access a module's functions by
calling them from the shell.  The complexity lies in how much code is needed
to properly construct an ArgumentParser that can take sub-commands.

The application may define as much or as little configuration as it feels is
necessary to help users gain access to the exposed module functions.  If no
configuration is specified, all module-level functions that are not prefixed
with an underscore are made a available to the shell.  Each argument is listed
by its function's parameter name.  Unless configured otherwise, parameters are
all passed as strings from the command line.

Note: This does NOT expose any built-in functions or things that are otherwise
accessible to this module.  Only locally-defined functions are exposed.

To get a good idea of the flexibility provided here, start by requesting the
script's "help" documentation:

    ./module_script.py -h

A list of sub-commands is provided.  Each sub-command maps to one of the
locally-defined module functions in this file.  To request the documentation
related to any of these sub-commands, specify its name first:

    ./module_script.py fun0 -h

A list of all valid/optional arguments are provided as if the sub-command was
a stand-alone script.
"""


__version__ = '0.0.0'


#-----------------------------------------------------------------------------
# Application-specific Functions
#-----------------------------------------------------------------------------

#=============================================================================
def fun0( a, b, c = 42, d = 'hello' ):
    """
    A function used for testing the example.
    """
    print '{3}, {0}. Do you want {2} {1}s?'.format( a, b, c, d )
    return 0


#=============================================================================
def fun1( x ):
    """
    Another function used for testing the example.
    """
    print '{0} times {0} is {1}'.format( x, ( x * x ) )
    return 0


#=============================================================================
def fun2():
    """
    A function that takes no parameters.
    """
    print 'Hello from function number two!'
    return 0


#=============================================================================
def _fun3():
    """
    Example of a conventionally "private" function.
    """
    print 'Whoa!  How\'d you find me?'
    return 0


#-----------------------------------------------------------------------------
# The script that automatically calls the application's functions.
#-----------------------------------------------------------------------------

#=============================================================================
def main( argv ):
    """
    Script execution entry point
    @param argv         Arguments passed to the script
    @return             Exit code (0 = success)
    """

    #-------------------------------------------------------------------------
    # BEGIN: Per-script Configuration
    #-------------------------------------------------------------------------

    # set a pattern used to match desired function names
    # example of only allowing certain prefixes:
    #    guard_pattern = r'^demo_'
    guard_pattern = None

    # set up auto type-conversions for functions that expect parameters to
    # be of a specified type
    # note: the parameter list must be complete for any specified function.
    #       the default parser will pass all parameters as strings if the
    #       function is not listed here.
    parameter_types = {
        'fun1' : { 'x' : int }
    }

    # set up auto parameter documentation here
    # note: the parameter list must be complete for any specified function.
    parameter_docs = {
        'fun0' : {
            'a' : 'Name',
            'b' : 'Desired item',
            'c' : 'Number of desired items',
            'd' : 'The greeting'
        }
    }

    #-------------------------------------------------------------------------
    # END: Per-script Configuration
    #-------------------------------------------------------------------------

    # imports when using this as a script
    # note: it's probably better to put these at the top of the file, but
    #       we're assuming the application may not rely on these modules.
    import argparse
    import inspect
    import re

    # get the name of the current function (most likely "main")
    current_name = inspect.currentframe().f_code.co_name

    # create a list of functions used to test each function for exposure
    tests = [

        # only expose functions
        inspect.isfunction,

        # do not expose conventionally "private" functions
        lambda f: f.__name__[ : 1 ] != '_',

        # do not expose the current function
        lambda f: f.__name__ != current_name
    ]

    # if there's a guard pattern, set up a regular expression to test it
    if guard_pattern is not None:
        tests.append(
            lambda f: re.match( guard_pattern, f.__name__ ) is not None
        )

    # create a filter function (in a closure) to omit unwanted functions
    def create_predicate( tests ):
        def predicate( function ):
            for test in tests:
                if test( function ) == False:
                    return False
            return True
        return predicate
    test = create_predicate( tests )

    # get a reference to the current module
    module = sys.modules[ __name__ ]

    # construct a list of functions from the module's dictionary
    functions = [ m[ 1 ] for m in inspect.getmembers( module, test ) ]

    # standard (improved) help argument specification
    helpargs   = [ '-h', '--help' ]
    helpkwargs = {
        'default' : argparse.SUPPRESS,
        'help'    : 'Display this help message and exit.',
        'action'  : 'help'
    }

    # create and configure an argument parser
    parser = argparse.ArgumentParser(
        description = 'Module Shell Script Example',
        add_help    = False
    )
    parser.add_argument( *helpargs, **helpkwargs )
    parser.add_argument(
        '-t',
        '--test',
        default = argparse.SUPPRESS,
        help    = 'Execute script self-test.',
        action  = 'store_true'
    )
    parser.add_argument(
        '-v',
        '--version',
        default = argparse.SUPPRESS,
        help    = 'Display script version and exit.',
        action  = 'version',
        version = __version__
    )

    # set up sub-command parsers
    subparsers = parser.add_subparsers(
        title = 'Functions',
        help  = 'The following functions are available.'
    )

    # add a sub-command parser for each function
    for function in functions:

        # shortcut for the function name
        name = function.__name__

        # use the function's docstring for helpful information
        docstring = inspect.getdoc( function )

        # create a sub-parser for this function
        subparser = subparsers.add_parser(
            name,
            description     = docstring,
            help            = docstring,
            add_help        = False,
            formatter_class = argparse.ArgumentDefaultsHelpFormatter
        )

        # standard help switch
        subparser.add_argument( *helpargs, **helpkwargs )

        # argument specification of function
        fun_args = inspect.getargspec( function )
        num_args = len( fun_args.args )

        # check for argument defaults
        if fun_args.defaults is not None:
            defaults = list( fun_args.defaults )
        else:
            defaults = []

        # load arguments into this sub-parser
        for arg in fun_args.args:

            # keyword arguments used to create the sub-parser argument
            kwargs = {}

            # check for default values specified in the function
            if num_args == len( defaults ):
                kwargs[ 'nargs' ]   = '?'
                kwargs[ 'default' ] = defaults.pop( 0 )

            # check for specified parameter types for this function
            if name in parameter_types:
                kwargs[ 'type' ] = parameter_types[ name ][ arg ]

            # check for specified parameter documentation for this function
            if name in parameter_docs:
                kwargs[ 'help' ] = parameter_docs[ name ][ arg ]

            # add the specified argument to the sub-parser
            subparser.add_argument( arg, **kwargs )

            # decrement number of remaining arguments to add
            num_args -= 1

        # set the function to be called when this sub-command is issued
        subparser.set_defaults( _call = function )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # check for self-test request
    if hasattr( args, 'test' ) and args.test == True:
        import os
        result = 0
        script = os.path.basename( __file__ )
        tests  = [
            ( script, 'fun0', 'Bob', 'waffles' ),
            ( script, 'fun0', 'Bob', 'waffles', 3 ),
            ( script, 'fun0', 'Bob', 'waffles', 4, 'Greetings' )
        ]
        for test in tests:
            try:
                result = main( *test )
            except:
                print 'CAUGHT: {}'.format( sys.exc_info()[0] )
                raise
            else:
                if result != 0:
                    return result
        return result

    # load arguments into a new dict instance
    params = dict( vars( args ) )

    # scrub things that aren't arguments to the requested function
    # note: this means the function can't have parameters that begin with "_"
    for key in params.keys():
        if key[ : 1 ] == '_':
            del params[ key ]

    # call the function that was set for the specified sub-command
    result = args._call( **params )

    # check return for something non-shell-like
    if type( result ) is not int:
        print result
        return 0

    # return result
    return result


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )

