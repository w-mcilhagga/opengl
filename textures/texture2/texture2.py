# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 16:08:25 2021

@author: whmcilha
Drawing a triangle in opengl with texturing, 
using the texture objects in cauldron.

"""

import pyglet
from pyglet import gl
import pyshaders
import numpy as np
from cauldron import VertexArrayObject, TextureObject

config = pyglet.gl.Config(sample_buffers=1, samples=4)
window = pyglet.window.Window(width=300, height=600, config=config)

# SHADERS - color and texture
# use texelfetch to treat a texture like an array.

def setup_program():
    
    vertex_shader = '''
        #version 300 es
        precision mediump float;
        layout(location = 0) in vec4 position;
        layout(location = 1) in vec2 tex_coord;

        out vec2 tcoord;
        uniform vec2 scale; // the x, y scales
        
        void main()
        {
            gl_Position = position/vec4(scale, 1.0, 1.0);
            tcoord = tex_coord;
        }
    '''

    fragment_shader = '''
        #version 300 es
        precision mediump float;
        
        in vec2 tcoord;
        out vec4 fColor;
        
        uniform int stripes;
        uniform sampler2D texture;
        uniform sampler2D texture1;
        uniform int activetextures;
                
        void main()
        {
            // maybe use texelFetch() for images
            if (activetextures==2) {
                fColor = mix(texture2D(texture,tcoord), texture2D(texture1,tcoord), 0.2);
            } else {
                fColor = texture2D(texture,tcoord);
            }
            if (stripes>1) {
                if (int(gl_FragCoord.x)%stripes==0) {
                    fColor = vec4(0,0,0,1);
                }  
            }
        }
    '''

    program = pyshaders.from_string(vertex_shader, fragment_shader)
    program.use()
    return program

program = setup_program()

# VERTICES

VAO = VertexArrayObject()
# vertices
vertices = VAO.createBuffer(data=(((-0.6, -0.5, 0.1), (0.6, -0.5, 0.1), 
                                  (0.6, 0.5, 0.1),(-0.6, 0.5, 0.1))))
vertices.connectToShader(location=0)

# texture coords mapping vertices to texture locations
texcoords = VAO.createBuffer(data=((0,0),(1,0),(1,1),(0,1)))
texcoords.connectToShader(location=1)

VAO2 = VertexArrayObject()
# vertices
_vertices = VAO2.createBuffer(data=(((-0.6+0.1, -0.5, 0.6), (0.6+0.1, -0.5, 0.6), 
                                  (0.6+0.1, 0.5, 0.6),(-0.6+0.1, 0.5, 0.6))))
_vertices.connectToShader(location=0)

# texture coords mapping vertices to texture locations
texcoords = VAO2.createBuffer(data=((0,0),(1,0),(1,1),(0,1)))
texcoords.connectToShader(location=1)


# TEXTURE

TEX = TextureObject()
TEX.setData(np.array( (((1,0,0),(0,1,0)),((0.5,0.5,0),(1,1,0)) ) ))

TEX2 = TextureObject()
TEX2.setData(np.random.rand(20,20,3))

TEX3 = TextureObject()
TEX3.setData(np.random.rand(10,10,3))

# RUN 
if window.width>window.height:
    program.uniforms.scale=[window.width/window.height,1]
else:
    program.uniforms.scale=[1, window.height/window.width]

@window.event
def on_draw():
    gl.glClearColor(0.5, 0.6, 0.7, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    TEX.connectToShader(program.uniforms['texture']) 
    TEX3.connectToShader(program.uniforms['texture1']) 
    program.uniforms.stripes = 10
    program.uniforms.activetextures = 2
    VAO.drawArrays(mode=gl.GL_TRIANGLE_FAN) 
    TEX.disconnect()
    TEX3.disconnect()
    # next image
    TEX2.setData(np.random.rand(20,20,3))
    TEX2.connectToShader(program.uniforms['texture']) 
    program.uniforms.stripes = 0
    program.uniforms.activetextures = 1
    VAO2.drawArrays(mode=gl.GL_TRIANGLE_FAN) 
    TEX2.disconnect()
    # can't unbind the texture...

dx = dy = 0
@window.event
def on_mouse_press(x,y,*args):
    # can't cope with scaling.
    global dx, dy, verts
    dx = (x-300)/300.0
    dy = (y-300)/300.0
    vertices.setData(((-0.6+dx, -0.5+dy, 0.1), (0.6+dx, -0.5+dy, 0.1), 
                     (0.6+dx, 0.5+dy, 0.1),(-0.6+dx, 0.5+dy, 0.1)))

    
gl.glEnable(gl.GL_DEPTH_TEST) # 3d
fn = lambda dt:0
pyglet.clock.schedule_interval(fn, 1/10)
pyglet.app.run()
pyglet.clock.unschedule(fn)

TEX.free()
TEX2.free()
TEX3.free()