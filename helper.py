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

def binarizeSegments(image, div, thresh):
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
                    if(image[y*pixelperclustery + i, x*pixelperclusterx + j] >= image_segmented[y, x]/2):
                        image_bin[y*pixelperclustery + i, x*pixelperclusterx + j] = 255
                    else:
                        image_bin[y * pixelperclustery + i, x * pixelperclusterx + j] = 0


    return image_bin

def searchRow(line, y):
    sumblack = [[0, 0], [0, 0], [0, 0]]
    sumwhite = [[0, 0], [0, 0], [0, 0], [0, 0]]
    thresh = 5
    foundlist = []
    actualcolor = 0 if line[0] == 0 else 1  # init with first color
    borderpix = 3
    needToProof = 0

    for i in range(len(line)):
        if i == 292:
            dummy = 1
        if i == 309:
            dummy = 1

        if line[i] == 0:  # if pixel is black
            if(actualcolor == 1):  # here the color is changed from white to black
                actualcolor = 0

                # shift list to the left
                sumblack = deque(sumblack)
                sumblack.rotate(-1) # shift list to the left

                sumblack[2][1] = i  # save the index
                sumblack[2][0] = 0  # reset value

            sumblack[2][0] += 1

        else:  # if pixel is white
            if(actualcolor == 0):  # here the color is changed from black to white
                actualcolor = 1    # 1 if white

                # shift list to the left
                sumwhite = deque(sumwhite)
                sumwhite.rotate(-1)  # shift list to the left

                sumwhite[3][1] = i  # save the index
                sumwhite[3][0] = 0  # reset value

            sumwhite[3][0] += 1

        #  proof for 1:1:3:1:1 pattern
        if sumwhite[0][0] > borderpix:
            if sumwhite[1][0] != 0 and sumblack[1][0] != 0:
                if abs(sumwhite[1][0] - sumblack[0][0]) <= thresh:
                    if abs(3 * sumwhite[1][0] - sumblack[1][0]) <= 2*thresh:
                        if abs(3 * sumwhite[2][0] - sumblack[1][0]) <= 2*thresh:
                            if abs(sumwhite[2][0] - sumblack[2][0]) <= thresh:
                                if abs(sumwhite[3][0] - sumblack[2][0]) <= thresh:
                                    if(sumwhite[3][0] > borderpix):
                                        first = int( (sumwhite[1][1] + sumblack[0][1])/2 )
                                        second = int( (sumwhite[3][1] + sumblack[2][1])/2 )
                                        center = int( (first + second) / 2 )
                                        whitespacefirst = int(sumwhite[1][0])
                                        whitesapacesecond = int(sumwhite[2][0])
                                        patternLineResult = {"first": first,
                                                             "second": second,
                                                             "center": center,
                                                             "whitespacefirst": whitespacefirst,
                                                             "whitespacesecond": whitesapacesecond
                                                             }
                                        ## there is a pattern
                                        foundlist.append(patternLineResult)
                                        sumblack = [[0, 0], [0, 0], [0, 0]]
                                        sumwhite = [[0, 0], [0, 0], [0, 0], [0, 0]]

    return foundlist


def evalLine(line):
    sumwhite = 0
    sumblack = 0
    thresh = 2
    first = 1
    color = line[0]
    for pixel in line:
        if pixel != 0:
            sumwhite += 1  # here starts the white area
            if(color == 0):
                if not(first):
                    if(abs(sumwhite - sumblack) <= thresh):
                        # this is valid

                        return [1, int((sumblack + sumwhite) / 2)]
                    else:
                        return [0, 0]
                else:
                    sumblack = 0
                    first = 0
            color = 1
        else:
            sumblack += 1
            color = 0


