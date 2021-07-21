# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 16:08:25 2021

@author: whmcilha
Drawing a triangle in opengl with vertex attribute (colour)

"""

import pyglet
from pyglet import gl
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

# VERTICES

VAO = VertexArrayObject()
# vertices
vertices = VAO.createBuffer(data=((-0.6, -0.5, 0.1), (0.6, -0.5, 0.1), (0.0, 0.5, 0.1)))
vertices.connectToShader(location=0)
# colors
colors = VAO.createBuffer(data=((1,0,0),(0,1,0), (0,0,1)))
colors.connectToShader(location=1)

# RUN 

@window.event
def on_draw():
    gl.glClearColor(0.5, 0.6, 0.7, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    VAO.drawArrays()

gl.glEnable(gl.GL_MULTISAMPLE) # antialiasing
gl.glEnable(gl.GL_DEPTH_TEST) # 3d
pyglet.app.run()