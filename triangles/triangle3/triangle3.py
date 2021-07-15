# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 16:08:25 2021

@author: whmcilha
Drawing a triangle in opengl with vertex attribute (colour)
and changing some attributes by mouse click

opengl area is -1...1 x and y, 0..1 z
"""

import pyglet
from pyglet import gl
import ctypes
import pyshaders

window = pyglet.window.Window(width=600, height=600)

# SHADERS - color and location

def setup_program():
    
    vertex_shader = '''
        #version 300 es
        precision mediump float;
        layout(location = 0) in vec4 position;
        layout(location = 1) in vec4 color;

        out vec4 vcolor ;
        
        void main()
        {
            gl_Position = position;
            vcolor = color;
        }
    '''

    fragment_shader = '''
        #version 300 es
        precision mediump float;
        
        in vec4 vcolor;
        out vec4 fColor;
        
        void main()
        {
             fColor = vcolor;
        }
    '''

    program = pyshaders.from_string(vertex_shader, fragment_shader)
    program.use()
    return program

program = setup_program()

# VERTICES

VAO = gl.GLuint(0)
VBO = gl.GLuint(0)
CBO = gl.GLuint(0)

# create the VAO

gl.glGenVertexArrays(1, ctypes.byref(VAO)) 
gl.glBindVertexArray(VAO) # makes the handle currently active

# create vertex buffer for a triangle

VERTEX = gl.GLfloat*3

gl.glGenBuffers(1, ctypes.byref(VBO)) # creates a handle to a VBO object
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO) # makes the buffer currently active

# make data and put in buffer

verts = (VERTEX * 3)((-0.6, -0.5, 0.1),(0.6, -0.5, 0.1), (0.0, 0.5, 0.1))
gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(verts), verts, gl.GL_DYNAMIC_DRAW)

# connect the buffer to location=0

gl.glEnableVertexAttribArray(0) # like pyshaders.attr.enable()
gl.glVertexAttribPointer(0, len(VERTEX()), gl.GL_FLOAT, False, ctypes.sizeof(VERTEX), 0)

# create the vertex colors for the triangle

COLOUR = gl.GLfloat*3;

gl.glGenBuffers(1, ctypes.byref(CBO)) # creates a handle to a VBO object
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, CBO) # makes the buffer currently active

# make data and put in buffer

colors = (COLOUR * 3)((1,0,0),(0,1,0), (0,0,1))
gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(colors), colors, gl.GL_DYNAMIC_DRAW)

# connect the buffer to location=1

gl.glEnableVertexAttribArray(1) # like pyshaders.attr.enable()
gl.glVertexAttribPointer(1, len(COLOUR()), gl.GL_FLOAT, False, ctypes.sizeof(COLOUR), 0)


gl.glBindVertexArray(0) # unbinds the VAO we were using

# RUN 

@window.event
def on_draw():
    gl.glClearColor(0.5, 0.6, 0.7, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glBindVertexArray(VAO)
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(verts)) # streams all the other attr as well
    gl.glBindVertexArray(0)

dx = dy = 0
@window.event
def on_mouse_press(x,y,*args):
    global dx, dy, verts
    dx = (x-300)/300.0
    dy = (y-300)/300.0
    print(dx, dy)
    verts = (VERTEX * 3)((-0.6+dx, -0.5+dy, 0.1),(0.6+dx, -0.5+dy, 0.1), (0.0+dx, 0.5+dy, 0.1))
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO) # makes the buffer currently active
    gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(verts), verts, gl.GL_DYNAMIC_DRAW)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0) # makes the buffer currently active

    
gl.glEnable(gl.GL_DEPTH_TEST) # 3d
pyglet.app.run()