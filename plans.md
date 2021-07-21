# Window, etc.

This is much as before, with just a bit extra to make sure the opengl
context is setup right, and that we can switch ticks on/off correctly.

# Drawables:

## Rect:
```python
Rect(centre, width, height, color)
Rect(top, left, bottom, right, color)
```
Draws a rectangle.

## Background:
```python
Background(color)
```
The values r,g,b are floating point and will be interpreted according to the
pixel pipeline. Background is just `Rect(1,-1,-1,1,color)` with the z-location
set to 0.999

## Lines:
```python
Lines(color, lines, thickness)
```

## Image:
```python
Image(centre, rotate, data)
```
The data has to be n*m*3 or maybe n*m*4. It is displayed pixel for pixel. The
centre is adjusted minimally to suit this. If rotate is not zero, however, you
will get resampling. Centre can be (x,y) or (x,y,z). If no z coord, it is set to 
0.5

## ImageStack:
```python
Image(centre, rotate, data, composite, composite, ...)
```
This way of calling `Image` lets you blend a series of images onto the base
image, using the mode. A composite is a pair `(mode, data)` or `(mode, function)`. 
Mode will be e.g. add, multiply. A function is a scalar function of space & time,
which can be used to define spatial patterns or temporal envelopes. Eventually
the function will be traceable and reconstructed by the fragment shader from
a stack.

All the images need to be the same size, depth, etc. The idea is to allow an
image to be composited from a set of existing images. Also, we should be able
to change an image intensity as a function of time in the shader.


# Pixel Pipeline.

The colours specified by the drawable is a float. It is interpreted by the 
following calls:

## Contrast
```python
Contrast(br,bg,bb)
```
This says that all GL intensities are contrasts against the background 
level `(br,bg,bb)` which is in the range 0...1. Contrasts (in the range
-1...(1/background)-1 are converted to
intensities by the equation `intensity = (contrast+1)*background`.

If omitted, it is assumed `intensity=contrast`.

## ColourModel
```python
ColourModel(mat)
```
Converts the intensities to RGB by multiplying by the matrix. Useful for
cone contrast calculations. If omitted, an identity matrix is assumed.

## Gamma
```python
Gamma(exponent|lookup)
```
Does gamma correction.

## Device
```python
Device('mono++', 'color++')
```
Does pixel munging for the device in question. Nothing happens if not specified.
If mono++ used, only the first channel is used to signal intensity. If color++
is used, adjacent pixels should have the same value.


