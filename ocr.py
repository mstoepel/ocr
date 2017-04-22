import time
import pytesseract
import ConfigParser
import glob
import os
import sys
import json
import csv
import numpy as np
import pandas as pd
from PIL import Image

# print(pytesseract.image_to_string(im))
# print(pytesseract.image_to_string(im,config='digits'))
im = Image.open("C:/ML/datarole/Cropped/Owner/belleville_Page_002_box8.tiff")

fp = "C:/ML/datarole/Cropped/test/*.tiff"
fp2 = "C:/ML/datarole/Cropped/Owner/*.tiff"
fp3 = "C:/ML/datarole/Cropped/Location/*.tiff"
fp4 = "C:/ML/datarole/Cropped/Description/*.tiff"
fp5 = "C:/ML/datarole/Cropped/Construction_Value/*.tiff"
fp6 = "C:/ML/datarole/Cropped/Permit_Fee/*.tiff"

def ocr_run(fp,con):
    im = Image.open(fp)
    output = pytesseract.image_to_string(im,config=con)
    a = json.dumps(output)
    a = a.rstrip().split('\\n')
    for i in range(len(a)):
        a[i] = a[i].strip('"')
    while '' in a:
        a.remove('')
    # a = a[0]
    return a

start_time = time.time()
ocr_list_owner = [ocr_run(file,'psm 1') for file in sorted(glob.glob(fp2))]
print("--- Took %s seconds to complete OCR ---" % round((time.time() - start_time),2))
ocr_list_loc = [ocr_run(file,'psm 1') for file in sorted(glob.glob(fp3))]
ocr_list_desc = [ocr_run(file,'psm 1') for file in sorted(glob.glob(fp4))]
ocr_list_value = [ocr_run(file,'digits') for file in sorted(glob.glob(fp5))]
ocr_list_fee = [ocr_run(file,'digits') for file in sorted(glob.glob(fp6))]

df =  pd.DataFrame({'Owner':ocr_list_owner,'Location':ocr_list_loc,'Description':ocr_list_desc,'ConstructionValue':ocr_list_value,'PermitFee':ocr_list_fee})
df.to_csv("C:/ML/datarole/output.csv",index=False)


