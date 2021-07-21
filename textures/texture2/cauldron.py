# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 10:01:42 2021

@author: whmcilha

a library to help with Open GL incantations with vertex objects and buffers.
"""

import pyglet.gl as gl
import ctypes
import numpy as np
import numpy.ctypeslib as ctlib


class VertexArrayObject:
    # Vertex Array Object as an object
    def __init__(self):
        _vao = gl.GLuint(0)
        gl.glGenVertexArrays(1, ctypes.byref(_vao))
        self._vao = _vao
        self.buffers = []
        
    def __enter__(self):
        # binds the vertex array object 
        gl.glBindVertexArray(self._vao)
        return self
    
    def __exit__(self, extype, exvalue, extraceback):
        # releases the vertex array object
        gl.glBindVertexArray(0)
        
    def createBuffer(self, **kwargs):
        # creates a buffer object connected to self
        with self:
            buffer = _VertexBufferObject(self, **kwargs)
        self.buffers.append(buffer)
        return buffer
    
    def drawArrays(self, mode=gl.GL_TRIANGLE_STRIP, first=0, count=None):
        if count is None:
            count = self.buffers[0].n
        with self:
            gl.glDrawArrays(mode, first, count)
            

class _VertexBufferObject:
    # Vertex Buffer Object as an object
    def __init__(self, vao, target=gl.GL_ARRAY_BUFFER, usage=gl.GL_DYNAMIC_DRAW, data=None):
        self._vao = vao
        _vbo = gl.GLuint(0)
        gl.glGenBuffers(1, ctypes.byref(_vbo))
        self._vbo = _vbo
        self.target = target
        self.usage = usage
        if data is not None:
            self.setData(data)
            
    def __enter__(self):
        # binds the vertex array object 
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vbo)
        return self
    
    def __exit__(self, extype, exvalue, extraceback):
        # releases the vertex array object
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        
    def setData(self, data, target=None, usage=None):
        # puts the data in the buffer
        if type(data) in (list, tuple):
            data, self.size = py2ctypes(data)
        elif type(data) is np.ndarray:
            data, self.size = numpy2ctypes(data)
        self.n = len(data) # used when drawing
        target = target or self.target
        usage = usage or self.usage
        with self:
            gl.glBufferData(target, ctypes.sizeof(data), data, usage)
            
    def connectToShader(self, location, normalized=False):
        # enables a location in the shader & binds this buffer to it.
        # note that both the vao and self have to be in use for this to work.
        # If the location value isn't known, use <shader>.attributes.name.loc to get it
        with self._vao:
            with self:
                gl.glEnableVertexAttribArray(location)
                gl.glVertexAttribPointer(location, self.size, gl.GL_FLOAT, normalized, 0, 0)



# conversion routines to change lists, np arrays to the appropriate ctypes
# data for vertex buffers.

def find_ctype(data):
    # works out the nested ctype for the data, which
    # may be lists of lists
    if type(data) in (list, tuple):
        return find_ctype(data[0])*len(data)
    else:
        return gl.GLfloat
    
def tuplify(data):
    if type(data[0]) in (list, tuple):
        return tuple(tuplify(d) for d in data)
    else:
        return tuple(data)

def py2ctypes(data):
    # converts a list (or list of lists) to a ctypes array of arrays,
    # specifically for vertex data
    elemsize = len(data[0]) if type(data[0]) in (list, tuple) else 1
    data = (find_ctype(data))(*tuplify(data))
    return data, elemsize

# work out byte sizes and numpy format for glfloat
bytes = ctypes.sizeof(gl.GLfloat)
glfloat_dtype = np.dtype(f'f{bytes}')

def numpy2ctypes(data):
    # converts a numpy array of floats to a ctypes array
    # of GLfloat.
    # 1. work out size of glfloat & corresponding numpy format
    # 2. check type of data and convert to glfloat_dtype as needed
    if data.dtype!=glfloat_dtype:
        data = data.astype(glfloat_dtype)
    # 3. work out the elemsize
    elemsize = 1
    if data.ndim>1:
        elemsize = len(data[0])
    # 4. convert the data & return
    data = ctlib.as_ctypes(data)
    return data, elemsize

        
class TextureObject:
    def __init__(self, data=None):
        _tex = gl.GLuint(0)
        gl.glGenTextures(1, ctypes.byref(_tex))
        self._tex = _tex
        self.texunit = -1
        if data is not None:
            self.setData(data)
        
    def __enter__(self):
        # binds the vertex array object 
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._tex)
        return self
    
    def __exit__(self, extype, exvalue, extraceback):
        # releases the vertex array object
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def setData(self, data):
        # the data has to be a 2D array of rgb float, preferably float32
        if type(data) in (list, tuple):
            data, self.size = py2ctypes(data)
        elif type(data) is np.ndarray:
            data, self.size = numpy2ctypes(data)
        with self:
            level = 0
            border = 0
            width = self.size
            height = len(data)
            # Internal format GL_RGB32F should avoid clamping of inputs, so
            # contrasts can be used.
            gl.glTexImage2D(gl.GL_TEXTURE_2D, level, gl.GL_RGB32F, 
                            width, height, border, gl.GL_RGB, gl.GL_FLOAT, data)
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            
    def connectToShader(self, uniform):
        # sets up the shader connection prior to drawing.
        uloc = uniform.loc.value
        self.texunit = gl.GL_TEXTURE0+uloc
        gl.glActiveTexture(self.texunit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._tex) # bind it 
        # connect the shader uniform at uloc to the texture number TEXTURE0+uloc
        gl.glUniform1i(uloc, uloc)


    def disconnect(self):
        # makes this texture no longer active (probably)
        gl.glActiveTexture(self.texunit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        
    def free(self):
        # sometimes useful if running the program repeatedly
        gl.glDeleteTextures(1,ctypes.byref(self._tex))
