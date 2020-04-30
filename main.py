from distutils.command.config import config

from PIL import Image
import matplotlib.pyplot as plt
import time
import numpy as np
from helper import *
import math


### crop the image to 1000x500 pixel ###
im = np.asarray(Image.open("testdata/code.jpg").crop((0, 0, 550, 550)).rotate(120))
im = np.mean(im, axis=2)
#defines
XSIZE = im.shape[1]
YSIZE = im.shape[0]
# acess image pixel value at (x,y) with image[y][x]



### binarize image ###
image_bin = binarizeSegments(image=im, div=10, thresh=10)

#plt.ion()
#plt.imshow(image_bin, cmap="gray")
#plt.show()


candidates = findCandidates(image_bin)  # contain center, left, right, top, bottom

regions = getRegionsfromCandidates(image_bin, candidates)  # contain inner, outer region from candidate
capstones = getCapstonesFromRegions(image_bin, regions)

im_edit = np.stack((image_bin,)*3, axis=-1)

drawRegions(image=im_edit, regions=regions, colorInner=[0, 255, 0], colorOuter=[255, 0, 0])

for el in candidates:
    drawCross(image=im_edit, pixel=el["center"], size=5, color=[255, 0, 0])
#plt.ion()
#plt.imshow(im_edit)


plt.ioff()
plt.imshow(im_edit)
plt.show()