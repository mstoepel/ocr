from PIL import Image
import numpy as np
from ast import literal_eval

path = "C:/ML/datarole/grid/"
path1 = "C:/ML/datarole/grid/image.tiff"
path2 = "C:/ML/datarole/grid/image_grid.tiff"

dim = raw_input('Dimensions: ')
dim = literal_eval(dim)

im = Image.open(path1).resize(dim, Image.ANTIALIAS)
im = im.convert('RGB')

img = np.asanyarray(im)
img.flags.writeable = True

for i in range(500,max(dim),500):
    img[i:i+10,:] = 0
    img[:,i:i+10] = 0

img = Image.fromarray(img)

img.save(path2,"TIFF")
