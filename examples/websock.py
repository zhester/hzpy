#!/usr/bin/env python


# http://tools.ietf.org/html/rfc6455

# typical HTTP request headers (rfc6455)
# GET /chat HTTP/1.1
# Host: server.example.com
# Upgrade: websocket
# Connection: Upgrade
# Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
# Origin: http://example.com
# Sec-WebSocket-Protocol: chat, superchat
# Sec-WebSocket-Version: 13

# validity checking (client requirements):
#   1. handshake must be valid HTTP request (rfc2616)
#   2. handshake must be a GET request, and HTTP version must be 1.1
#   3. request URI must match ws/wss URI
#   4. request must have Host header
#   5. request must have Upgrade header set to "websocket"
#   must have Connection: Upgrade
#   must have Sec-WebSocket-Version: 13
# if client doesn't send this correctly, respond with HTTP 400 error code
#   optional Origin:
#   optional Sec-WebSocket-Protocol:
#   optional Sec-WebSocket-Extensions:


"""
A Demonstration WebSocket Server
"""


import base64
import hashlib
import socket
import struct
import threading


__version__ = '0.0.0'


#=============================================================================
_guid = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'


#=============================================================================
_handshake = '''HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Origin: %s
Sec-WebSocket-Location: ws://%s
Sec-WebSocket-Accept: %s
Sec-WebSocket-Protocol: sample

'''


#=============================================================================
def frame2text( frame ):

    # unpack the initial two bytes to check for extent of header data
    header = struct.unpack( 'BB', frame[ : 2 ] )
    payload_length = header[ 1 ] & 0x7F

    # ZIH - should verify ( header[ 0 ] & 0x0F ) == 0x01
    #       to indicate text frame

    # 16-bit payload length
    if payload_length == 126:
        payload_length = struct.unpack( '!H', frame[ 2 : 4 ] )[ 0 ]
        if header[ 1 ] & 0x80 == 0x80:
            masking_key = struct.unpack( '!4B', frame[ 4 : 8 ] )
            offset = 8
        else:
            offset = 4

    # 63-bit payload length
    elif payload_length == 127:
        payload_length = struct.unpack( '!Q', frame[ 2 : 10 ] )[ 0 ]
        if header[ 1 ] & 0x80 == 0x80:
            masking_key = struct.unpack( '!4B', frame[ 10 : 14 ] )
            offset = 14
        else:
            offset = 10

    # 7-bit payload length
    else:
        if header[ 1 ] & 0x80 == 0x80:
            masking_key = struct.unpack( '!4B', frame[ 2 : 6 ] )
            offset = 6
        else:
            offset = 2

    # unpack payload as a byte array
    payload = struct.unpack( '%dB' % payload_length, frame[ offset : ] )

    # check for masking
    if header[ 1 ] & 0x80 == 0x80:
        payload = [
            payload[ i ] ^ masking_key[ i % 4 ]
            for i in range( payload_length )
        ]

    # return the payload as a byte string
    return ''.join( chr( c ) for c in payload )


#=============================================================================
def text2frame( text ):

    payload_length = len( text )

    # ZIH - only supports text < 126 characters

    frame = struct.pack(
        'BB%ds' % payload_length,
        0x81,
        payload_length,
        text
    )

    return frame


#=============================================================================
def hexdump( blob ):
    import math
    length   = len( blob )
    bytes    = struct.unpack( '%dB' % length, blob )
    per_row  = 16
    num_rows = int( math.ceil( length / float( per_row ) ) )
    rows     = []
    for i in range( num_rows ):
        offset = i * per_row
        rows.append(
            ' '.join(
                '%02X' % x for x in bytes[ offset : offset + per_row ]
            )
        )
    return '  ' + '\n  '.join( rows )


#=============================================================================
def handle( connection, address ):
    request  = connection.recv( 1024 )
    lines    = request.strip().splitlines()
    headers  = dict( h.split( ': ', 1 ) for h in lines if ': ' in h )
    key      = headers[ 'Sec-WebSocket-Key' ]
    response = _handshake % (
        headers[ 'Origin' ],
        headers[ 'Host' ] + lines[ 0 ].split()[ 1 ],
        base64.b64encode( hashlib.sha1( key + _guid ).digest() )
    )
    connection.send( response )
    while True:
        data = connection.recv( 1024 )
        if len( data ) > 0:
            # ZIH - here we should decode opcode, and decide what to do
            text = frame2text( data )
            data = text2frame( text.upper() )
            connection.send( data )
        else:
            break
    connection.close()


#=============================================================================
def wsnet( address ):
    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    sock.bind( address )
    sock.listen( 5 )
    while True:
        try:
            connection, address = sock.accept()
        except ( KeyboardInterrupt, SystemExit ):
            break
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
