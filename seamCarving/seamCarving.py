# coding: utf-8
import numpy as np
import cv2
import sys
import matplotlib.pyplot as plt


# load the image from path. imType can be:
#   cv2.CV_LOAD_IMAGE_COLOR, cv2.CV_LOAD_IMAGE_GRAYSCALE, cv2.CV_LOAD_IMAGE_UNCHANGED
# dataType can be :
#   np.float32, np.float64, np.uint8, np.int32, ...
# Will throw an exception on error
def load_image(path, imtype = cv2.CV_LOAD_IMAGE_UNCHANGED, data_type = np.uint8):
    print "Loading image:", path
    image = cv2.imread(path, imtype)

    if(image is None):
        raise IOError("Couldn't open image: " + path)

    return image.astype(data_type)


# Save the image to the file name, pad the columns with zeros to get the shape
# can handle grayscale images and color images
def save_image_fixed_size(name, image, shape):
    toSave = np.zeros(shape)
    if len(shape) == 2: # not an image, grayscale
        toSave[:, :(image.shape[1])] = image
        plt.imsave(name, toSave)
    else:
        toSave[:, :(image.shape[1]), :] = image
        cv2.imwrite(name, toSave)


# Generate the energy map, filterType can be 's' for Sobel, or 'g' for Gabor filter. half_width is the half-size of the filter
# ex: half_width = 3 means that the final size of the filter will be 3 * 2 + 1 = 7 pixels
def generate_energy_map(image, filterType, half_width):
    if filterType == "g":
        kernel = cv2.getGaborKernel((half_width * 2 + 1, half_width * 2 + 1))
        gradient = cv2.filter2D(image, cv2.CV_32F, kernel, 2, 0, 3, 1)
    elif filterType == "s":
        gradient = cv2.Sobel(image, cv2.CV_32F, 1, 0, ksize=half_width * 2 + 1)
    return np.multiply(gradient, gradient)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print "Usage: ", sys.argv[0], "<inputImage> <outputImageName> <nbColsToRemove> <g|s>"
        print "Will generate one of each for each column removed:"
        print " - <outputImageName>_image_%04d.png : the image"
        print " - <outputImageName>_costs_%04d.png : the cost map"
        print "As well as the final image <outputImageName>.png"
        print "Energy map can be computed using g (Gabor) or Sobel (s) filter"
        sys.exit(2)

    (_, inputImage, outputImName, nbColsToRemove, filter) = sys.argv
    nbColsToRemove = int(nbColsToRemove)

    originalIm = load_image(inputImage, cv2.CV_LOAD_IMAGE_COLOR)
    (rows, cols, depth) = originalIm.shape

    # half size of the filter used to generate the energy map
    half_filterw = 4

    originalImGray = cv2.cvtColor(originalIm, cv2.COLOR_RGB2GRAY);

    currentImage = originalIm
    currentImageGray = originalImGray

    # remove nbColsToRemove lines
    for iter in range(1, nbColsToRemove):

        # Generate the energy map
        energyMap = generate_energy_map(currentImageGray, filter, half_filterw)

        # borders removal
        energyMap = energyMap[:, half_filterw:-half_filterw]

        # Creation of the weight map
        costs = np.zeros_like(energyMap)

        # Initialize first line
        costs[0, :] = energyMap[0, :]

        # Propagate the best solution
        for i in range(1, rows):
            # min f(i, j) = gradient(i, j) + min ( f(i-1, j-1), f(i-1, j), f(i-1, j +1 ) )
            opt = np.minimum( costs[i-1, :-2], costs[i-1, 1:-1] )
            opt = np.minimum( costs[i-1, 2:], opt )
            costs[i, 1:-1] = energyMap[i, 1:-1] + opt
            costs[i, 0] = energyMap[i, 0] + np.min(costs[i-1, :2] )
            costs[i, -1] = energyMap[i, -1] + np.min(costs[i-1, -2:] )

        minPos = np.argmin(costs[-1, :])

        newColsNumber = energyMap.shape[1] - 1

        #####################
        # Creation of the image matrix where the lowest-energy line has been removed (cut*)
        cutCosts = np.zeros( (rows, newColsNumber) )

        # The borders of cutImageGray and cutIm are not removed, therefore they are filterwidth * 2 larger
        cutImageGray = np.zeros( (rows, newColsNumber + half_filterw * 2), dtype=np.float32 )
        cutIm = np.zeros( (rows, newColsNumber + half_filterw * 2, depth), dtype=np.uint8 )

        #####################
        # backtrack from the bottom to the top to select the lowest-energy line

        # minPos is the position of the lowest-energy pixel at the row i that is connected to
        # the lowest-energy path at rows i+1 and beyond
        minPos = 1 + np.argmin(costs[rows - 1, 1:-2], axis=0)

        for i in range(rows -1, 0, -1):
            # Special cases: at the last row, the path was on the left or right edges
            if minPos == 0:
                minPos = minPos + np.argmin( costs[i, 0 : 2] )
            elif minPos == newColsNumber-1:
                minPos = minPos + np.argmin( costs[i, -2 : -1] ) - 1
            # General case
            else:
                minPos = minPos + np.argmin( costs[i, minPos - 1 : minPos + 2] ) - 1
            # draw the lowest-energy path on the image and on the weight map, used to generate pretty pictures.
            # The pixels that are changed will be removed for the cut* images
            currentImage[i, minPos + half_filterw, :] = 0
            costs[i, minPos] = 0

            cutIm[i, :, :] = np.delete(currentImage[i, :, :], minPos + half_filterw, axis=0)
            cutCosts[i, :] = np.delete(costs[i, :], minPos, axis=0)
            cutImageGray[i, :] = np.delete(currentImageGray[i, :], minPos + half_filterw, axis=0)

        save_image_fixed_size("%s_image_%04d.png"%(outputImName, iter), currentImage, (rows, cols, depth))
        save_image_fixed_size("%s_costs_%04d.png"%(outputImName, iter), np.log(costs), (rows, cols))

        currentImage = cutIm
        currentImageGray = cutImageGray

    plt.figure("Result image")
    plt.imshow(currentImage.astype(np.uint8))
    cv2.imwrite(outputImName + ".png", currentImage)
    plt.show()

    sys.exit(0)