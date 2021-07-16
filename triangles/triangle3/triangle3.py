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
from cauldron import VertexArrayObject

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

# TRIANGLE1

VAO1 = VertexArrayObject()
# vertices
vertices = VAO1.createBuffer(data=((-0.6, -0.5, 0.5), (0.6, -0.5, 0.5), (0.0, 0.5, 0.5)))
vertices.connectToShader(location=0)
# colors
colors = VAO1.createBuffer(data=((0,0,1),(1,0,0),(0,1,0)))
colors.connectToShader(location=1)

# TRANGLE2

VAO2 = VertexArrayObject()
# vertices
vertices = VAO2.createBuffer(data=((-0.6, -0.5, 0.1), (0.6, -0.5, 0.1), (0.0, 0.5, 0.1)))
vertices.connectToShader(location=0)
# colors
colors = VAO2.createBuffer(data=((1,0,0),(0,1,0),(0,0,1)))
colors.connectToShader(location=1)

# RUN 

@window.event
def on_draw():
    gl.glClearColor(0.5, 0.6, 0.7, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    VAO2.drawArrays()
    VAO1.drawArrays()

dx = dy = 0
@window.event
def on_mouse_press(x,y,*args):
    global dx, dy, verts
    dx = (x-300)/300.0
    dy = (y-300)/300.0
    vertices.setData(((-0.6+dx, -0.5+dy, 0.1),(0.6+dx, -0.5+dy, 0.1), (0.0+dx, 0.5+dy, 0.1)))

    
gl.glEnable(gl.GL_DEPTH_TEST) # 3d
pyglet.app.run()