# coding: utf-8
import numpy as np
import cv2
import sys
import math
import matplotlib.pyplot as plt

BLOCK_SIZE = 512


# return the new size of the image, which must be a multiple of BLOCK_SIZE
def getcorrectsize(oldSize):
    return oldSize - oldSize%BLOCK_SIZE


# return a block from the image. each block has a size of (BLOCK_SIZE, BLOCK_SIZE)
def getblock(image, col, row):
    return image[row * BLOCK_SIZE : (row+1) * BLOCK_SIZE, col * BLOCK_SIZE : (col+1) * BLOCK_SIZE]


# load the image from path. imType can be:
#   cv2.CV_LOAD_IMAGE_COLOR, cv2.CV_LOAD_IMAGE_GRAYSCALE, cv2.CV_LOAD_IMAGE_UNCHANGED
# dataType can be :
#   np.float32, np.float64, np.uint8, np.int32, ...
def loadImage(path, imtype = cv2.CV_LOAD_IMAGE_UNCHANGED, datatype = np.uint8):
    print "Loading image:", path
    image = cv2.imread(path, imtype)

    if(image is None):
        raise IOError("Couldn't open image: " + sys.argv[1])

    return image.astype(datatype)


# show the log of the histogram of matrix.
def showLogHistogram(matrix, label):
    plt.figure("Log Histogram")

    for m, l in zip(matrix, label):
        plt.hist( m.ravel(), bins=50, label=l)

    plt.legend()
    ax = plt.subplot(1,1,1)
    ax.set_yscale('log')
    plt.show()

# return the value of the angle between (0, PI)
def normAngle( angle ):
    while angle > math.pi:
        angle -= math.pi

    while angle < 0:
        angle += math.pi

    return angle

# estimate the angle using the gradient of the image dx and dy, using the mask (non zero values are weight)
def estimateAngle(dx, dy, mask):
    candidates = np.where( mask > 0)
    angles = np.zeros_like(mask, dtype=np.float32)

    for row,col in zip(candidates[0], candidates[1]):
        angles[row, col] = normAngle( math.atan2(dy[row, col], dx[row, col]) - math.pi / 2.0 )

    angleHisto = cv2.calcHist([angles], [0], mask=mask, histSize=[100], ranges=(0, math.pi) )

    posMax = np.argmax(angleHisto)
    finalAngle = math.pi * posMax / 100
    return finalAngle


def drawvector(im, pos, angle):
    col,row = pos
    center = ( int( (col + 0.5) * BLOCK_SIZE), int( (row + 0.5) * BLOCK_SIZE) )
    length = BLOCK_SIZE / 4
    beginOfLine = ( int(center[0] - math.cos(angle) * length), int(center[1] - math.sin(angle) * length))
    endOfLine = ( int(center[0] + math.cos(angle) * length), int(center[1] + math.sin(angle) * length))
    cv2.line(im, beginOfLine, endOfLine, (255, 0, 0), 5 )

# return a mask with zeros for the background, and weights proportionals to the norm of the gradients for the stars
def getMask(dx, dy):
    minAmountOfFreqData = 500
    threshold = max( np.amax(dx), np.amax(dy) )
    maskx = masky = np.zeros_like(dx)

    # we need a minimum of minAmountOfFreqData to get a reliable angle estimate, which is why we try to lower the threshold until 
    # we have at least this amount of points outside of the mask.
    while minAmountOfFreqData > cv2.sumElems(maskx)[0] + cv2.sumElems(masky)[0]:
        threshold -= 500
        _, maskx = cv2.threshold( np.abs(dx), threshold, 1, cv2.THRESH_BINARY )
        _, masky = cv2.threshold( np.abs(dy), threshold, 1, cv2.THRESH_BINARY )
    fullMask = np.maximum(maskx, masky).astype(np.uint8)

    # norm of the gradient sqrt(dx*dx + dy*dy)
    normGradient = np.sqrt( np.add(np.multiply(dx, dx), np.multiply(dy, dy)) )
    maskGradient = np.multiply(fullMask, normGradient)
    factor = 255 / np.amax(maskGradient)

    # return a mask with weight proportionnals to the norm of the gradient sqrt(dx*dx + dy*dy) for stars, and zero everywhere else
    return (maskGradient * factor).astype(np.uint8)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: ", sys.argv[0], "<inputImage> <outputImage>"
        sys.exit(2)

    im = loadImage(sys.argv[1], cv2.CV_LOAD_IMAGE_GRAYSCALE)

    # no calculations will be made on imColor, it is used only to generate the output image
    imColor = loadImage(sys.argv[1], cv2.CV_LOAD_IMAGE_COLOR)
    imColor = imColor * 1.5 + 20

    print "image shape:", im.shape

    # crop the image to a multiple of BLOCK_SIZE x BLOCK_SIZE. All the estimations will be done
    # on BLOCK_SIZE x BLOCK_SIZE images
    im = im[ :getcorrectsize(im.shape[0]), :getcorrectsize(im.shape[1]) ]

    # Estimation of the gradient along the x and y axis
    dx = cv2.Sobel(im,cv2.CV_32F,1,0,ksize=5)
    dy = cv2.Sobel(im,cv2.CV_32F,0,1,ksize=5)

    nbRows, nbCols = (im.shape[0]/BLOCK_SIZE, im.shape[1]/BLOCK_SIZE)

    for i in range(nbCols):
        for j in range(nbRows):
            # generate the data for the current block
            dxBlock = getblock(dx, i, j)
            dyBlock = getblock(dy, i, j)
            # create the mask for the current block: the angle will be estimated only for the stars and not the background
            mask = getMask(dxBlock, dyBlock)

            angle = estimateAngle(dxBlock, dyBlock, mask)
            print i, ",", j, "angle:" + str(angle)

            # paint the angle vector on the output image
            drawvector(imColor, (i,j), angle)

    print "writing to: ", sys.argv[2]
    cv2.imwrite(sys.argv[2], imColor)
    sys.exit(0)
