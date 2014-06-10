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
def print_procs():
    """
    Use the Win32 PSAPI to query the system for a list of processes and print
    their process IDs and image basenames to stdout.
    """

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

                # print out the information
                print '%u: %s' % ( pids[ i ], module_name.value )

            # release the process handle
            krnl.CloseHandle( handle )


#=============================================================================
if __name__ == "__main__":
    print_procs()

