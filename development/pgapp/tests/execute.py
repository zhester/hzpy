#!/cygdrive/c/Python27/python.exe


"""
Test Execution Script
"""


import importlib
import os
import sys


__version__ = '0.0.0'


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
        description = 'Test Execution Script',
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
    parser.add_argument(
        'target',
        nargs   = '?',
        default = None,
        help    = 'Specify the test target.',
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # set the test execution path
    exec_path = os.path.dirname( os.path.realpath( __file__ ) )

    # check for specific test target
    if args.target is not None:

        # construct path to test script
        filename  = args.target + '.py'
        exec_file = os.path.join( exec_path, filename )

        # check for existence of test script
        if os.path.isfile( exec_file ):

            # import the test script
            sys.path.append( exec_path )
            test_mod = importlib.import_module( args.target )

            # run the test script
            result = test_mod.run( None, None )

            # output the result
            if result == True:
                print( 'Success' )
            else:
                print( 'Failure' )

        # test script not available
        else:
            print( 'Unable to locate test script "{}"'.format( filename ) )

    # no test target given
    else:
        print( 'Batch testing not yet implemented.' )

    # return success
    return 0


#=============================================================================
if __name__ == "__main__":
    sys.exit( main( sys.argv ) )

