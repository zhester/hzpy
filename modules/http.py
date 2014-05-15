#!/usr/bin/env python


"""
HTTP helper class for typical use cases.
"""


import BaseHTTPServer
import cookielib
import json
import urllib2


__version__ = '0.0.0'


# set a module variable to the dict of HTTP response code strings
_http_codes = BaseHTTPServer.BaseHTTPRequestHandler.responses


#=============================================================================
class http_error( Exception ):
    """
    Narrowing error class for simplified exception handling.
    The only reason this is used is to shield the user from the underlying
    exceptions (and having to know the various incantations needed to produce
    a meaningful message), and present a single string in an attempt to help
    the user find a solution.
    """
    pass


#=============================================================================
class http( object ):
    """
    Provides a simplified interface to fetching files and data over HTTP.
    """


    #=========================================================================
    def __init__( self, config = None ):
        """
        Initializes an http object.

        Example:
            client = http( { 'proxy' : { 'host':'proxy','port':3128 } } )

        @param config Optionally specify configuration values that need to
                      remain consistent from one request to the next.
                      The configuration should be a dictionary.
                      Supported configuration values are as follows:
                        proxy   Container dictionary for the following items:
                          type  Type of proxy (currently, only "http")
                          host  Proxy host
                          port  Proxy service port
                          user  Optional user name to send to proxy
                          pass  Optional password to send to proxy
        """

        # store the config in object state
        self.config = config if config is not None else {}

        # set up a list of HTTP handlers
        self.handlers = []

        # check for proxy configuration, and initialize as needed
        self._check_proxy()

        # initialize a cookie jar for browser-like cookie handling
        policy = cookielib.DefaultCookiePolicy(
            rfc2965          = True,
            strict_ns_domain = cookielib.DefaultCookiePolicy.DomainStrict
        )
        cjar = cookielib.CookieJar( policy )
        cproc = urllib2.HTTPCookieProcessor( cjar )
        self.handlers.append( cproc )

        # build our custom opener and install it for future requests
        opener = urllib2.build_opener( *self.handlers )
        urllib2.install_opener( opener )


    #=========================================================================
    def fetch( self, url, local ):
        """
        Requests a remote file over HTTP, and stores the response on the local
        file system.
        @param url The URL of the remote file to download over HTTP
        @param local The path to the local destination file
        @return The number of bytes written to the local file
        @throws http_error
        """

        # attempt to open the local file for writing the contents of the fetch
        try:
            handle = open( local, 'wb' )
        except IOError:
            raise http_error( 'Unable to open %s.' % local )

        # attempt to fetch the remote file
        response = self._get_url( url )

        # write the contents of the remote file to the local file
        handle.write( response.read() )

        # determine how many bytes were written
        result = handle.tell()

        # fetch the response headers
        info = response.info()

        # see if a Content-Length header was sent
        if 'content-length' in info:

            # check the length of the file against the header's value
            length = int( info[ 'content-length' ] )
            if result != length:
                raise http_error(
                    'Data written (%d) does not match data promised (%d).' % (
                        result, length
                    )
                )

        # close the file
        handle.close()

        # return the number of bytes written
        return result


    #=========================================================================
    def get_json( self, url ):
        """
        Requests a URL, receives the response, and parses the response as if
        it were a JSON document.
        @param url The URL of the JSON resource to request
        @return An object containing the data parsed from the JSON document
        @throws http_error
        """

        # attempt to fetch the JSON response from the host
        response = self._get_url( url )

        # make sure the host says it sent JSON data
        if response.ctype[ 0 ] == 'application/json':

            # attempt to parse the response data into a native dict/list/etc
            return json.loads( response.read() )

        # host did not send the appropriate Content-Type header
        raise http_error(
            'Invalid Content-Type (%s) received for JSON request.\n%s' % (
                response.ctype[ 0 ],
                response.read()
            )
        )


    #=========================================================================
    def post_json( self, url, data ):
        """
        Requests a URL with a message body containing a JSON document.  Then
        receives the response, and parses the response as if it were a JSON
        document.
        @param url URL of the resource that accepts POST requests
        @param data Data to send in the body (will be converted to JSON)
        @return An object containing the data parsed from the JSON document
        @throws http_error
        """

        # send the POST request, fetch a JSON response (hopefully)
        response = self._post_url(
            url,
            body     = json.dumps( data ),
            mimetype = 'application/json'
        )

        # make sure the host says it sent JSON data
        if response.ctype[ 0 ] == 'application/json':

            # attempt to parse the response data into a native dict/list/etc
            return json.loads( response.read() )

        # host did not send the appropriate Content-Type header
        raise http_error(
            'Invalid Content-Type (%s) received for JSON request.\n%s' % (
                response.ctype[ 0 ],
                response.read()
            )
        )


    #=========================================================================
    def _check_proxy( self ):
        """
        Check for proxy information in the user's configuration.
        """
        if 'proxy' in self.config:
            pc = self.config[ 'proxy' ]
            if 'type' not in pc:
                pc[ 'type' ] = 'http'
            if 'host' not in pc:
                pc[ 'host' ] = 'proxy'
            if 'port' not in pc:
                pc[ 'port' ] = 3128
            elif type( pc[ 'port' ] ) is not str:
                pc[ 'port' ] = str( pc[ 'port' ] )
            if ( 'user' in pc ) and ( pc[ 'user' ] is not None ):
                if ( 'pass' in pc ) and ( pc[ 'pass' ] is not None ):
                    auth = pc[ 'user' ] + ':' + pc[ 'pass' ] + '@'
                else:
                    auth = pc[ 'user' ] + '@'
            else:
                auth = ''
            self.proxy = {
                pc[ 'type' ] :
                    'http://%s%s:%d' % ( auth, pc['host'], pc['port'] )
            }
            proxy = urllib2.ProxyHandler( self.proxy )
            self.handlers.append( proxy )


    #=========================================================================
    def _decorate_response( self, response ):
        """
        Decorates response objects for internal use.
        """
        # make the content-type header easier to use
        headers = response.info()
        dtype   = [ 'text/html', 'utf-8' ]
        if 'content-type' in headers:
            ctype = headers[ 'content-type' ]
            pos = ctype.find( ';' )
            if pos != -1:
                dtype[ 0 ] = ctype[ 0 : pos ]
                dtype[ 1 ] = ( ctype[ ( pos + 1 ) : ] ).strip()
            else:
                dtype[ 0 ] = ctype
        setattr( response, 'ctype', dtype )


    #=========================================================================
    def _get_url( self, url ):
        """
        Perform a GET request for the given URL, and return a response object.
        """
        request = urllib2.Request( url )
        try:
            response = urllib2.urlopen( request )
        except HTTPError as e:
            raise http_error(
                'Error: %d; %s' % ( e.code, _http_codes[ e.code ][ 0 ] )
            )
        except URLError as e:
            raise http_error( 'Error: %d; %s' % e.reason )
        self._decorate_response( response )
        return response


    #=========================================================================
    def _post_url( self, url, body, mimetype = None ):
        """
        Perform a POST request for the given URL.
        @param url URL of the resource that accepts POST requests
        @param body POST message body as a string
        @param mimetype Optional POST body MIME type
                        Typical types include:
                          application/x-www-form-urlencoded: Simple HTML forms
                          multipart/form-data: Multipart HTML forms (files)
                          application/json: JSON document
                          text/plain: Plain text (spaces converted to "+")
                        If not specified, the MIME type is assumed to be
                        application/x-www-form-urlencoded.
        @return The response object from the remote host
        @throws http_error
        """

        # default the mimetype, if necessary
        if mimetype is None:
            mimetype = 'application/x-www-form-urlencoded'

        # set up the request
        request = urllib2.Request(
            url, body, { 'Content-Type' : mimetype }
        )

        # send the request, fetch the response
        try:
            response = urllib2.urlopen( request )
        except HTTPError as e:
            raise http_error(
                'Error: %d; %s' % ( e.code, _http_codes[ e.code ][ 0 ] )
            )
        except URLError as e:
            raise http_error( 'Error: %d; %s' % e.reason )

        # return the response object
        self._decorate_response( response )
        return response


