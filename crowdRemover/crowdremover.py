# coding: utf-8
import numpy as np
import cv2
import sys

BLOCK_SIZE = 40


# return the padding needed to be a mutiple of BLOCK_SIZE
def getpadding(oldSize):
    return BLOCK_SIZE - oldSize % BLOCK_SIZE


# return the block (i, j) of image. each block has a size of (BLOCK_SIZE, BLOCK_SIZE)
def get_block(image, i, j):
    return image[i * BLOCK_SIZE:(i+1) * BLOCK_SIZE, j * BLOCK_SIZE:(j+1) * BLOCK_SIZE, :]


def set_block(image, block, i, j):
    image[i * BLOCK_SIZE:(i+1) * BLOCK_SIZE, j * BLOCK_SIZE:(j+1) * BLOCK_SIZE, :] = block


def get_all_blocks(images, i, j):
    return [get_block(image, i, j) for image in images]


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
        image = cv2.imread(file_name, cv2.IMREAD_COLOR)
        if image is None:
            print "Couldn't open image", sys.argv[1]
        image = image.astype(np.int16)
        originalSize = image.shape
        image = cv2.copyMakeBorder(
            image, 0, getpadding(image.shape[0]), 0, getpadding(image.shape[1]), cv2.BORDER_REFLECT)
        input_images.append(image)

    output_image = np.zeros_like(input_images[0])
    nb_images = len(input_images)

    blocks_shape = (image.shape[0] / BLOCK_SIZE, image.shape[1] / BLOCK_SIZE)
    selected_image = np.zeros(blocks_shape, dtype=np.int32)
    similarity_matrix = np.zeros(
            (blocks_shape[0], blocks_shape[1], nb_images, nb_images), dtype=np.int32)

    print "Compute similarity matrix"
    for blkx in range(blocks_shape[0]):
        for blky in range(blocks_shape[1]):
            blocks = get_all_blocks(input_images, blkx, blky)
            similarity_matrix[blkx, blky, :] = compute_similarity_matrix(blocks)

    print "Find solution"
    for blkx in range(blocks_shape[0]):
        for blky in range(blocks_shape[1]):
            selected_image[blkx, blky] = np.argmin(np.sum(similarity_matrix[blkx, blky], axis=1))

    print "Generate output image"
    for blkx in range(blocks_shape[0]):
        for blky in range(blocks_shape[1]):
            blocks = get_all_blocks(input_images, blkx, blky)
            set_block(output_image, blocks[selected_image[blkx, blky]], blkx, blky)

    output_image = output_image[:originalSize[0], :originalSize[1], :]
    cv2.imwrite("test.jpg", output_image)