def evaluateCandidate(image, pixel):
    ret = 0
    pixelperDot = [0, 0, 0, 0]
    thresh = 1
    # eval to the right
    line = image[pixel[0], pixel[1]:]
    res = evalLine(line)
    pixelperDot[0] = res[1]
    if res[0]: # eval to the right
        line = image[pixel[0], :pixel[1]]
        line = np.flip(line, 0)
        res = evalLine(line)
        pixelperDot[1] = res[1]
        if res[0]: # eval to the left
            line = image[:pixel[0], pixel[1]]
            line = np.flip(line, 0)
            res = evalLine(line)
            pixelperDot[2] = res[1]
            if res[0]:  # eval to the top
                line = image[pixel[0]:, pixel[1]]
                res = evalLine(line)
                pixelperDot[3] = res[1]
                if res[0]:  # eval to the bottom
                    ret = 1
                    for el in pixelperDot:
                        for el2 in pixelperDot:
                            if el != el2:
                                if el not in range(el2-thresh, el2+thresh):
                                    ret = 0
    return ret


def findCandidates(image):
    candidates = []

    for y in range(image.shape[0]):  # iterate over each horizontal line
        if(y == 345):
            a = 10
        patterns_x = searchRow(image[y, :], y)

        if len(patterns_x) > 0:  # if there are potential capstone patterns, check the column at the x-values, detected a 1:1:3:1:1 pattern
            for pattern_x in patterns_x:   # for every x value, a pattern was detected
                nexts = 5
                breaki = False
                for i in range(1, nexts):
                    if(y <= image.shape[1] - nexts):
                        if(searchRow(image[y+i, :], y+i) == []):
                            breaki = True
                if(breaki):
                    continue

                patterns_y = searchRow(image[:, pattern_x["center"]], y)   # search for the same pattern in y direction
                patterns_y[:] = (value for value in patterns_y if value["center"] in range(y - 20, y + 20))
                if len(patterns_y) > 0:  # there is a captone, pretty sure
                    nexts = 5
                    breaki = False
                    for i in range(-int(nexts/2), int(nexts/2)):
                        if (pattern_x["center"]+i < image.shape[0]):
                            if (searchRow(image[:, pattern_x["center"]+i], y) == []):
                                breaki = True
                    if (not(breaki)):
                        candidate = {
                            "center":   [patterns_y[0]["center"], pattern_x["center"]],
                            "top":      [patterns_y[0]["first"], pattern_x["center"]],
                            "bottom":   [patterns_y[0]["second"], pattern_x["center"]],
                            "left":     [patterns_y[0]["center"], pattern_x["first"]],
                            "right":    [patterns_y[0]["center"], pattern_x["second"]],
                            "whitespaceLeft":   int(pattern_x["whitespacefirst"]),
                            "whitespaceRight":  int(pattern_x["whitespacesecond"]),
                            "whitespaceTop":    int(patterns_y[0]["whitespacefirst"]),
                            "whitespaceBottom": int(patterns_y[0]["whitespacesecond"])
                        }
                        whitespace = candidate["whitespaceLeft"]
                        thresi = 2
                        if((candidate["whitespaceRight"]     in range(whitespace - thresi, whitespace + thresi)) and
                           (candidate["whitespaceTop"]       in range(whitespace - thresi, whitespace + thresi)) and
                           (candidate["whitespaceBottom"]    in range(whitespace - thresi, whitespace + thresi))):
                            if len(candidates) == 0:
                                candidates.append(candidate)
                            else:
                                add = True
                                for el in candidates:
                                    if((candidate["center"][0] in range(el["center"][0] - 30, el["center"][0] + 30)) and
                                       (candidate["center"][1] in range(el["center"][1] - 30, el["center"][1] + 30))):
                                        add = False
                                if(add):
                                    candidates.append(candidate)

                patterns_y.clear()
            patterns_x.clear()


    return candidates


    '''
                for el in patterns_x:
        pattern_y = searchRow(image[:, el])
        pattern_y[:] = (value for value in pattern_y if value in range(y-50, y+50))

        if len(pattern_y) > 0:  # there is a captone, pretty sure
            if([pattern_y[0], el] not in candidates):
                candidates.append([pattern_y[0], el])
        pattern_y.clear()
    patterns_x.clear()
    '''


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