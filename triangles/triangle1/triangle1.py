# -*- coding: utf-8 -*-

import pyglet
from pyglet import gl
import ctypes
import pyshaders

window = pyglet.window.Window(width=600, height=600)

# SHADERS - not doing much here.

# using opengl 300 es for the shaders, as this gives me location & in/out
# which modern opengl shaders use.

def setup_program():
    
    vertex_shader = '''
        #version 300 es
        precision mediump float;
        layout(location = 0) in vec4 position;

        void main()
        {
            gl_Position = position;
        }
    '''

    fragment_shader = '''
        #version 300 es
        precision mediump float;
        
        out vec4 fColor;
        
        void main()
        {
             fColor = vec4(1.0, 0.5, 0.5, 1.0);
        }
    '''

    program = pyshaders.from_string(vertex_shader, fragment_shader)
    program.use()
    return program

program = setup_program()

# VERTICES

VAO = gl.GLuint(0)
VBO = gl.GLuint(0)

# create the VAO

gl.glGenVertexArrays(1, ctypes.byref(VAO)) 
gl.glBindVertexArray(VAO) # makes the handle currently active

# create vertex buffer for a triangle

VERTEX = gl.GLfloat*3

gl.glGenBuffers(1, ctypes.byref(VBO)) # creates a handle to a VBO object
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO) # makes the buffer currently active

# make data and put in buffer

data = (VERTEX * 3)((-0.6, -0.5, 0.1),(0.6, -0.5, 0.1), (0.0, 0.5, 0.1))
gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(data), data, gl.GL_DYNAMIC_DRAW)

# connect the buffer to location=0

gl.glEnableVertexAttribArray(0) # like pyshaders.attr.enable()
gl.glVertexAttribPointer(0, len(VERTEX()), gl.GL_FLOAT, False, ctypes.sizeof(VERTEX), 0)

gl.glBindVertexArray(0) # unbinds the VAO we were using

# RUN 

@window.event
def on_draw():
    gl.glClearColor(0.5, 0.6, 0.7, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glBindVertexArray(VAO)
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(data))

gl.glEnable(gl.GL_DEPTH_TEST) # 3d
pyglet.app.run()