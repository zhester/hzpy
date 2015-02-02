#!/usr/bin/env python


"""
Application/Development Logging
===============================

This module's goal is similar, in spirit, to Python's built-in `logging`
module.  However, that module maintains global state, and can't be easily
extended or separately instantiated to maintain multiple logs from the same
application.  This is a simplified implementation that can do those things.

Interface
---------

### `EventLog`

The `EventLog` class provides a very simple logging facility that can be used
for basic application event logging and/or debugging.

#### `EventLog.put()`

To log a basic message, use the following:

    with open( 'output.log', 'w+' ) as log_file:
        elog = EventLog( log_file )
        elog.put( 'Hello World' )

For debugging Python code, two additional methods are provided.

#### `EventLog.trace()` and `EventLog.assrt()`

The `trace()` method adds the name of the python file, the line where the
message was logged, the name of the module, and the name of the calling
context (e.g. function name) to the message that is recorded.

The `assrt()` method does the same as `trace()`, but it requires an expression
to evaulate to a non-false value before the message can be logged.

    # a message full of context is not needed
    elog.trace( 'oops' )

    # only log if the test fails
    elog.assrt( type( age ) is int, "age wasn't an integer" )

#### `EventLog.enable()`

Sometimes it's nice to leave a lot of debugging code throughout your code.
The `enable()` method can either enable or disable all logging with a single
call.  Therefore, you don't need to "comment out" all the calls to logging
methods just to stop logging them.

### `LevelLog`

The `LevelLog` class provides the typical level-based logging facility in
fairly flexible interface.  As it extends the `EventLog`, those methods are
still available.

See `LevelLog` class' docstrings for more details on the additional interfaces
used to support multiple levels of logging.

Testing
-------

This module provides a built-in unit test.  The test can be run from the shell
by passing the `-t` or `--test` arguments.
"""


import json
import inspect
import os


__version__ = '0.0.0'


#=============================================================================
class EventLog( object ):
    """
    Simple event log.
    """

    #=========================================================================
    def __init__( self, stream = None, enable = True ):
        """
        Initializes an EventLog object.

        @param stream The output stream to which entries are logged
        @param enable Initially enable or disable all logging.  The log can
                      be enabled or disabled at any time via the `enable()`
                      method.
        """

        # initialize the parent
        super( EventLog, self ).__init__()

        # check and set the output stream
        self._stream = stream if stream is not None else sys.stdout

        # set the initial enable state
        self._enabled = enable


    #=========================================================================
    def enable( self, enable = True ):
        """
        Enables or disables the event log.

        @param enable Set to enable logging, clear to disable logging.
        """
        self._enabled = enable


    #=========================================================================
    def assrt( self, assertion, message ):
        """
        Adds a trace entry to the log only if the assertion fails.

        @param assertion The result of the user's assertion.  If the assertion
                         fails (False), the message is logged.  Otherwise, the
                         message is ignored.
        @param message   The message string to log.  This should not include a
                         new-line character at the end.  A minor amount of
                         magical formatting may be performed to allow logging
                         non-strings in a sensible fashion.
        """

        # test the assertion
        if assertion == False:

            # obtain the frame from the calling context
            frame = inspect.stack()[ 1 ][ 0 ]

            # add the trace entry
            self.trace_from( message, frame )


    #=========================================================================
    def put( self, message ):
        """
        Adds an entry to the log.

        @param message The message string to log.  This should not include a
                       new-line character at the end.  A minor amount of
                       magical formatting may be performed to allow logging
                       non-strings in a sensible fashion.
        """

        # check if the log is currently enabled
        if self._enabled == True:

            # see if the message is not a string
            if isinstance( message, str ) == False:

                # see if the message is a container type, and encode
                if isinstance( message, dict ) or isinstance( message, list ):
                    message = json.dumps( message )

                # otherwise, try to coerce the message into a string
                else:
                    message = str( message )

            # add the entry to the log
            self._stream.write( '{}\n'.format( message ) )

            # flush the buffer in case someone is following the log
            self._stream.flush()


    #=========================================================================
    def trace( self, message ):
        """
        Traces the entry from the caller, and adds it to the log.

        The difference between this an `put()` is that additional code tracing
        information is added to the log entry.  This enables simpler messages
        to be sent to the event log since the source file and line number are
        recorded to assist with tracking the source of the message.

        @param message The message string to log.  This should not include a
                       new-line character at the end.  A minor amount of
                       magical formatting may be performed to allow logging
                       non-strings in a sensible fashion.
        """

        # obtain the frame from the calling context
        frame = inspect.stack()[ 1 ][ 0 ]

        # trace from this frame
        self.trace_from( message, frame )


    #=========================================================================
    def trace_from( self, message, frame ):
        """
        Traces the entry from any given frame, and adds it to the log.

        @param message The message string to log.  This should not include a
                       new-line character at the end.  A minor amount of
                       magical formatting may be performed to allow logging
                       non-strings in a sensible fashion.
        @param frame   The calling context's frame.
        """

        # extract information about the given frame
        module = inspect.getmodule( frame )
        info   = inspect.getframeinfo( frame )

        # format a log entry with code context information
        output = '{}:{},{}.{}> {}'.format(
            info.filename,
            info.lineno,
            module.__name__,
            info.function,
            message
        )

        # add the trace entry to the log
        self.put( output )


