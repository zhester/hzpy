#!/usr/bin/env python.exe
#############################################################################
#
# List processes in Windows for the current user.
#
# Note: Magical ".exe" allows this to run from Cygwin as well as normal
#       Windows file association.
#
#############################################################################

import ctypes

#============================================================================
def get_proc_list():
    """
    Use the Win32 PSAPI to query the system for a list of processes.
    Various details about each process is returned as a list of dicts.
    """

    # process list storage
    procs = []

    # reference the Windows DLLs that inform us about processes
    psapi = ctypes.windll.psapi
    krnl  = ctypes.windll.kernel32

    # arguments to psapi call
    arr  = ctypes.c_ulong * 256
    pids = arr()
    size = ctypes.c_ulong()

    # arguments to kernel call
    proc_query = 0x0400 | 0x0010

    # arguments to psapi call
    module_handle = ctypes.c_ulong()
    module_count  = ctypes.c_ulong()
    module_name   = ctypes.create_unicode_buffer( 256 )

    # get a list of process IDs
    psapi.EnumProcesses(
        ctypes.byref( pids ),
        ctypes.sizeof( pids ),
        ctypes.byref( size )
    )

    # number of processes currently running
    num_procs = size.value / ctypes.sizeof( ctypes.c_ulong() )

    # examine processes
    for i in range( num_procs ):

        # fetch a handle to a process by ID
        handle = krnl.OpenProcess( proc_query, False, pids[ i ] )

        # make sure we got a process handle
        if handle is not None:

            # create storage for process information
            proc = { 'id' : pids[ i ] }

            # query the process for information
            psapi.EnumProcessModules(
                handle,
                ctypes.byref( module_handle ),
                ctypes.sizeof( module_handle ),
                ctypes.byref( module_count )
            )
            psapi.GetModuleBaseNameW(
                handle,
                module_handle.value,
                module_name,
                ctypes.sizeof( module_name )
            )

            # check for returned basename
            basename = module_name.value
            if len( basename ) > 0:

                # set basename
                proc[ 'basename' ] = module_name.value

            # add this process to the list of processes
            procs.append( proc )

            # release the process handle
            krnl.CloseHandle( handle )

    # return the process list information
    return procs


#=============================================================================
if __name__ == "__main__":
    import sys
    procs = get_proc_list()
    for p in procs:
        pairs = []
        for ( k, v ) in p.items():
            pairs.append( '%s:%s' % ( k, str( v ) ) )
        print '; '.join( pairs )

