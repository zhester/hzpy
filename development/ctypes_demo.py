#!/cygdrive/c/Python35/python.exe

import ctypes
import ctypes.wintypes

class TestStruct( ctypes.Structure ):

    _fields_ = [
        ( 'a', ctypes.c_uint32 ),
        ( 'b', ctypes.c_uint32 ),
        ( 'c', ctypes.c_uint16 ),
        ( 'd', ctypes.c_uint16 ),
        ( 'e', ctypes.c_char * 32 ),
        ( 'f', ctypes.c_char_p ),
        ( 'g', ctypes.c_wchar * 32 ),
        ( 'h', ctypes.c_wchar_p ),
        ( 'i', ctypes.c_void_p )
    ]

data = TestStruct()

for f in data._fields_:
    attr = getattr( data, f[ 0 ] )
    print( type( attr ), ':', attr )

class TestUnion( ctypes.Union ):

    _fields_ = [
        ( 'a', ctypes.c_uint32 ),
        ( 'b', ctypes.c_int32 ),
        ( 'c', ctypes.c_float )
    ]

unions = [
    TestUnion( a = 0x80000000 ),
    TestUnion( b = 0x80000000 ),
    TestUnion( c = 3.14159 )
]

for u in unions:
    for f in u._fields_:
        attr = getattr( u, f[ 0 ] )
        print( type( attr ), ' [', ctypes.sizeof( u ), ']:', attr )