#=============================================================================
class LevelLog( EventLog ):
    """
    Implements a log that maintains multiple levels of reporting.

    Note: The logging levels are generated when an object is created.  The
    class property `_levels` is used to maintain the initial list of logging
    levels.  Each level will have a numerical attribute named for the level
    that can be passed into LevelLog.log().

        log = LevelLog()
        log.log( log.WARN, 'my message' )

    Additionally, each level has a generated method that can be used with the
    same results, only in a shorter notation.

        log = LevelLog()
        log.warn( 'my message' )

    The method names are just lower-cased versions of the property names.
    """

    #=========================================================================

    # log reporting levels
    _levels = [ 'NOTICE', 'WARN', 'ERROR' ]


    #=========================================================================
    def __init__(
        self,
        stream = None,
        enable = True,
        level  = 0,
        levels = None
    ):
        """
        Initializes a LevelLog object.

        @param stream The output stream to which entries are logged
        @param enable Initially enable or disable all logging.  The log can
                      be enabled or disabled at any time via the `enable()`
                      method.
        @param level  The minimum log level to add to the log.  All events
                      that are logged below this level are ignored.  This
                      level can be changed at any time via the `level`
                      property.
        @param levels A custom list of log levels to use instead of the
                      built-in list [ 'NOTICE', 'WARN', 'ERROR' ]
        """

        # initialize the parent
        super( LevelLog, self ).__init__( stream, enable )

        # set the minimum logging level
        self.level = level

        # check for a custom list of logging levels
        if levels is not None:
            self._levels = [ l.upper() for l in levels ]

        # closure to build custom level methods
        def make_level_method( index ):
            def level_method( self, message ):
                self.log( index, message )
            return level_method

        # construct convenience properties and methods
        index = 0
        for level in self._levels:
            setattr( LevelLog, level, index )
            setattr( LevelLog, level.lower(), make_level_method( index ) )
            index += 1


    #=========================================================================
    def log( self, level, message ):
        """
        Logs a message at a specified level.

        @param level   The level at which to log this message.  This may be
                       either an integer (0 = NOTICE, 1 = WARN, etc.), a
                       string ( 'NOTICE', 'WARN', etc.), or a property
                       (obj.NOTICE, obj.WARN, etc.).
                       The level must be at or above the configured level in
                       order for it to be added to the log.
        @param message The message string to log.  This should not include a
                       new-line character at the end.  A minor amount of
                       magical formatting may be performed to allow logging
                       non-strings in a sensible fashion.
        """

        # levels can be specified by their string in `self._levels`
        if isinstance( level, str ):
            level = self._levels.index( level )

        # boundary check index-specified levels
        elif level >= len( self._levels ):
            raise RuntimeError( 'Invalid logging level: {}.'.format( level ) )

        # only log events that are at or above the configured level
        if self.level <= level:

            # add the entry to the log
            self.put( '{}: {}'.format( self._levels[ level ], message ) )


#=============================================================================
def _test_event_log( log ):
    """
    Basic test to ensure the event log works as intended.
    """

    import re
    import StringIO

    log.put( 'EventLog' )

    # test regular message logging using a string stream
    output = StringIO.StringIO()
    elog = EventLog( output )
    lines = [ 'hello world', 'another entry', 'yet another entry' ]
    for line in lines:
        elog.put( line )
    actual = output.getvalue()
    output.close()

    expected = '\n'.join( lines ) + '\n'
    if expected != actual:
        log.fail( 'put (multiple lines)' )

    # test non-string messages
    output = StringIO.StringIO()
    elog = EventLog( output )
    class NotAString:
        def __str__( self ):
            return 'i am not a string'
    elog.put( NotAString() )
    elog.put( { 'a' : 1, 'b' : 2 } )
    elog.put( [ 42, 3.14159, 'hello', ( 1, 2, 3 ) ] )
    elog.put( 42 )
    expected = """i am not a string
{"a": 1, "b": 2}
[42, 3.14159, "hello", [1, 2, 3]]
42
"""
    actual = output.getvalue()
    output.close()
    if expected != actual:
        log.fail( 'put (non-string messages)' )

    # test trace message logging
    output = StringIO.StringIO()
    elog = EventLog( output )
    expected = 'message'

    # before we request a trace, grab the current frame state
    frame = inspect.currentframe()

    # request a debugging trace message
    elog.trace( expected )
    expected_line = frame.f_lineno - 1

    actual = output.getvalue().strip()
    output.close()

    # parse the log entry
    #./eventlog.py:106,__main__._test_log> message
    pattern = r'(?P<script>[^:]+):(?P<line>\d+),'    \
        + r'(?P<module>[^.]+)\.(?P<function>[^>]+)>' \
        + r' (?P<message>.*)'
    match = re.match( pattern, actual )
    if match is None:
        log.fail( 'trace (entry pattern)' )
    a = match.groupdict()
    a[ 'script' ] = os.path.basename( a[ 'script' ] )

    # dynamically set the expected results of the trace entry
    e = {
        'script'   : os.path.basename( frame.f_code.co_filename ),
        'line'     : str( expected_line ),
        'module'   : __name__,
        'function' : frame.f_code.co_name,
        'message'  : expected
    }

    # evaluate all values in the entry in the trace log
    for key in e.keys():
        if a[ key ] != e[ key ]:
            log.fail(
                'trace ({}: "{}" != "{}")'.format( key, e[ key ], a[ key ] )
            )

    # test assertion logging
    output = StringIO.StringIO()
    elog = EventLog( output )
    expected = 'assertion failed'
    elog.assrt( False, expected )
    elog.assrt( True, 'assertion passed' )
    actual = output.getvalue().strip()
    output.close()
    match = re.match( r'.+\> (.*)$', actual )
    if match is None:
        log.fail( 'assrt (entry pattern)' )
    if match.group( 1 ) != expected:
        log.fail( 'assrt ("{}" != "{}")'.format( expected, actual ) )


#=============================================================================
def _test_level_log( log ):
    """
    Tests the LevelLog class.
    """

    import re
    import StringIO

    log.put( 'LevelLog' )

    output = StringIO.StringIO()

    llog = LevelLog( output )
    llog.log( 'NOTICE', 'notice message' )
    llog.log( llog.WARN, 'warn message' )
    llog.error( 'error message' )
    llog.level = 1
    llog.notice( 'ignored message' )
    llog.error( 'another error' )

    actual = output.getvalue()
    output.close()

    expected = """NOTICE: notice message
WARN: warn message
ERROR: error message
ERROR: another error
"""

    if actual != expected:
        log.fail( 'LevelLog' )


#=============================================================================
def _test():
    """
    Executes all module test functions.

    @return True if all tests pass, false if one fails.
    """

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
        description = 'Development EventLog',
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

