#!/cygdrive/c/Python27/python.exe

import numpy
import OpenGL as ogl
import OpenGL.GLUT
import OpenGL.GLU

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

num_vertices = 0

def init_poly():
    global num_vertices
    vertices = [
        [ 0, 1, 2 ],
        [ 1, 2, 3 ],
        [ 2, 3, 0 ],
        [ 3, 0, 1 ],
        [ 0, 1, 2 ]
    ]
    num_vertices = len( vertices )
    colors       = numpy.ones( ( num_vertices, 3 ) )
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


if __name__ == '__main__':

    # GLUT setup
    ogl.GLUT.glutInit()
    ogl.GLUT.glutInitWindowSize( 640, 480 )
    ogl.GLUT.glutCreateWindow( 'Hello World' )
    ogl.GLUT.glutInitDisplayMode( ogl.GLUT.GLUT_SINGLE | ogl.GLUT.GLUT_RGB )

    # run test code
    #ogl.GLUT.glutDisplayFunc( display_points )
    #init_points()

    ogl.GLUT.glutDisplayFunc( display_poly )
    init_poly()

    # application loop
    ogl.GLUT.glutMainLoop()

