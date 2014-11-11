#!/usr/bin/env python


"""
Hyperlink Reference Resolution
"""


__version__ = '0.0.0'


#=============================================================================
class HyperRef( object ):
    """
    Deals with the subtleties of resolving hyperlink references.
    """

    #========================================================================
    def __init__( self, reference_file ):
        """
        """
        self._ref      = reference_file
        self._realpath = os.path.realpath( reference_file )
        self._dir      = os.path.dirname( self._realpath )

    #========================================================================
    def relative( self, path ):
        """
        """
        # ZIH TODO
        # look for URL-y things (http|https)
        # relative path may or may not be local to file system
        #realpath = os.path.realpath( path )
        # is it a file or directory?
        # compare self._dir to dirname()
        # look for document root references (/blah/blah)
        pass


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
        description = 'Hyperlink Reference Resolution Test',
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
    print 'No tests currently implemented.'

    # return success
    return 0


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )

