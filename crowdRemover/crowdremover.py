# coding: utf-8
import numpy as np
import cv2
import sys

BLOCK_SIZE = 40
SMOOTH_SIZE = 2


# return the padding needed to be a mutiple of BLOCK_SIZE
def getpadding(oldSize):
    return BLOCK_SIZE - oldSize % BLOCK_SIZE


# return the block (i, j) of image. each block has a size of (BLOCK_SIZE, BLOCK_SIZE)
def get_block(image, i, j, extra_border=0):
    im = image[
        SMOOTH_SIZE - extra_border + i * BLOCK_SIZE:
            SMOOTH_SIZE + extra_border + (i+1) * BLOCK_SIZE,
        SMOOTH_SIZE - extra_border + j * BLOCK_SIZE:
            SMOOTH_SIZE + extra_border + (j+1) * BLOCK_SIZE,
        :]
    return im


def add_block(output, image, i, j, extra_border):
    output[
        SMOOTH_SIZE - extra_border + i * BLOCK_SIZE: (i+1)*BLOCK_SIZE + extra_border + SMOOTH_SIZE,
        SMOOTH_SIZE - extra_border + j * BLOCK_SIZE: (j+1)*BLOCK_SIZE + extra_border + SMOOTH_SIZE,
        :] += image


def create_stencil(image_shape, smooth):
    stencil = np.ones(image_shape, dtype=np.float32)
    # 2 * smooth because we need to blend the inside of the block with the outside of the other block
    # for smooth = 4, i1; inside image 1, o1: outside image 1
    # o1 o1 o1 o1 | i1 i1 i1 i1
    # i1 i1 i1 i1 | o1 o1 o1 o1
    factors = np.linspace(0, 1, 2*smooth+1, endpoint=False)[1:]
    for i, f in enumerate(factors):
        stencil[i, :, :] *= f
        stencil[:, i, :] *= f
    for i, f in enumerate(factors):
        stencil[image_shape[0] - i - 1, :, :] *= f
        stencil[:, image_shape[1] - i - 1, :] *= f
    return stencil


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
        print("Usage: ", sys.argv[0], "<inputImage> <inputImage> <outputImage>")
        sys.exit(2)

    input_images_names = sys.argv[1:-2]
    output_image_name = sys.argv[-1]
    input_images = []
    input_images_orig = []

    print("Loading input images")
    for file_name in input_images_names:
        image = cv2.imread(file_name, cv2.IMREAD_COLOR)
        if image is None:
            print("Couldn't open image", sys.argv[1])
        image = image.astype(np.int16)
        originalSize = image.shape
        image = cv2.copyMakeBorder(
            image,
            SMOOTH_SIZE, getpadding(image.shape[0]) + SMOOTH_SIZE,
            SMOOTH_SIZE, getpadding(image.shape[1]) + SMOOTH_SIZE,
            cv2.BORDER_CONSTANT, 0)
        input_images.append(image)

    output_image = np.zeros_like(input_images[0], dtype=np.float32)

    nb_images = len(input_images)

    blocks_shape = (image.shape[0] // BLOCK_SIZE, image.shape[1] // BLOCK_SIZE)
    selected_image = np.zeros(blocks_shape, dtype=np.int32)
    similarity_matrix = np.zeros(
            (blocks_shape[0], blocks_shape[1], nb_images, nb_images), dtype=np.int32)

    print("Compute similarity matrix")
    for blkx in range(blocks_shape[0]):
        for blky in range(blocks_shape[1]):
            blocks = get_all_blocks(input_images, blkx, blky)
            similarity_matrix[blkx, blky, :] = compute_similarity_matrix(blocks)

    print("Find solution")
    for blkx in range(blocks_shape[0]):
        for blky in range(blocks_shape[1]):
            selected_image[blkx, blky] = np.argmin(np.sum(similarity_matrix[blkx, blky], axis=1))

    print("Generate output image")
    stencil = create_stencil(
        (BLOCK_SIZE + SMOOTH_SIZE * 2, BLOCK_SIZE + SMOOTH_SIZE * 2, 3),
        SMOOTH_SIZE)

    for blkx in range(blocks_shape[0]):
        for blky in range(blocks_shape[1]):
            block = get_block(input_images[selected_image[blkx, blky]], blkx, blky, SMOOTH_SIZE)
            block = block.astype(np.float32)
            block *= stencil
            add_block(output_image, block, blkx, blky, SMOOTH_SIZE)

    output_image = output_image[
            2*SMOOTH_SIZE:originalSize[0]+SMOOTH_SIZE,
            2*SMOOTH_SIZE:originalSize[1]+SMOOTH_SIZE, :].astype(np.uint8)

    cv2.namedWindow('test', cv2.WINDOW_NORMAL)
    cv2.imshow("test", output_image)
    ret_code = cv2.waitKey(0)
    print("Press 's' to save image, any other key to exit")
    if ret_code == 115:  # 's' pressed
        cv2.imwrite(output_image_name, output_image)
