import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from collections import namedtuple

def rgb2gray(image):
    retImage = np.array(object=np.zeros(shape=(image.shape[0], image.shape[1]), dtype=np.uint8), dtype=np.uint8)
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            for i in range(3):
                retImage[x][y] += image[x][y][i]/3

def convolution2D(image, x, y, operator, a, n):
    pixout = 0
    if(x < image.shape[1]-3 and y < image.shape[0]-3):
        pic = image[y:y+3, x:x+3]
        res = np.mean(pic * operator)
        if(res < 0):
            res = 0
        return res
    else:
        return image[y][x]

def binarize(image, thresh):
    image_bin = np.zeros((image.shape[0], image.shape[1]))
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            if(image[y][x] >= thresh):
                image_bin[y][x] = 255
            else:
                image_bin[y][x] = 0
    return image_bin

def binarizeSegments(image, div, treshfactor):
    image_bin = np.zeros((image.shape[0], image.shape[1]))
    pixelperclustery = int(image.shape[0]/div)
    pixelperclusterx = int(image.shape[1]/div)
    image_segmented = np.zeros((div, div))

    # calculate mean value of all segments
    for y in range(image_segmented.shape[0]):
        for x in range(image_segmented.shape[1]):
            xstart = x*pixelperclusterx
            ystart = y*pixelperclustery
            image_segmented[y, x] = np.mean(image[ystart:ystart+pixelperclustery, xstart:xstart+pixelperclusterx])
            for i in range(pixelperclustery):
                for j in range(pixelperclusterx):
                    if(image[y*pixelperclustery + i, x*pixelperclusterx + j] >= treshfactor*image_segmented[y, x]): # if pixel is brighter than tresh from region, set it white
                        image_bin[y*pixelperclustery + i, x*pixelperclusterx + j] = 255
                    else:
                        image_bin[y * pixelperclustery + i, x * pixelperclusterx + j] = 0 # if pixel is darker than thresh from region, set it black


    return image_bin

def sameSize(elems, thresh):
    retVal = True
    for i in range(len(elems)):
        for j in range(len(elems)):
            if i != j:
                if elems[i] not in range (elems[j] - thresh, elems[j] + thresh):
                    reVal = False
    return retVal

def searchRow(line, thresh):
    sumblack = [[0, 0], [0, 0], [0, 0]]
    sumwhite = [[0, 0], [0, 0], [0, 0], [0, 0]]
    foundlist = []
    actualcolor = 0 if line[0] == 0 else 1  # init with first color
    checkPattern = False

    for i in range(len(line)):
        if line[i] == 0:  # if pixel is black
            if(actualcolor == 1):  # here the color is changed from white to black
                actualcolor = 0
                checkPattern = False

                # shift list to the left
                sumblack = deque(sumblack)
                sumblack.rotate(-1) # shift list to the left

                sumblack[2][1] = i  # save the index
                sumblack[2][0] = 0  # reset value

            sumblack[2][0] += 1

        else:  # if pixel is white
            if(actualcolor == 0):  # here the color is changed from black to white
                actualcolor = 1    # 1 if white
                checkPattern = True

                # shift list to the left
                sumwhite = deque(sumwhite)
                sumwhite.rotate(-1)  # shift list to the left

                sumwhite[3][1] = i  # save the index
                sumwhite[3][0] = 0  # reset value

            sumwhite[3][0] += 1

        # check for 1:1:3:1:1 pattern
        if(sumblack[0][0] != 0 and sumblack[1][0] != 0 and sumblack[2][0] != 0 and checkPattern and
           sumwhite[0][0] != 0 and sumwhite[1][0] != 0 and sumwhite[2][0] != 0 and sumwhite[3][0] != 0): # if we measured anything
            if(sumwhite[3][0] >= sumblack[2][0]-thresh):   # if the last white area is greater or equal than the last black area
                if(sumblack[1][0] >= 10): # if the inner capsonte area (black) contains more than 10 pixels
                    if(abs(sumwhite[1][0] - sumwhite[2][0]) <= thresh): #if the inner white area is the same size
                        if ((abs(sumblack[1][0] - 3 * sumwhite[1][0]) <= 5 * thresh) and (abs(sumblack[1][0] - 3 * sumwhite[2][0]) <= 5 * thresh)):  # if middle capstone is 3 * white inner region
                            if ((abs(sumwhite[1][0] - sumblack[0][0]) <= thresh) and (abs(sumwhite[2][0] - sumblack[2][0]) <= thresh)):  # if outer border is the same size as inner border
                                if (((sumwhite[0][0] - sumblack[0][0]) >= -thresh) and ((sumwhite[3][0] - sumblack[2][0]) >= -thresh)):  # this is a valid capstone pattern
                                    first = int((sumwhite[1][1] + sumblack[0][1]) / 2)
                                    second = int((sumwhite[3][1] + sumblack[2][1]) / 2)
                                    center = int((first + second) / 2)
                                    whitespacefirst = int(sumwhite[1][0])
                                    whitesapacesecond = int(sumwhite[2][0])
                                    patternLineResult = {"first": first,
                                                         "second": second,
                                                         "center": center,
                                                         "whitespacefirst": whitespacefirst,
                                                         "whitespacesecond": whitesapacesecond
                                                         }
                                    ## there is a pattern
                                    if(sameSize([whitespacefirst, whitesapacesecond], thresh)):
                                        foundlist.append(patternLineResult)
                                        sumblack = [[0, 0], [0, 0], [0, 0]]
                                        sumwhite = [[0, 0], [0, 0], [0, 0], [0, 0]]

    return foundlist

