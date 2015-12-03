#!/usr/bin/env python
#=============================================================================
#
# Clean CSV
#
#=============================================================================

"""
Clean CSV
=========
"""


import csv
import sys


__version__ = '0.0.0'


#=============================================================================
def clean_csv( source, target ):
    """
    Cleans a CSV file.
    """
    with open( source ) as sfh:
        reader = csv.reader( sfh )
        with open( target, 'w' ) as tfh:
            writer = csv.writer( tfh )
            for record in reader:
                writer.writerow( map( lambda x : x.strip(), record ) )


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
        description = 'Clean CSV',
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
        'source',
        help = 'Path to source CSV file.'
    )
    parser.add_argument(
        'target',
        help = 'Path to target CSV file.'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # check args.* for script execution here
    clean_csv( args.source, args.target )

    # return success
    return 0


#=============================================================================
if __name__ == "__main__":
    sys.exit( main( sys.argv ) )

