import argparse
import cv2
import pandas as pd
from PIL import Image

clicks = []
refPt = []
cropping = False
imsize = (765,990)

def clicker(event,x,y,flags,param):
    global refPt, cropping

    if event == cv2.EVENT_LBUTTONDOWN:
        refPt =[(x,y)]
        cropping = True
    elif event == cv2.EVENT_LBUTTONUP:
        refPt.append((x,y))
        cropping=False

        cv2.rectangle(image,refPt[0], refPt[1], 0,2)
        cv2.imshow('image',image)

ap = argparse.ArgumentParser()
ap.add_argument("-i","--image",required=True,help="Path to the image")
args = vars(ap.parse_args())

image =  cv2.imread(args["image"],cv2.IMREAD_GRAYSCALE)
image = cv2.resize(image,imsize)
clone = image.copy()
cv2.namedWindow("image")
cv2.setMouseCallback("image",clicker)

while True:
    cv2.imshow("image",image)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("r"):
        image = clone.copy()

    elif key == ord("c"):
        clicks.append(refPt)

    elif key == ord("q"):
        break


img2 = Image.open(args["image"]).resize(imsize)
pixels = list(img2.getdata())
pix_str = ' '.join(str(p) for p in pixels)

new_df = pd.DataFrame({'filename':[args["image"][9:]],'owner_a':clicks[0][0][0],'owner_b':clicks[0][0][1],'owner_c':clicks[0][1][0],'owner_d':clicks[0][1][1],'loc_a':clicks[1][0][0],'loc_b':clicks[1][0][1],'loc_c':clicks[1][1][0],
                       'loc_d':clicks[1][1][1],'desc_a':clicks[2][0][0],'desc_b':clicks[2][0][1],'desc_c':clicks[2][1][0],'desc_d':clicks[2][1][1],'val_a':clicks[3][0][0],'val_b':clicks[3][0][1],'val_c':clicks[3][1][0],
                       'val_d':clicks[3][1][1],'fee_a':clicks[4][0][0],'fee_b':clicks[4][0][1],'fee_c':clicks[4][1][0],'fee_d':clicks[4][1][1],'pixels':pix_str})

# new_df.to_csv("C:/ML/datarole/training.csv",index=False)

df = pd.read_csv("C:/ML/datarole/training.csv")
df = df.append(new_df)
df.to_csv("C:/ML/datarole/training.csv",index=False)
# print(pix_str)
print(len(pix_str))
# print(len(image.tolist()))
print(new_df.head())

cv2.destroyAllWindows()