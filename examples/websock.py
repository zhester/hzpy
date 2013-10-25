#!/usr/bin/env python


"""
A Demonstration WebSocket Server
"""


import socket
import threading


__version__ = '0.0.0'


#=============================================================================
_handshake = '''HTTP/1.1 101 Web Socket Protocol Handshake
Connection: Upgrade
Upgrade: WebSocket
Sec-WebSocket-Origin: %s
Sec-WebSocket-Location: ws://%s/
Sec-WebSocket-Protocol: demo

'''


#=============================================================================
def handle( connection, address ):
    request = connection.recv( 1024 )
    lines   = request.strip().splitlines()
    headers = dict( h.split( ': ', 1 ) for h in lines if ':' in h )
    connection.send( _handshake % ( headers[ 'Origin' ], headers[ 'Host' ] ) )
    while True:
        data = connection.recv( 1024 )
        if len( data ) > 0:
            connection.send( data.upper() )
        else:
            break
    connection.close()


#=============================================================================
def wsnet( address ):
    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    sock.bind( address )
    sock.listen( 5 )
    while True:
        connection, address = sock.accept()
        print 'hello %d' % address[ 1 ]
        thread = threading.Thread(
            target = handle,
            args   = ( connection, address )
        )
        thread.daemon = True
        thread.start()
    sock.close()
    return 0


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
        description = 'A Demonstration WebSocket Server'
    )
    parser.add_argument(
        '-p',
        '--port',
        default = 9999,
        help    = 'TCP listen port.',
    )
    parser.add_argument(
        '-v',
        '--version',
        default = False,
        help    = 'Display script version.',
        action  = 'store_true'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # check for version request
    if args.version == True:
        print 'Version', __version__
        return 0

    # run the server until interrupted
    exit_code = wsnet( ( '', args.port ) )

    # return success
    return exit_code


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
