# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 16:08:25 2021

@author: whmcilha
Drawing a triangle in opengl with texturing

opengl area is -1...1 x and y, 0..1 z
"""

import pyglet
from pyglet import gl
import ctypes
import pyshaders

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
            fColor = texture2D(texture, tcoord);
        }
    '''

    program = pyshaders.from_string(vertex_shader, fragment_shader)
    program.use()
    return program

program = setup_program()

print(program.attributes.position.loc, program.attributes.tex_coord.loc)
# VERTICES

VAO = gl.GLuint(0)
VBO = gl.GLuint(0)
TBO = gl.GLuint(0)

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

# unbind it
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0) 

# create the texture coordinates for the triangle

TEX = gl.GLfloat*2;

gl.glGenBuffers(1, ctypes.byref(TBO)) # creates a handle to a VBO object
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, TBO) # makes the buffer currently active

# make data and put in buffer

texcoords = (TEX * 3)((0,0),(1,0), (0.5,1))
gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(texcoords), texcoords, gl.GL_DYNAMIC_DRAW)

# connect the buffer to location=1

gl.glEnableVertexAttribArray(1) # like pyshaders.attr.enable()
gl.glVertexAttribPointer(1, len(TEX()), gl.GL_FLOAT, False, ctypes.sizeof(TEX), 0)

# unbind it
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0) 

gl.glBindVertexArray(0) # unbinds the VAO we were using

# TEXTURE

TEXO = gl.GLuint(0)

PIXEL = gl.GLfloat*3

mytex = (PIXEL*4)((1,0,0),(0,1,0),(0.5,0.5,0),(1,1,0))

gl.glGenTextures(1, ctypes.byref(TEXO))
gl.glBindTexture(gl.GL_TEXTURE_2D, TEXO)
gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, 2, 2, 0, gl.GL_RGB, 
                gl.GL_FLOAT, mytex);
gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR);
gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST);
gl.glBindTexture(gl.GL_TEXTURE_2D, 0) # unbind it

# bind the texture to a uniform in the shader.
program.uniforms.texture = TEXO

# RUN 

@window.event
def on_draw():
    gl.glClearColor(0.5, 0.6, 0.7, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glBindVertexArray(VAO)
    gl.glActiveTexture(gl.GL_TEXTURE0)
    gl.glBindTexture(gl.GL_TEXTURE_2D, TEXO) # bind it again
    # draw starts everything happening:
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(verts)) 
    gl.glBindVertexArray(0)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0) # unbind it again

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