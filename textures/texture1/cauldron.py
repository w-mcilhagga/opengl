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
        if type(data) is np.ndarray:
            data, self.size = numpy2ctypes(data)
        self.n = len(data)
        target = target or self.target
        usage = usage or self.usage
        with self:
            gl.glBufferData(target, ctypes.sizeof(data), data, usage)
            
    def connectToShader(self, location, normalized=False):
        # enables a location in the shader & binds this buffer to it.
        # note that both the vao and self have to be in use for this to work.
        # If the location value isn't known, use shader.attribute.name.loc to get it
        with self._vao:
            with self:
                gl.glEnableVertexAttribArray(location)
                gl.glVertexAttribPointer(location, self.size, gl.GL_FLOAT, normalized, 0, 0)



# conversion routines to change lists, np arrays to the appropriate ctypes
# data for vertex buffers.
    
def py2ctypes(data):
    # converts a list (or list of lists) to a ctypes array of arrays,
    # specifically for vertex data
    n = len(data)
    elemsize = 1
    if type(data[0]) in (list, tuple):
        elemsize = len(data[0])
        if type(data) is list:
            # ctypes objects accept tuples but not lists,
            # so have to change it.
            data = tuple(tuple(item) for item in data)
    if elemsize==1:
        data = (gl.GLfloat*n)(*data)
    else:
        elem = gl.GLfloat*elemsize
        data = (elem*n)(*data)
    return data, elemsize

def numpy2ctypes(data):
    # converts a numpy array of floats to a ctypes array
    # of GLfloat.
    # 1. work out size of glfloat & corresponding numpy format
    bytes = ctypes.sizeof(gl.GLfloat)
    glfmt = np.dtype(f'f{bytes}')
    # 2. check type of data and convert to glfmt as needed
    if data.dtype!=glfmt:
        data = data.astype(glfmt)
    # 3. work out the elemsize
    elemsize = 1
    if data.ndim>1:
        elemsize = len(data[0])
    # 4. convert the data & return
    data = ctlib.as_ctypes(data)
    return data, elemsize

        