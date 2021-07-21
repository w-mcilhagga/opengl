# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 16:08:25 2021

@author: whmcilha
Drawing a triangle in opengl with texturing

"""

import pyglet
from pyglet import gl
import ctypes
import pyshaders
import numpy as np
from cauldron import VertexArrayObject


window = pyglet.window.Window(width=600, height=600)

# SHADERS - color and texture

def setup_program():
    
    vertex_shader = '''
        #version 300 es
        precision mediump float;
        layout(location = 0) in vec4 position;
        layout(location = 1) in vec2 tex_coord;

        out vec2 tcoord ;
        
        void main()
        {
            gl_Position = position;
            tcoord = tex_coord;
        }
    '''

    fragment_shader = '''
        #version 300 es
        precision mediump float;
        
        in vec2 tcoord;
        out vec4 fColor;
        uniform sampler2D texture;
        
        void main()
        {
            fColor = texture2D(texture,tcoord);
        }
    '''

    program = pyshaders.from_string(vertex_shader, fragment_shader)
    program.use()
    return program

program = setup_program()

# VERTICES

VAO = VertexArrayObject()
# vertices
vertices = VAO.createBuffer(data=np.array(((-0.6, -0.5, 0.1), (0.6, -0.5, 0.1), 
                                  (0.6, 0.5, 0.1),(-0.6, 0.5, 0.1))))
vertices.connectToShader(location=0)
# texture coords mapping vertices to texture locations
texcoords = VAO.createBuffer(data=((0,0),(1,0),(1,1),(0,1)))
texcoords.connectToShader(location=1)

# TEXTURE

TEX = gl.GLuint(0)

PIXEL = gl.GLfloat*3

mytex = (PIXEL*4)((1,0,0),(0,1,0),(0.5,0.5,0),(1,1,0))

gl.glGenTextures(1, ctypes.byref(TEX))
gl.glBindTexture(gl.GL_TEXTURE_2D, TEX)

# textimage makes the texture mutable, texstorage makes it immutable
# (in terms of width, height, internal format but not data)
# but texstorage needs another call to set the data, so even more 
# complicated
gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, 2, 2, 0, gl.GL_RGB, 
                gl.GL_FLOAT, mytex);
gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR);
gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST);
gl.glBindTexture(gl.GL_TEXTURE_2D, 0) # unbind it

# RUN 

@window.event
def on_draw():
    gl.glClearColor(0.5, 0.6, 0.7, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glActiveTexture(gl.GL_TEXTURE0)
    gl.glBindTexture(gl.GL_TEXTURE_2D, TEX) # bind it 
    # connect the shader uniform to the texture unit 0, aka TEXTURE0
    uloc = program.uniforms['texture'].loc.value
    gl.glUniform1i(uloc, 0)
    VAO.drawArrays(mode=gl.GL_TRIANGLE_FAN) 
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0) # unbind it 

dx = dy = 0
@window.event
def on_mouse_press(x,y,*args):
    global dx, dy, verts
    dx = (x-300)/300.0
    dy = (y-300)/300.0
    vertices.setData(((-0.6+dx, -0.5+dy, 0.1), (0.6+dx, -0.5+dy, 0.1), 
                     (0.6+dx, 0.5+dy, 0.1),(-0.6+dx, 0.5+dy, 0.1)))

    
gl.glEnable(gl.GL_DEPTH_TEST) # 3d
pyglet.app.run()