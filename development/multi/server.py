#!/usr/bin/env python
##############################################################################
#
# server.py
#
##############################################################################


import signal
import SocketServer


#=============================================================================
class SimpleHandler( SocketServer.BaseRequestHandler ):
    """
    Allows handling server requests.
    """

    def handle( self ):
        """
        Handle server requests.
        """
        request  = self.request.recv( 128 ).strip()
        response = request.upper()
        self.request.sendall( response )


#=============================================================================
class StreamHandler( SocketServer.StreamRequestHandler ):
    """
    Allows handling server requests using streams.
    """

    def handle( self ):
        """
        Handle server requests.
        """
        request  = self.rfile.readline().strip()
        response = request.upper()
        self.wfile.write( response )


#=============================================================================
def run_server( host, port ):
    """
    Initializes and starts the server bound to the specified host and port.
    @param host         Bind the server to this address
    @param port         Bind the server to this port
    """

    # create a new TCP server
    server = SocketServer.TCPServer( ( host, port ), StreamHandler )

    try:

        # run the TCP server
        server.serve_forever()

    except:

        # syscall I/O is noisy on termination, handle all exceptions to avoid
        #   all the STDOUT/STDERR
        pass


#=============================================================================
def signal_handler( signal_number, frame ):
    """
    Empty signal handler (for now)
    @param signal_number
                        The signal number from the OS interrupt
    @param frame        The frame
    """
    pass


#=============================================================================
def main( argv ):
    """
    Script execution entry point
    @param argv         Arguments passed to the script
    @return             Exit code (0 = success)
    """

    # install some signal handlers to override what Python installed
    signal.signal( signal.SIGTERM, signal_handler )
    signal.signal( signal.SIGINT,  signal_handler )

    # basic config can be specified from program arguments
    host = 'localhost'
    port = 2142
    if( len( argv ) > 1 ):
        host = argv[ 1 ]
    if( len( argv ) > 2 ):
        port = int( argv[ 2 ] )

    # run the demo server
    run_server( host, port )

    # return success
    return 0


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
