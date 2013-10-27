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
def load_fields( obj, fields, data ):
    """
    Load binary data into an object's attributes given field definitions.
    A field definition is a dict describing a way to load and store each value
    in a data field.  A single field is described by a bit mask and bit offset
    within the unpacked data.  E.g. 'my_field' : ( 0xF0, 4 )
    @param obj          Target object to populate
    @param fields       Field definition list
    @param data         List of data fields resulting from a binary unpack
    """

    for field, value in zip( fields, data ):
        for name, desc in field.items():
            setattr( obj, name, ( ( value & desc[ 0 ] ) >> desc[ 1 ] ) )


#=============================================================================
def unload_fields( obj, fields ):
    """
    The complement of load_fields().
    @param obj          Source object to read
    @param fields       Field definition list
    @return             List of data fields suitable for a binary pack
    """

    data = []
    for field in fields:
        value = 0
        for name, desc in field.items():
            value |= getattr( obj, name ) << desc[ 1 ]
        data.append( value )
    return data


#=============================================================================
class _rfc6455_Frame( object ):

    #=========================================================================
    OP_CONTINUATION = 0x0
    OP_TEXT         = 0x1
    OP_BINARY       = 0x2
    OP_CLOSE        = 0x8
    OP_PING         = 0x9
    OP_PONG         = 0xA

    op_strings = (
        'continuation', 'text', 'binary', None, None, None, None, None,
        'close',        'ping', 'pong',   None, None, None, None, None
    )

    #=========================================================================
    _hdr = [
        {
            'final'   : ( 0x80, 7 ),
            'control' : ( 0x08, 3 ),
            'opcode'  : ( 0x0F, 0 )
        },
        {
            'mask'   : ( 0x80, 7 ),
            'length' : ( 0x7F, 0 )
        }
    ]

    _nhdrs = ( ( '', '!H', '!Q' ), ( '4B', '!H4B', '!Q4B' ) )

    _state_init     = 0
    _state_headers  = 1
    _state_payload  = 2
    _state_complete = 3

    #=========================================================================
    def __init__( self, data = None ):
        self._buffer   = ''
        self._hfmt     = ''
        self._hlen     = 0
        self._offset   = 2
        self._state    = self._state_init
        self._text     = None
        self._unmasked = None
        self.control   = 0
        self.final     = 0
        self.length    = 0
        self.mask      = 0
        self.mask_key  = None
        self.opcode    = 0
        if data is not None:
            self.put( data )

    #=========================================================================
#    def get_text_frame_data( self, text = None ):
#        hdr = unload_fields( self, self._hdr )
#        if text is None:
#            text = self.get_payload()
#        else:
#            self.length = len( text )
#
#        return hdr + nhdr + text

    #=========================================================================
    def get_payload( self ):
        if self.mask == 1:
            if self._unmasked is None:
                self._unmasked = ''.join(
                    chr(
                        ord( self._buffer[ i + self._offset ] )
                        ^
                        self.mask_key[ i % 4 ]
                    )
                    for i in range( self.length )
                )
            return self._unmasked
        return self._buffer[ self._offset : ]

    #=========================================================================
    def is_complete( self ):
        return self._state == self._state_complete

    #=========================================================================
    def is_control( self ):
        return self.control == 1

    #=========================================================================
    def is_final( self ):
        return self.final == 1

    #=========================================================================
    def is_masked( self ):
        return self.mask == 1

    #=========================================================================
    def put( self, data ):

        # append data to internal buffer string
        self._buffer += data
        length = len( self._buffer )

        # see if the frame is in the initial state
        if self._state == self._state_init:

            # skip everything else if we haven't received a second byte yet
            if length < 2:
                return

            # load the core header data into the object
            load_fields(
                self,
                self._hdr,
                struct.unpack( 'BB', self._buffer[ : 2 ] )
            )

            # check for additional headers with a large payload length
            if self.length > 125:
                self._hfmt = self._nhdrs[ self.mask ][ self.length - 125 ]

            # normal payload length
            else:
                self._hfmt = self._nhdrs[ self.mask ][ 0 ]

            # length of additional headers
            self._hlen = struct.calcsize( self._hfmt )

            # offset to the end of the headers, beginning of data
            self._offset = 2 + self._hlen

            # the frame has basic data available
            self._state = self._state_headers

        # see if the headers need additional parsing
        if self._state == self._state_headers:

            # do we have enough data to finish header parsing?
            if length >= self._offset:

                # parse additional header data (if any)
                hdat = struct.unpack(
                    self._hfmt,
                    self._buffer[ 2 : self._offset ]
                )

                # see if we should update payload length
                if self.length > 125:
                    self.length = hdat[ 0 ]

                # see if we need a masking key
                if self.mask == 1:
                    self.mask_key = hdat[ -4 : ]

                # from here on, we are only capturing payload
                self._state = self._state_payload

        # see if we still need data for the payload
        if self._state == self._state_payload:

            # see if we have captured enough data for the payload
            if length >= ( 2 + self._hlen + self.length ):

                # all set
                self._state = self._state_complete


#=============================================================================
class _rfc6455_Message( object ):

    #=========================================================================
    def __init__( self ):
        self._frame  = _rfc6455_Frame()
        self._frames = []

    #=========================================================================
    def is_complete( self ):
        try:
            return self._frames[ -1 ].is_final()
        except IndexError:
            return False

    #=========================================================================
    def is_control( self ):
        try:
            return self._frames[ -1 ].is_control()
        except IndexError:
            return False

    #=========================================================================
    def get_payload( self ):
        return ''.join( f.get_payload() for f in self._frames )

    #=========================================================================
    def get_type( self ):
        try:
            return self._frames[ 0 ].opcode
        except IndexError:
            return None

    #=========================================================================
    def put( self, data ):
        self._frame.put( data )
        if self._frame.is_complete() == True:
            self._frames.append( self._frame )
            self._frame = _rfc6455_Frame()


#=============================================================================
class _rfc6455_Stream( object ):

    #=========================================================================
    def __init__( self ):
        self._fifo    = []
        self._message = _rfc6455_Message()

    #=========================================================================
    def get_message( self ):
        try:
            return self._fifo.pop( 0 )
        except IndexError:
            raise ValueError

    #=========================================================================
    def put( self, data ):
        self._message.put( data )
        if self._message.is_complete() == True:
            self._fifo.append( self._message )
            self._message = _rfc6455_Message()


#=============================================================================
class rfc6455:


    #=========================================================================
    GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'


    #=========================================================================
    Frame   = _rfc6455_Frame
    Message = _rfc6455_Message
    Stream  = _rfc6455_Stream


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
    stream = rfc6455.Stream()

    # start the socket handling loop
    while True:

        # block until new data arrives from the client
        data = connection.recv( 1024 )

        # data received from connection
        if len( data ) > 0:

            # put data to stream
            stream.put( data )

            # get the next message in the input stream
            try:
                message = stream.get_message()
            except ValueError:
                pass
            else:

                # get type of message
                mtype = message.get_type()

                # close control message
                if mtype == rfc6455.Frame.OP_CLOSE:
                    # ZIH - echo frame payload to client
                    break

                # ZIH - also look for OP_PING (send OP_PONG)

                # handle text messages
                elif mtype == rfc6455.Frame.OP_TEXT:
                    text = message.get_payload()

                    # ZIH - temp
                    print text
                    data = text2frame( text.upper() )
                    connection.send( data )

        # empty data from connection (socket has closed)
        else:

            # shut down socket handling loop
            break

    # close our connection object
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
