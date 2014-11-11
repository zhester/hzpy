#!/usr/bin/env python


"""
Cookie Storage and Response Example
"""


__version__ = '0.0.0'


import cookielib
import json
import urllib2


#=============================================================================
def get_cookie_value( cookiejar, name ):
    """
    Retrieves the value of a cookie from a CookieJar given its name.
    """
    value = None
    for cookie in cookiejar:
        if cookie.name == name:
            value = cookie.value
            break
    return value


#=============================================================================
def print_cookies( uri ):
    """
    Prints all the cookies from a given URI.
    """

    # create a cookie jar
    cj = cookielib.CookieJar()

    # create the custom URL opener
    opener = urllib2.build_opener( urllib2.HTTPCookieProcessor( cj ) )
    urllib2.install_opener( opener )

    # create the client request object (this is where you set request headers)
    request = urllib2.Request( uri )

    # open the URL
    handle = urllib2.urlopen( request )

    # print all response headers
    #print handle.info()

    # print all the cookies for this URI
    for index, cookie in enumerate( cj ):
        print '[%d]%s:%s' % ( index, cookie.name, cookie.value )


#=============================================================================
def test_session( uri ):
    """
    Tests a "session" of requests to a known host resource.
    """

    # basic setup to handle cookies (all in-memory)
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener( urllib2.HTTPCookieProcessor( cj ) )
    urllib2.install_opener( opener )

    # request to get the initial session state
    request = urllib2.Request( uri + '?fetch=true' )
    handle = urllib2.urlopen( request )
    initial_id = get_cookie_value( cj, 'session_test' )
    initial = json.load( handle )

    # request to change the session state
    request = urllib2.Request( uri + '?ckey=tkey&cval=tval' )
    handle = urllib2.urlopen( request )
    setup_id = get_cookie_value( cj, 'session_test' )
    setup = json.load( handle )

    # request to get the final session state
    request = urllib2.Request( uri + '?fetch=true' )
    handle = urllib2.urlopen( request )
    final_id = get_cookie_value( cj, 'session_test' )
    final = json.load( handle )

    # tests consistency of reported session ID
    if initial_id != final_id:
        print 'FAILED: session ID mismatch: %s != %s' % (
            initial_id, final_id
        )

    # verifies the host resource isn't cheating
    elif 'tkey' in initial[ 'session' ]:
        print 'FAILED: "tkey" present in initial session'

    # verifies the updated state has a valid entry
    elif 'tkey' not in final[ 'session' ]:
        print 'FAILED: "tkey" not present in final session'

    # verifies the updated entry is correct
    elif final[ 'session' ][ 'tkey' ] != 'tval':
        print 'FAILED: "tkey" incorrect value "tval" != "%s"' % (
            final[ 'session' ][ 'tkey' ],
        )

    # all checks verified
    else:
        print 'PASSED: "tkey" set to "%s" in session %s' % (
            final[ 'session' ][ 'tkey' ],
            get_cookie_value( cj, 'session_test' )
        )



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
        description = 'Cookie Storage and Response Example',
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


    uri = 'http://hzian.com/projects/test/session.php'
    #print_cookies( uri )
    test_session( uri )


    # return success
    return 0


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )

