# coding: utf-8
import numpy as np
import cv2
import sys

BLOCK_SIZE = 40


# return the padding needed to be a mutiple of BLOCK_SIZE
def getpadding(oldSize):
    return BLOCK_SIZE - oldSize % BLOCK_SIZE


# return the block (1, j) of image. each block has a size of (BLOCK_SIZE, BLOCK_SIZE)
def getblock(image, i, j):
    return image[i * BLOCK_SIZE:(i+1) * BLOCK_SIZE, j * BLOCK_SIZE:(j+1) * BLOCK_SIZE]


# return the block (1, j) of image. each block has a size of (BLOCK_SIZE, BLOCK_SIZE)
def getblock_orig(image, i, j):
    return image[i * BLOCK_SIZE:(i+1) * BLOCK_SIZE, j * BLOCK_SIZE:(j+1) * BLOCK_SIZE, :]


def setblock(image, block, i, j):
    image[i * BLOCK_SIZE:(i+1) * BLOCK_SIZE, j * BLOCK_SIZE:(j+1) * BLOCK_SIZE, :] = block


def get_blocks(images, i, j):
    return [getblock(image, i, j) for image in images]


def get_blocks_orig(images, i, j):
    return [getblock_orig(image, i, j) for image in images]


def compute_similarity_matrix(blocks):
    nb_elts = len(blocks)
    matrix = np.zeros((nb_elts, nb_elts))
    for i in range(nb_elts):
        for j in range(nb_elts):
            diff = blocks[i] - blocks[j]
            matrix[i, j] = np.sum(diff * diff)
    return matrix


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print "Usage: ", sys.argv[0], "<inputImage> <inputImage> <outputImage>"
        sys.exit(2)

    input_images_names = sys.argv[1:-2]
    input_images = []
    input_images_orig = []

    print "Loading input images"
    for file_name in input_images_names:
        image = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
        image_orig = cv2.imread(file_name, cv2.IMREAD_COLOR)
        if image is None:
            print "Couldn't open image", sys.argv[1]
        image = image.astype(np.int16)
        originalSize = image.shape
        image = cv2.copyMakeBorder(
            image, 0, getpadding(image.shape[1]), 0, getpadding(image.shape[0]), cv2.BORDER_REFLECT)
        image_orig = cv2.copyMakeBorder(
            image_orig, 0, getpadding(image.shape[1]), 0, getpadding(image.shape[0]), cv2.BORDER_REFLECT)
        input_images.append(image)
        input_images_orig.append(image_orig)

    output_image = np.zeros_like(image_orig)

    selected_image = np.zeros((image.shape[0] / BLOCK_SIZE, image.shape[1] / BLOCK_SIZE), dtype=np.int32)

    for blkx in range(selected_image.shape[0]):
        for blky in range(selected_image.shape[1]):
            blocks = get_blocks(input_images, blkx, blky)
            blocks_orig = get_blocks_orig(input_images_orig, blkx, blky)
            similarity_matrix = compute_similarity_matrix(blocks)
            selected_image[blkx, blky] = np.argmin(np.sum(similarity_matrix, axis=1))
            setblock(output_image, blocks_orig[selected_image[blkx, blky]], blkx, blky)

    # cv2.imshow("test", output_image)
    # cv2.waitKey(0)
    cv2.imwrite("test.jpg", output_image)