#=============================================================================
def fetch( url, local, config = None ):
    """
    Provides a convenience function for simple file downloading.
    @param url The URL of the remote file to download over HTTP
    @param config Optional HTTP client config (see: http.__init__ docstring)
    @param local The path to the local destination file
    """

    # create a basic HTTP client
    client = http( config )

    # request the file, and attempt to store locally
    client.fetch( url, local )


#=============================================================================
def get_json( url, config = None ):
    """
    Provides a convenience function for simple JSON GET requests.
    @param url The URL of the JSON resource to request
    @param config Optional HTTP client config (see: http.__init__ docstring)
    @return An object containing the data parsed from the JSON document
    """

    # create a basic HTTP client
    client = http( config )

    # request the JSON document, and return the result
    return client.get_json( url )


#=============================================================================
def post_json( url, data, config = None ):
    """
    Provides a convenience function for simple JSON POST requests.
    @param url URL of the resource that accepts POST requests
    @param data Data to send in the body (will be converted to JSON)
    @param config Optional HTTP client config (see: http.__init__ docstring)
    @return An object containing the data parsed from the JSON document
    """

    # create a basic HTTP client
    client = http( config )

    # request the JSON document, and return the result
    return client.post_json( url, data )


#=============================================================================
def main( argv ):
    """
    Script execution entry point
    @param argv Arguments passed to the script
    @return Exit code (0 = success)
    """

    # imports when using this as a script
    import argparse

    # argument-aware file fetching
    def fetch_args( args ):
        fetch( args.url, args.file )

    # argument-aware JSON requesting
    def json_args( args ):
        if args.file:
            with open( args.file, 'r' ) as fh:
                data = json.load( fh )
                print post_json( args.url, data )
        else:
            print get_json( args.url )

    # other testing goes on in here
    def test( args ):
        print 'Sorry, no testing today.'

    # standard (improved) help argument specification
    helpargs = [ '-h', '--help' ]
    helpkwargs = {
        'default' : False,
        'help'    : 'Display this help message and exit.',
        'action'  : 'help'
    }

    # create and configure an argument parser
    parser = argparse.ArgumentParser(
        description = 'HTTP Client Script',
        add_help    = False
    )
    parser.add_argument( *helpargs, **helpkwargs )
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
        help    = 'Development testing switch.',
        action  = 'store_true'
    )

    # set up sub-parsers for each action
    subparsers = parser.add_subparsers(
        title = 'Actions',
        help  = 'The following commands are supported.'
    )

    # fetch action parser
    fetch_action = subparsers.add_parser(
        'fetch',
        description = 'Download a file over HTTP.',
        help        = 'Download a file over HTTP.',
        add_help    = False
    )
    fetch_action.add_argument( *helpargs, **helpkwargs )
    fetch_action.add_argument(
        'url',
        help    = 'The URL of the remote file to download'
    )
    fetch_action.add_argument(
        'file',
        help    = 'The path to the local destination file'
    )
    fetch_action.set_defaults( call = fetch_args )

    # JSON action parser
    json_action = subparsers.add_parser(
        'json',
        description = 'Request a URL expecting a JSON response.',
        help        = 'Request a URL expecting a JSON response.',
        add_help    = False
    )
    json_action.add_argument( *helpargs, **helpkwargs )
    json_action.add_argument(
        'url',
        help    = 'The URL of the remote resource to request'
    )
    json_action.add_argument(
        'file',
        help    = 'The path to a JSON document to send',
        default = False
    )
    json_action.set_defaults( call = json_args )

    # test action parser
    test_action = subparsers.add_parser(
        'test',
        description = 'Development testing.',
        help        = 'Development testing.',
        add_help    = False
    )
    test_action.add_argument( *helpargs, **helpkwargs )
    test_action.set_defaults( call = test )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # call the appropriate, arguments-aware function
    args.call( args )

    # return success
    return 0


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
