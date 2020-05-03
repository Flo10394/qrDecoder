from distutils.command.config import config

from PIL import Image
import matplotlib.pyplot as plt
import time
import numpy as np
from helper import *
import math

for angle in range(1):
    ### Initialized picture ###########################################################################################
    ###################################################################################################################
    start = time.time()
    pilImage = Image.open("testdata/code2.jpg").crop((0, 0, 600, 800)).rotate(80)
    #pilImage = pilImage.resize((int(pilImage.size[0]/4), int(pilImage.size[1]/4)))
    im = np.asarray(pilImage) # crop and rotate
    im = np.mean(im, axis=2) # grayscale
    plt.ion()
    plt.show()
    plt.subplot(2, 2, 1)
    plt.title("input image")
    plt.imshow(im, cmap="gray", vmin=0, vmax=255)
    end = time.time()
    print("Init: {}".format(end-start))
    ###################################################################################################################
    ###################################################################################################################


    ### Image binarization ############################################################################################
    ###################################################################################################################
    start = time.time()
    ### binarize image ###
    image_bin = binarize(im, 128)
    plt.subplot(2, 2, 2)
    plt.title("binarized image")
    plt.imshow(image_bin, cmap="gray", vmin=0, vmax=255)
    end = time.time()
    print("Binarization: {}".format(end - start))
    ###################################################################################################################
    ###################################################################################################################

    ### find capstone candidates ######################################################################################
    ###################################################################################################################
    start = time.time()
    candidates = findCandidates(image_bin)  # contain center, left, right, top, bottom
    im_candidates = np.stack((image_bin,)*3, axis=-1)
    plt.subplot(2, 2, 3)
    plt.title("valid candidates")
    for el in candidates:
        drawCross(image=im_candidates, pixel=[el["center"][0], el["center"][1]], size=5, color=[200, 0, 0])
    plt.imshow(im_candidates, vmin=0, vmax=255)
    for i in range(len(candidates)):
        for j in range(len(candidates)):
            if candidates[i] != candidates[j] and candidates[i] != 0 and candidates[j] != 0:
                if((abs(candidates[i]["center"][0] - candidates[j]["center"][0]) < int(im_candidates.shape[0]/10))   and
                   (abs(candidates[i]["center"][1] - candidates[j]["center"][1]) < int(im_candidates.shape[1]/10))): # if there is a duplicate
                        candidates[i] = 0
    capstones = []
    for el in candidates:
        if el != 0:
            capstones.append(el)
    end = time.time()
    print("Find Candidates: {}".format(end - start))
    ###################################################################################################################
    ###################################################################################################################


    ### region growing (evaluate capstones) ###########################################################################
    ###################################################################################################################
    start = time.time()
    im_regions = np.stack((image_bin,)*3, axis=-1)
    plt.subplot(2, 2, 4)
    plt.title("regions")
    regions = getRegionsfromCandidates(image_bin, capstones)  # contain inner, outer region from candidate
    drawRegions(image=im_regions, regions=regions, colorInner=[0, 255, 0], colorOuter=[200, 0, 0])
    plt.imshow(im_regions, vmin=0, vmax=255)
    end = time.time()
    print("Region Growing: {}".format(end - start))
    ###################################################################################################################
    ###################################################################################################################

    if( len(capstones) != 3):
        print("angle ", angle, " problem")
    else:
        print("angle ", angle, "ok")
