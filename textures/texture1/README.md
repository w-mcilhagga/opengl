# texture1.py

This file adds texturing to a *rectangle*, just for a change. The `cauldron` library is used to make things easier, but the texture code is pure Open GL (as seen via pyglet). The first part of the program is as usual:

```python
import pyglet
from pyglet import gl
import ctypes
import pyshaders
import numpy as np
from cauldron import VertexArrayObject


window = pyglet.window.Window(width=600, height=600)
```
The vertex shader has changed a little. There is now a texture coordinate `tex_coord` passed in with each vertex (we'll see how later), and this is just passed on to the fragment shader by being copied to `tcoord`

```python
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
```
The fragment shader changes too. It takes a texture coordinate `tcoord` from the fragment shader. This has been interpolated between the values at the vertices. It uses that coordinate to look up a texture which is passed in as a uniform sampler variable.

```python
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
```
Next, we set up the vertices using cauldron. There are now four vertices for the four corners of the rectangle. We don't bother giving these vertices colours because the rectangle will be textured anyway. We also pass in the texture coordinates in a buffer `texcoords`, which connects yup to location 1 in the shader.

Each texture coordinate says where, in the texture, you should look for the colour of the pixel. So vertex `(-0.6, -0.5, 0.1)` corresponds to texture location `(0,0)`, and vertex `(0.6, 0.5, 0.1)` to texture location `(1,1)`.

```python
# VERTICES

VAO = VertexArrayObject()
# vertices
vertices = VAO.createBuffer(data=np.array(((-0.6, -0.5, 0.1), (0.6, -0.5, 0.1), 
                                  (0.6, 0.5, 0.1),(-0.6, 0.5, 0.1))))
vertices.connectToShader(location=0)
# texture coords mapping vertices to texture locations
texcoords = VAO.createBuffer(data=((0,0),(1,0),(1,1),(0,1)))
texcoords.connectToShader(location=1)
```
Now we define the texture. This uses a combination of Open GL and ctypes. The texture is just four pixels.

```python
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

```
The texture is created and then bound (made the current texture). Then the image data is loaded into it with the call to `glTexImage`.

A four pixel texture is going to have trouble filling up the rectangle, so we need to define what to do to magnify it or minify it.

```python
gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR);
gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST);
gl.glBindTexture(gl.GL_TEXTURE_2D, 0) # unbind it
```

Let's run it. 

```python

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
```
Lines 3-7 in the draw routine are used to connect the texture to the shader. This probably only has to be done once if you only have one texture, but otherwise, it goes in the `on_draw`. A number of things happen:
1. We activate one of the many predefined "texture units" with `gl.glActiveTexture(gl.GL_TEXTURE0)`.
2. We make our texture active with `gl.glBindTexture(gl.GL_TEXTURE_2D, TEX)`. Note that changing the order of steps 1 and 2 doesn't seem to affect anything.
3. We now connect the texture unit `gl.GL_TEXTURE0` to the uniform. First we find the uniform's location with `program.uniforms['texture'].loc.value`
4. Then we say that the uniform at that location is connected to texture unit 0 with `gl.glUniform1i(uloc, 0)`; why this particular call should do this is beyond me.

Anyway that's it, and it runs.

```python
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
```

