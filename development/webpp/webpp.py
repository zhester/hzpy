#!/usr/bin/env python


"""
Offline Web Preprocessor
"""


import HTMLParser
import os
import re
import sys

from xml.dom import minidom


__version__ = '0.0.0'


#=============================================================================
class PpHTMLParser( HTMLParser.HTMLParser ):
    """
    ZIH - currently a pure passthrough parser (no mutation)
    """
    def __init__( self, ofh ):
        # old-style parent constructor invocation
        HTMLParser.HTMLParser.__init__( self )
        self._ofh = ofh
    def handle_charref( self, name ):
        self._ofh.write( '&#%s;' % name )
    def handle_comment( self, comment ):
        self._ofh.write( '<!--%s-->' % comment )
    def handle_data( self, data ):
        self._ofh.write( data )
    def handle_decl( self, decl ):
        self._ofh.write( '<!%s>' % decl )
    def handle_endtag( self, tag ):
        self._ofh.write( '</%s>' % tag )
    def handle_entityref( self, name ):
        self._ofh.write( '&%s;' % name )
    def handle_pi( self, data ):
        self._ofh.write( '<%s>' % data )
    def handle_starttag( self, tag, attrs ):
        dattrs = dict( attrs )
        if ( tag == 'link' )                        \
            and ( 'rel' in dattrs )                 \
            and ( 'href' in dattrs )                \
            and ( dattrs[ 'rel' ] == 'stylesheet' ) :
            # ZIH - fix path referencing
            self._handle_style( dattrs[ 'href' ] )
        else:
            guts = tag
            for attr in attrs:
                guts += ' %s="%s"' % ( attr[ 0 ], attr[ 1 ] )
            self._ofh.write( '<%s>' % guts )
    def handle_startendtag( self, tag, attrs ):
        self.handle_starttag( tag, attrs )

    def _handle_style( self, href ):
        self._ofh.write( '<style>\n' )
        with open( href, 'rb' ) as handle:
            self._ofh.write( handle.read() )
        self._ofh.write( '\n</style>' )


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


#=============================================================================
class Preprocessor( object ):
    """
    Web Preprocessor
    """


    #=========================================================================

    # List of known input formats
    formats = [ 'html' ]


    #=========================================================================
    def __init__( self, input_handle, base_path = '.', file_type = 0 ):
        """
        Initializes an instance of a web preprocessor object.

        @param input_handle The input file handle from which to read the
                            source file
        @param base_path    Base path to check for relative references
        @param file_type    The type of file we will be resolving (index into
                            the `formats` list).  If not specified, the class
                            starts by assuming we are resolving an HTML file.
        """

        # initalize object state
        self._base_path    = base_path
        self._file_type    = file_type
        self._input_handle = input_handle


    #=========================================================================
    def get_status( self ):
        """
        Check the status of the preprocessor.

        @return The preprocessor's current status.  0 is nominal.
        """

        return 0


    #=========================================================================
    def proc( self, output_handle = None ):
        """
        Executes the preprocessor.

        @param output_handle The output file to which resolved contents are
                             written.  If not specified, output is written to
                             stdout.
        """

        # see if the user wishes to capture output on stdout
        if output_handle is None:
            output_handle = sys.stdout

        # dispatch type-specific preprocessor
        if self._file_type < len( Preprocessor.formats ):
            type_proc = getattr(
                self,
                ( '_proc_' + Preprocessor.formats[ self._file_type ] )
            )
            type_proc( output_handle )

        # unknown format
        else:
            raise ValueError(
                'Unknown source file type index: %d' % self._file_type
            )


    #=========================================================================
    def _proc_html( self, writer ):
        """
        ZIH - not fully implemented
        """

        parser = PpHTMLParser( writer, self._base_path )
        parser.feed( self._input_handle.read() )


    #=========================================================================
    def _proc_xml( self, writer ):
        """
        ZIH - partial attempt at XHTML support
        """

        # attempt to parse the HTML file
        dom = minidom.parse( self._input_handle )

        # look for script tags
        scripts = dom.documentElement.getElementsByTagName( 'script' )
        for script in scripts:
            if script.hasAttribute( 'src' ) == True:
                # ZIH - fix path resolution
                source = script.getAttribute( 'src' )
                with open( source, 'rb' ) as handle:
                    cdata = document.createTextNode( handle.read() )
                script.removeAttribute( 'src' )
                script.appendChild( cdata )

        # look for link tags
        links = dom.documentElement.getElementsByTagName( 'link' )
        for link in links:
            if link.getAttribute( 'rel' ) == 'stylesheet':
                # ZIH - fix path resolution
                href = link.getAttribute( 'href' )
                with open( href, 'rb' ) as handle:
                    cdata = document.createTextNode( handle.read() )
                style = dom.documentElement.createElement( 'style' )
                style.appendChild( cdata )
                dom.documentElement.replaceChild( link, style )

        # write the modified DOM to the output
        dom.writexml( writer, addindent = '  ' )



#=============================================================================
def proc( ifile, ofile = None ):
    """
    Convenience function for executing the preprocessor on the given source
    files.

    @param ifile The input file to begin resolving external references
    @param ofile The output file to write the resolved source file
    @return      The success of the preprocessor (0 = successful)
    """

    # determine the type of input file from the extension
    match = re.search( r'\.(\w+)$', ifile )
    if match is None:
        print '### ', ifile
        raise ValueError( 'Unable to determine input file type.' )
    ext = match.group( 1 )
    try:
        ftype = Preprocessor.formats.index( ext )
    except:
        raise ValueError( 'Unknown format in "%s" file.' % ext )

    # check for optional output file name
    if ofile is None:
        ofile = re.sub( r'\.(\w+)$', r'.out.\1', ifile )

    # determine path information
    base = os.path.dirname( os.path.realpath( ifile ) )

    # open the input and output files
    ifh = open( ifile, 'rb' )
    ofh = open( ofile, 'wb' )

    # create the preprocessor
    pp = Preprocessor( ifh, file_type = ftype, base_path = base )

    # execute the preprocessor writing contents to the given file
    pp.proc( ofh )

    # close the files
    ifh.close()
    ofh.close()

    # return the shell-style status of the preprocessor
    return pp.get_status()


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
        description = 'Offline Web Preprocessor',
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
        'input',
        help = 'Input file'
    )
    parser.add_argument(
        'output',
        default = None,
        nargs   = '?',
        help    = 'Output file'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # run the preprocessor convenience function with the given files
    return proc( args.input, args.output )


#=============================================================================
if __name__ == "__main__":
    sys.exit( main( sys.argv ) )

