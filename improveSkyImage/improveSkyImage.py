# coding: utf-8
import numpy as np
import cv2
import sys

BLOCK_SIZE = 256
FINAL_THRESHOLD = 20


# return the padding needed to be a mutiple of BLOCK_SIZE
def getpadding(oldSize):
    return BLOCK_SIZE - oldSize%BLOCK_SIZE

# return the block (1, j) of image. each block has a size of (BLOCK_SIZE, BLOCK_SIZE)
def getblock(image, i, j):
    return image[i * BLOCK_SIZE : (i+1) * BLOCK_SIZE, j * BLOCK_SIZE : (j+1) * BLOCK_SIZE, :]

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: ", sys.argv[0], "<inputImage> <outputImage>"
        sys.exit(2)

    print "Loading image"
    image = cv2.imread(sys.argv[1], cv2.IMREAD_COLOR)
    if( image is None):
        print "Couldn't open image", sys.argv[1]

    image = image.astype(np.uint8)
    originalSize = image.shape

    print "adding border to have a size multiple of BLOCK_SIZE"
    image = cv2.copyMakeBorder(image, 0, getpadding(image.shape[1]), 0, getpadding(image.shape[0]), cv2.BORDER_REFLECT, )

    print "Creating low resolution image of the background light level"
    background = np.zeros( (image.shape[0] / BLOCK_SIZE, image.shape[1] / BLOCK_SIZE, 3), dtype=image.dtype)

    print "Calculating the maximum value of the histogram for each block of ", BLOCK_SIZE, "pixel"
    for i in range(0, background.shape[0]):
        for j in range(0, background.shape[1]):
            for color in range(3):
                background[i, j, color] = cv2.calcHist([getblock(image, i, j)], [color], None, [255], [0,255]).argmax()

    print "Generating the background image by upscaling"
    background = cv2.resize(background, ( image.shape[1], image.shape[0] ), interpolation=cv2.INTER_CUBIC)
    cv2.imshow("Background", background)

    print "Substracting the background image"
    imResult = cv2.subtract(image, background)
    cv2.imshow("Flattened", imResult)

    print "Thresholding the image to remove low background noise"
    _, imThresholded = cv2.threshold(imResult, FINAL_THRESHOLD, 255, cv2.THRESH_TOZERO)
    cv2.imshow("Thresholded", imThresholded)

    print "Smoothing the result with a small kernel to remove hard thresholded edges"
    kernel = cv2.getGaussianKernel(3, -1)
    smooth = cv2.filter2D(imThresholded, -1, kernel)
    cv2.imshow("Smoothened", smooth)

    print "Writing the result"
    cv2.imwrite(sys.argv[2], smooth[:originalSize[0], :originalSize[1], :])

    cv2.waitKey()
    cv2.destroyAllWindows()