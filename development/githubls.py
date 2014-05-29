#!/usr/bin/env python


"""
Lists all GitHub repositories for a given user.
"""


import sys

sys.path.append( '../modules' )
import http


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
        description = 'List a user\'s GitHub repositories.',
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
        'user',
        help = 'Specify the GitHub user name.'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # fetch the user's repos
    repos = http.get_json(
        'https://api.github.com/users/%s/repos' % args.user
    )

    # send list of repo names to stdout
    for r in repos:
        print r[ 'name' ]

    # return success
    return 0


#=============================================================================
if __name__ == "__main__":
    sys.exit( main( sys.argv ) )

