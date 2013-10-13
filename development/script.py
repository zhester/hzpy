#!/usr/bin/env python


"""
A Shell Script
"""


__version__ = '0.0.0'


#=============================================================================
def main( argv ):
    """
    Script execution entry point
    @param argv         Arguments passed to the script
    @return             Exit code (0 = success)
    """

    # imports when using this as a script
    import argparse

    # create and configure an argument parser
    parser = argparse.ArgumentParser(
        description = 'A Shell Script'
    )
    parser.add_argument(
        '-v',
        '--version',
        default = False,
        help    = 'Display script version.',
        action  = 'store_true'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # check for version request
    if args.version == True:
        print 'Version', __version__

    # return success
    return 0


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
