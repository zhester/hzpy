#!/usr/bin/env python


"""
Text Processing Module
======================

"""


import cStringIO
import os
import re


__version__ = '0.0.0'


#=============================================================================
class Processor( object ):
    """
    A general-purpose text file processor.  This gives developers a simple
    interface to building text processors based on their own needs.

    The two primary features provided are recursive inclusion of files within
    other files, and the ability to define macro symbols and have them
    substituted within the text.
    """

    #=========================================================================
    def __init__( self, paths = None ):
        """
        Initializes a Processor object.

        @param paths The list of search paths for file inclusion
        """

        # list of paths to search (in order) for file inclusion
        self.paths = paths if paths is not None else [ '.' ]

        # default patterns will (probably) do nothing
        self._pat_inc = r'__INCLUDE__'
        self._pat_set = r'__DEFINE__'
        self._pat_sub = r'__SUBSTITUTE__'

        # macro state map, keys are symbol names, values are literals
        self._macros = {}


    #=========================================================================
    def process( self, fh ):
        """
        Process the given file-like object.

        @param fh A file-like object to process
        @return   A file-like object of processed text
        """

        # the macro substitution replacer
        replacer = self._make_replacer( self._macros )

        # send post-processed output to an in-memory file
        pp = cStringIO.StringIO()

        # scan through each line in the file
        for line in fh:

            # check line for include directives
            match = re.match( self._pat_inc, line )
            if match is not None:
                incfile  = match.group( 1 )
                included = False

                # scan for file in all paths
                for p in self.paths:
                    incpath = p + os.path.sep + incfile
                    if os.path.isfile( incpath ):

                        # open file for processing before inclusion
                        with open( incpath, 'r' ) as ifh:
                            processed = self.process( ifh )
                            pp.write( processed.read() )
                        included = True
                        break

                # include directive found, but file not included
                if included == False:
                    raise RuntimeError(
                        'Unable to include file: "{}"'.format( incfile )
                    )

                # this is a directive, do not allow it to be added to file
                continue

            # check line for template macro definitions
            match = re.match( self._pat_set, line )
            if match is not None:

                # set the macro in the state map
                self._macros[ match.group( 1 ) ] = match.group( 2 )

                # this is a directive, do not allow it to be added to file
                continue

            # check line for macro substitutions
            line = re.sub( self._pat_sub, replacer, line )

            # write the line to the processed file
            pp.write( line )

        # reset the file position for the processed file
        pp.seek( 0, os.SEEK_SET )

        # return the handle to the processed file
        return pp


    #=========================================================================
    def set_include_pattern( self, pattern ):
        """
        Sets the file-inclusion pattern.  The first match group in this
        pattern must yield the file name to use for inclusion.

        @param pattern A pattern to extract inclusion directives
        """
        self._pat_inc = pattern


    #=========================================================================
    def set_macro_patterns( self, definition, substitution ):
        """
        Sets the macro definition and substitution patterns.  The first match
        group in each of these patterns must yield the string that is used in
        the macros definition/expansion.  The second match group in the
        definition pattern must extract the macro's literal value.

        @param definition   A pattern to extract defining macros
        @param substitution A pattern to substitute macro values
        """
        self._pat_set = definition
        self._pat_sub = substitution


    #=========================================================================
    def _make_replacer( self, state ):
        """
        Creates a macro symbol replacer function for `re.sub()`.

        @param state Current macro symbol-literal map state
        @return      A function that can be used to substitute matched
                     substition literals from `re.sub()`
        """
        def closure( match ):
            key = match.group( 1 )
            if key in state:
                return state[ key ]
            return match.group( 0 )
        return closure


#=============================================================================
class PreProcessor( Processor ):
    """
    A specialization of the generic `Processor` class that defines its own
    include and macro patterns.

    #include "external.file"
    #set SYMBOL LITERAL
    normal text with ${SYMBOL} substitution
    """

    #=========================================================================
    def __init__( self, *args, **kwargs ):
        """
        Initializes a PreProcessor object.
        """
        super( PreProcessor, self ).__init__( *args, **kwargs )
        self.set_include_pattern( r'#include\s+"([^"]+)"' )
        self.set_macro_patterns( r'#set\s+(\w+)\s+([^\n]+)', r'\$\{(\w+)\}' )


#=============================================================================
def _test_preprocessor( log ):
    """
    Tests the PreProcessor class.
    """

    # use temp files to check inclusion
    import tempfile

    # create a named temp file for inclusion in source file
    ef = tempfile.NamedTemporaryFile( delete = False )
    ef.write( 'External file contents.\n' )
    ef.write( 'Look, I can see ${SYMBOL}, too!\n' )
    ef.write( 'Here, have a symbol from me:\n' )
    ef.write( '#set EXTSYM EXTLIT\n' )
    ef_name = ef.name
    ef.close()

    # create the text processor
    pp = PreProcessor()

    # allow the preprocessor to find the temp file
    pp.paths.append( os.path.dirname( ef_name ) )

    # create a temp file for preprocessing
    tf = tempfile.TemporaryFile()
    tf.write( 'Example file\n#set SYMBOL LITERAL\n' )
    tf.write( 'Here is a ${SYMBOL} in the file.  Also here: ${SYMBOL}.\n' )
    tf.write( '#include "{}"\n'.format( os.path.basename( ef_name ) ) )
    tf.write( 'Content after including a file.\n' )
    tf.write( 'Included file set ${EXTSYM}.\n' )
    tf.seek( 0, os.SEEK_SET )

    # process the temp file
    processed = pp.process( tf )

    # close the temp file
    tf.close()

    # delete the temporary external file
    os.unlink( ef_name )

    # log the results of preprocessing
    log.put( 'Testing `PreProcessor`' )
    log.put( processed.read() )


#=============================================================================
def _test():
    """
    Executes all module test functions.

    @return True if all tests pass, false if one fails.
    """

    # imports for testing only
    import inspect

    # set up a simple logging facility to capture or print test output
    class TestError( RuntimeError ):
        pass
    class TestLogger( object ):
        def fail( self, message ):
            caller = inspect.getframeinfo( inspect.stack()[ 1 ][ 0 ] )
            output = '## FAILED {}: {} ##'.format( caller.lineno, message )
            self.put( output )
            raise TestError( output )
        def put( self, message ):
            sys.stdout.write( '{}\n'.format( message ) )
    log = TestLogger()

    # list of all module members
    members = globals().copy()
    members.update( locals() )

    # iterate through module members
    for member in members:

        # check members for test functions
        if ( member[ : 6 ] == '_test_' ) and ( callable( members[ member ] ) ):

            # execute the test
            try:
                members[ member ]( log )

            # catch any errors in the test
            except TestError:

                # return failure to the user
                return False

    # if no test fails, send a helpful message
    log.put( '!! PASSED !!' )

    # return success to the user
    return True


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
        description = 'Text Processing Module',
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
        '-t',
        '--test',
        default = False,
        help    = 'Execute built-in unit tests.',
        action  = 'store_true'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # user requests built-in unit tests
    if args.test != False:
        result = _test()
        if result == False:
            return os.EX_SOFTWARE
        return os.EX_OK

    # check args.* for script execution here
    else:
        print 'Module executed as script.'
        return os.EX_USAGE

    # return success
    return os.EX_OK


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )

