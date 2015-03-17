#!/usr/bin/env python


"""
MySQL Database Development Tool
===============================

Provides a user-friendly interface to executing (and re-executing) large
amounts of SQL statements on the DBMS using an SQL source file.  The use case
where this is most useful is in developing complicated stored
procedures/functions and triggers.
"""


import cStringIO
import csv
import os
import re
import subprocess
import sys

sys.path.append( '../modules' )

import text
import textproc


__version__ = '0.0.0'


#=============================================================================
mysql_client = '/usr/local/bin/mysql'
mysql_flags  = [ '-B' ]


#=============================================================================
def build_and_execute( filename, arguments = None, capture = False ):
    """
    Performs any necessary pre-processing on the target SQL script, then
    executes it using the configured MySQL command-line client.

    @param filename  The SQL source script file name
    @param arguments Additional arguments to pass to the MySQL CLI
    @param capture   When set, captures output to a set of CSV files
    """

    # sanity check user's file name
    if os.path.isfile( filename ) == False:
        print 'Unable to find file: {}'.format( filename )
        return

    # create a text pre-processor for the SQL source
    preproc = textproc.PreProcessor()

    # open the SQL source to redirect into the MySQL CLI
    with open( filename, 'r' ) as ifh:

        # run the preprocessor on the file (retrieves another file handle)
        pfh = preproc.process( ifh )

    # construct the list of command argument strings
    if arguments is None:
        arguments = [ mysql_client ] + mysql_flags
    else:
        arguments = [ mysql_client ] + mysql_flags + arguments

    # attempt to call CLI
    try:
        proc = subprocess.Popen(
            arguments,
            stdin  = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT
        )
        output, errors = proc.communicate( pfh.read() )

    # CLI returned non-zero, display code and error output
    except subprocess.CalledProcessError as error:
        print 'Client returned {}: {}'.format(
            error.returncode, error.output
        )

    # CLI returned zero
    else:

        # MySQL doesn't appear to return proper shell codes if there's an
        # error, this means it won't trap the exception above, and we need
        # redirect stderr into stdout, and check all output for errors
        if re.match( r'^ERROR', output ):
            print output.strip().split( "\n" )[ 0 ]
            exit( 1 )

        # get number of columns on console
        rows, columns = subprocess.check_output( [ 'stty', 'size' ] ).split()

        # capture file name format
        capfilefmt = filename[ : -4 ] + '_{:02}.csv'
        capnum = 0

        # display the result sets
        for result in parse_batch( output ):

            # print the result set in a formatted table
            print text.tabular( result, width = columns )

            # check for capture request
            if capture == True:
                cfname = capfilefmt.format( capnum )
                capnum += 1
                with open( cfname, 'w' ) as cfh:
                    writer = csv.writer( cfh )
                    for record in result:
                        writer.writerow( record )

    # close the processed SQL source file
    pfh.close()


#=============================================================================
def parse_batch( string ):
    """
    Parses MySQL CLI batch-mode output.
    Note: For now, this assumes that when the number of columns change, the
    batch output is sending a separate result set.  There should probably be
    a more explicit way of separating result sets.

    @param string The output from the MySQL CLI run in batch mode (-B)
    @yield        A series of two-dimensional lists of result set data
    """

    # break TSV data into individual lines
    lines = string.strip().split( '\n' )

    # initialize result set state
    num_cols = 0
    result   = None

    # scan each line in the batch output
    for line in lines:

        # parse TSV values
        items = line.split( '\t' )

        # number of items on this line
        num_items = len( items )

        # check for TSV item number transition
        if num_items != num_cols:

            # yield the previous result set
            if result is not None:
                yield result

            # set up a new result set
            num_cols = num_items
            result   = [ items ]

        # continuation of current result set
        else:
            result.append( items )

    # yield the final result set (no item number transition)
    if result is not None:
        yield result


#=============================================================================
def main( argv ):
    """
    Script execution entry point
    @param argv List of arguments passed to the script
    @return     Shell exit code (0 = success)
    """

    # when using as a script, write UTF-8 to stdout
    if sys.stdout.encoding != 'UTF-8':
        import codecs
        writer = codecs.getwriter( 'UTF-8' )
        sys.stdout = writer( sys.stdout )

    # imports when using this as a script
    import argparse

    # create and configure an argument parser
    parser = argparse.ArgumentParser(
        description = 'MySQL Database Development Tool',
        add_help    = False
    )
    parser.add_argument(
        '-c',
        '--capture',
        default = False,
        help    = 'Enable result set capturing to CSV files.',
        action  = 'store_true'
    )
    parser.add_argument(
        '-h',
        '--help',
        default = False,
        help    = 'Display this help message and exit.',
        action  = 'help'
    )
    parser.add_argument(
        '-p',
        '--password',
        help    = 'Database access password'
    )
    parser.add_argument(
        '-u',
        '--username',
        help    = 'Database access user name'
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
        help = 'SQL source file name to execute.'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # construct arguments to client program
    arguments = []
    if args.username is not None:
        arguments.append( '-u' )
        arguments.append( args.username )
    if args.password is not None:
        arguments.append( '-p' + args.password )

    # build and execute the SQL source file
    build_and_execute(
        args.source,
        arguments = arguments,
        capture   = args.capture
    )

    # return success
    return os.EX_OK


#=============================================================================
if __name__ == "__main__":
    sys.exit( main( sys.argv ) )

