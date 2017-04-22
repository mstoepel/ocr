import time
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter
from PIL import ImageOps
import glob
import os
import sys

path = "C:/ML/datarole/"
path1 = "C:/ML/datarole/images/*.tif*"
path2 = "C:/ML/datarole/Cropped/"
path3 = "C:/ML/datarole/Cropped/Owner/"
path4 = "C:/ML/datarole/Cropped/Location/"
path5 = "C:/ML/datarole/Cropped/Description/"
path6 = "C:/ML/datarole/Cropped/Construction_Value/"
path7 = "C:/ML/datarole/Cropped/Permit_Fee/"

if not os.path.exists(path2):
    create = raw_input('This project does not exist. Would you like to create it?: ').lower()
    if create in ('y','yes'):
        os.makedirs(path2)
        os.makedirs(path3)
        os.makedirs(path4)
        os.makedirs(path5)
        os.makedirs(path6)
        os.makedirs(path7)
    else:
        print('Exiting.')
        sys.exit()

start_time = time.time()
quality_val = 95

owner_box = [(800,((i*350)+500),1900,((i*350)+850)) for i in range(14)]
loc_box = [(1900,((i*350)+500),2750,((i*350)+850)) for i in range(14)]
desc_box = [(2750,((i*350)+500),3900,((i*350)+850)) for i in range(14)]
value_box = [(3900,((i*350)+500),4350,((i*350)+850)) for i in range(14)]
fee_box = [(4350,((i*350)+500),5000,((i*350)+850)) for i in range(14)]

boxes = [owner_box,loc_box,desc_box,value_box,fee_box]

def img_proc(img,box,out):
    im_crop = img.crop(box)
    enhancer = ImageEnhance.Brightness(im_crop)
    im_crop = enhancer.enhance(1.4)
    im_crop.save(out,"TIFF",quality_val=quality_val,dpi=(300,300))

# def outfile_path(f,j):
#     outfile_path = path2 + f[len(f)-19:len(f)] + "_box" + str(j+1) + e
#     return outfile_path

for i, filename in enumerate(sorted(glob.glob(path1))):
    f, e = os.path.splitext(filename)
    owner_outfile = [f[0:len(f)-26] + "Cropped/Owner/" + f[len(f)-19:len(f)] + "_box" + str(j+1).zfill(2) + e for j in range(len(owner_box))]
    loc_outfile = [f[0:len(f)-26] + "Cropped/Location/" + f[len(f)-19:len(f)] + "_box" + str(j+1).zfill(2) + e for j in range(len(loc_box))]
    desc_outfile = [f[0:len(f) - 26] + "Cropped/Description/" + f[len(f) - 19:len(f)] + "_box" + str(j + 1).zfill(2) + e for j in range(len(desc_box))]
    value_outfile = [f[0:len(f) - 26] + "Cropped/Construction_Value/" + f[len(f) - 19:len(f)] + "_box" + str(j + 1).zfill(2) + e for j in range(len(value_box))]
    fee_outfile = [f[0:len(f) - 26] + "Cropped/Permit_Fee/" + f[len(f) - 19:len(f)] + "_box" + str(j + 1).zfill(2) + e for j in range(len(fee_box))]
    im = Image.open(filename)

    [img_proc(im,owner_box[j],owner_outfile[j]) for j in range(len(owner_box))]
    [img_proc(im,loc_box[j],loc_outfile[j]) for j in range(len(loc_box))]
    [img_proc(im,desc_box[j],desc_outfile[j]) for j in range(len(desc_box))]
    [img_proc(im,value_box[j],value_outfile[j]) for j in range(len(value_box))]
    [img_proc(im,fee_box[j],fee_outfile[j]) for j in range(len(fee_box))]


print("--- Took %s seconds to complete cropping ---" % round((time.time() - start_time),2))

