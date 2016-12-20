#!/cygdrive/c/Python27/python.exe

import numpy
import OpenGL as ogl
import OpenGL.GLUT
import OpenGL.GLU


num_vertices = 0


def init_points():
    ogl.GL.glClearColor( 1.0, 1.0, 1.0, 0.0 )
    ogl.GL.glColor3f( 0.0, 0.0, 0.0 )
    ogl.GL.glPointSize( 4.0 )
    ogl.GL.glMatrixMode( ogl.GL.GL_PROJECTION )
    ogl.GL.glLoadIdentity()
    ogl.GLU.gluOrtho2D( 0.0, 640.0, 0.0, 480.0 )

def display_points():
    ogl.GL.glClear( ogl.GL.GL_COLOR_BUFFER_BIT )
    ogl.GL.glBegin( ogl.GL.GL_POINTS )
    ogl.GL.glVertex2i( 100, 50 )
    ogl.GL.glVertex2i( 100, 130 )
    ogl.GL.glVertex2i( 150, 130 )
    ogl.GL.glEnd()
    ogl.GL.glFlush()


def init_cube():
    ogl.GL.glClearColor( 0.0, 0.0, 0.0, 0.0 )
    ogl.GL.glShadeModel( ogl.GL.GL_FLAT )
    ogl.GL.glColor3f( 1.0, 1.0, 1.0 )
    #ogl.GL.glMatrixMode( ogl.GL.GL_PROJECTION )
    ogl.GL.glMatrixMode( ogl.GL.GL_MODELVIEW )
    ogl.GL.glLoadIdentity()
    ogl.GL.glOrtho( -2.0, 2.0, -2.0, 2.0, 0.0, 4.0 )

def display_cube():
    global num_vertices
    ogl.GL.glClear( ogl.GL.GL_COLOR_BUFFER_BIT )
    vertices = (
        (  1, -1, -1 ),
        (  1,  1, -1 ),
        ( -1,  1, -1 ),
        ( -1, -1, -1 ),
        (  1, -1,  1 ),
        (  1,  1,  1 ),
        ( -1, -1,  1 ),
        ( -1,  1,  1 )
    )
    edges = (
        ( 0, 1 ),
        ( 0, 3 ),
        ( 0, 4 ),
        ( 2, 1 ),
        ( 2, 3 ),
        ( 2, 7 ),
        ( 6, 3 ),
        ( 6, 4 ),
        ( 6, 7 ),
        ( 5, 1 ),
        ( 5, 4 ),
        ( 5, 7 )
    )
    num_vertices = len( vertices )
    ogl.GL.glBegin( ogl.GL.GL_LINES )
    for edge in edges:
        for vertex_index in edge:
            ogl.GL.glVertex3fv( vertices[ vertex_index ] )
    ogl.GL.glEnd()
    ogl.GL.glFlush()


def init_poly():
    vertices = (
        ( 0, 1, 0 ),
        ( 1, 2, 0 ),
        ( 2, 3, 0 ),
        ( 3, 2, 0 ),
        ( 2, 1, 0 ),
        ( 0, 1, 0 )
    )
    colors = numpy.ones( ( num_vertices, 3 ) )
    ogl.GL.glClearColor( 1.0, 1.0, 1.0, 0.0 )
    ogl.GL.glVertexPointerd( vertices )
    ogl.GL.glColorPointerd( colors )
    ogl.GL.glEnableClientState( ogl.GL.GL_VERTEX_ARRAY )
    ogl.GL.glEnableClientState( ogl.GL.GL_COLOR_ARRAY )

def display_poly():
    global num_vertices
    ogl.GL.glClear( ogl.GL.GL_COLOR_BUFFER_BIT | ogl.GL.GL_DEPTH_BUFFER_BIT )
    ogl.GL.glOrtho( -1, 1, -1, 1, -1, 1 )
    ogl.GL.glDisable( ogl.GL.GL_LIGHTING )
    ogl.GL.glDrawArrays( ogl.GL.GL_LINE_LOOP, 0, num_vertices )
    ogl.GL.glEnable( ogl.GL.GL_LIGHTING )


def init_gcube():
    ogl.GL.glClearColor( 0.0, 0.0, 0.0, 0.0 )
    ogl.GL.glShadeModel( ogl.GL.GL_FLAT )

def display_gcube():
    ogl.GL.glClear( ogl.GL.GL_COLOR_BUFFER_BIT )
    ogl.GL.glColor3f( 1.0, 1.0, 1.0 )
    ogl.GL.glLoadIdentity()
    ogl.GLU.gluLookAt( 0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0 )
    ogl.GL.glScalef( 1.0, 2.0, 1.0 )
    #ogl.GLUT.glutSolidCube( 1.0 )
    ogl.GLUT.glutWireCube( 1.0 )
    ogl.GL.glFlush()

def reshape_gcube( width, height ):
    ogl.GL.glViewport( 0, 0, width, height )
    ogl.GL.glMatrixMode( ogl.GL.GL_PROJECTION )
    ogl.GL.glLoadIdentity()
    ogl.GL.glFrustum( -1.0, 1.0, -1.0, 1.0, 1.5, 20.0 )
    ogl.GL.glMatrixMode( ogl.GL.GL_MODELVIEW )


if __name__ == '__main__':

    # GLUT setup
    ogl.GLUT.glutInit()
    ogl.GLUT.glutInitWindowSize( 640, 480 )
    ogl.GLUT.glutCreateWindow( 'Hello World' )
    ogl.GLUT.glutInitDisplayMode( ogl.GLUT.GLUT_SINGLE | ogl.GLUT.GLUT_RGB )

    # display some vertices (works)
    #ogl.GLUT.glutDisplayFunc( display_points )
    #init_points()

    # display some flat geometry (doesn't work)
    #ogl.GLUT.glutDisplayFunc( display_poly )
    #init_poly()

    # display a manually-drawn cube (doesn't work)
    init_cube()
    ogl.GLUT.glutDisplayFunc( display_cube )

    # display a cheater-drawn cube (works)
    #init_gcube()
    #ogl.GLUT.glutDisplayFunc( display_gcube )
    #ogl.GLUT.glutReshapeFunc( reshape_gcube )

    # application loop
    ogl.GLUT.glutMainLoop()