def findCandidates(image):
    thresh = 3

    candidates = []
    for y in range(image.shape[0]):  # check every image row for a 1:1:3:1:1 pattern
        patterns_x = searchRow(image[y, :], thresh)
        if(len(patterns_x) > 0):
            for pattern_x in patterns_x:
                patterns_y = searchRow(image[:, pattern_x["center"]], thresh)
                if(len(patterns_y) > 0):
                    for pattern_y in patterns_y:
                        if(pattern_y["center"] in range(y-10,y+10)):
                            candidate = {
                            "center":   [pattern_y["center"], pattern_x["center"]],
                            "top":      [pattern_y["first"],  pattern_x["center"]],
                            "bottom":   [pattern_y["second"], pattern_x["center"]],
                            "left":     [pattern_y["center"], pattern_x["first"]],
                            "right":    [pattern_y["center"], pattern_x["second"]],
                            "whitespaceLeft":   int(pattern_x["whitespacefirst"]),
                            "whitespaceRight":  int(pattern_x["whitespacesecond"]),
                            "whitespaceTop":    int(pattern_y["whitespacefirst"]),
                            "whitespaceBottom": int(pattern_y["whitespacesecond"])}
                            if(candidate["whitespaceLeft"] > 0 and candidate["whitespaceRight"] > 0 and candidate["whitespaceTop"] > 0 and candidate["whitespaceBottom"] > 0):
                                if( sameSize(elems=[candidate["whitespaceLeft"], candidate["whitespaceRight"], candidate["whitespaceTop"], candidate["whitespaceBottom"]], thresh=thresh)):
                                    if(candidate not in candidates):
                                        candidates.append(candidate)
                    patterns_y.clear()
            patterns_x.clear()
                #check for 1:1:3:1:1 pattern in y direction
    return candidates

def processPixel(image, x, y, toAnalyze, regionPixelList):
    if (x in range(0, image.shape[1]) and y in range(0, image.shape[0])):
        if image[y][x] == 0:  # if pixel is black
            if [y, x] not in regionPixelList:
                if [y, x] not in toAnalyze:
                    toAnalyze.append([y, x])

def checkPixelNeighbours(image, pixel, regionPixelList, toAnalyze):
    x = pixel[1]
    y = pixel[0]

    # check right pixel
    x += 1
    processPixel(image=image, x=x, y=y, regionPixelList=regionPixelList, toAnalyze=toAnalyze)

    # check top pixel
    x -= 1
    y -= 1
    processPixel(image=image, x=x, y=y, regionPixelList=regionPixelList, toAnalyze=toAnalyze)

    # check bottom pixel
    y += 2
    processPixel(image=image, x=x, y=y, regionPixelList=regionPixelList, toAnalyze=toAnalyze)

    # check left pixel
    y -= 1
    x -= 1
    processPixel(image=image, x=x, y=y, regionPixelList=regionPixelList, toAnalyze=toAnalyze)

def getRegionfromPixel(image, pixel):
    pixellist = []
    toAnalyze = []
    checkPixelNeighbours(image, pixel, pixellist, toAnalyze)
    pixellist.append(pixel)
    while len(toAnalyze) > 0:
        if (toAnalyze[0] not in pixellist):
            checkPixelNeighbours(image, toAnalyze[0], pixellist, toAnalyze)
            pixellist.append(toAnalyze[0])
            toAnalyze.remove(toAnalyze[0])
        else:
            toAnalyze.remove(toAnalyze[0])
    return pixellist

def getRegionsfromCandidates(image, candidates):
    regionList = []
    for candidate in candidates:
        innerRegion = getRegionfromPixel(image, candidate["center"])
        outerRegionLeft = getRegionfromPixel(image, candidate["left"])
        outerRegionRight = getRegionfromPixel(image, candidate["right"])
        outerRegionLeft.sort()
        outerRegionRight.sort()


        if(outerRegionLeft == outerRegionRight):  # this is valid
            region = {
                "inner": innerRegion,
                "outer": outerRegionLeft
            }
            regionList.append(region)
    return regionList

def calculateMainEmphasis(image, region):
    x = 0
    y = 0
    for pixel in region:
        y += pixel[0]
        x += pixel[1]
    y /= len(region)
    x /= len(region)
    return [y, x]

def getCapstonesFromRegions(image, regions):
    capstones = []
    for region in regions:
        # region contains inner and outer region
        # calculate inner
        innerMainEmphasis = calculateMainEmphasis(image, region["inner"])
        outerMainEmphasis = calculateMainEmphasis(image, region["outer"])

        if((int(innerMainEmphasis[0]) in range(int(outerMainEmphasis[0] - 5), int(outerMainEmphasis[0] + 5) )) and
           (int(innerMainEmphasis[1]) in range(int(outerMainEmphasis[1] - 5), int(outerMainEmphasis[1] + 5)))):
            capstones.append([int(innerMainEmphasis[0]), int(innerMainEmphasis[1])])

    return capstones

def drawCross(image, pixel, size, color):
    y = pixel[0]
    x = pixel[1]

    for i in range(x-size, x+size):
        image[y, i, :] = color
    for i in range(y-size, y+size):
        image[i, x, :] = color

def drawRegions(image, regions, colorInner, colorOuter):
    for region in regions:
        for pixel in region["inner"]:
            image[pixel[0]][pixel[1]] = colorInner
        for pixel in region["outer"]:
            image[pixel[0]][pixel[1]] = colorOuter