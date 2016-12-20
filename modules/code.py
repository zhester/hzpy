#=============================================================================
#
# Source Code Analysis and Manipulation Utilities
#
#=============================================================================

"""
Source Code Analysis and Manipulation Utilities
===============================================
"""


import collections
import logging
import re
import textwrap


__version__ = '0.0.0'



#=============================================================================
# Code manipulation report entry
Entry = collections.NamedTuple( 'Entry', 'message,start,stop' )


#=============================================================================
class Reporter( object ):
    """
    Code manipulation reporting system.
    """


    #=========================================================================
    def __init__( self ):
        """
        Initializes a Reporter object.
        """
        self._reports = []


    #=========================================================================
    def add( self, message, start, stop = None ):
        """
        Adds an entry to the report.
        """
        entry = Entry( message, start, stop )
        self._reports.append( entry )


    #=========================================================================
    def __str__( self ):
        """
        Generates the report as a plain-text string of entries.
        """
        reports = []
        for entry in self._reports:
            if entry.stop is None:
                reports.append( '{}: {}'.format( entry.start, entry.message ) )
            else:
                reports.append(
                    '{}-{}: {}'.format(
                        entry.start, entry.stop, entry.message
                    )
                )
        return '\n'.join( reports )


#=============================================================================
def reblock( outflo, inflo, cols = 78, reporter = None ):
    """
    Reformats block-style comments to fit specific column widths.
    """

    # Default the reporter.
    if reporter is None:
        reporter = Reporter()

    # Patterns used to identify block-style comments.
    start = r'(\s*)/\*[*=-]+\s*'
    stop  = r'(\s*)[*=-]+\*/\s*'

    # The text wrapping system.
    tw = textwrap.TextWrapper( width = cols )

    # Comment capturing state.
    capture = False

    # Scan the file for block-style comments.
    for line in inflo:

        # Check for capturing phase.
        if capture == True:

            # Check for end-of-block.
            test = re.match( stop, line )
            if test is not None:

                # Finished capturing comments.
                capture = False

                # Set the default wrapping indentation.
                tw.initial_indent    = test.group( 1 )
                tw.subsequent_indent = test.group( 1 )

                # Break comments into paragraph sections.
                ###### ZIH

                # Re-flow comments back to outflo.
                for comment in clines:
                    ###### ZIH
                    pass

            # Currently capturing comments.
            else:
                clines.append( line )

        # Not capturing.
        else:

            # Check for start-of-block.
            test = re.match( start, line )
            if test is not None:

                # Prepare to capture comments.
                clines  = []
                capture = True

            # Not a start of block, and not capturing.
            else:

                # Write the original line directly to the outflo.
                outlfow.write( line )

