# coding: utf-8
import numpy as np
import argparse
import cv2
import sys

DEFAULT_OUTPUT = 'output.jpg'


def parse_arguments():
    parser = argparse.ArgumentParser(description='Remove crowd')
    parser.add_argument('-b', '--block-size', type=int, default=40,
                        help='Block size')
    parser.add_argument('-s', '--overlap', type=int, default=2,
                        help='overlap between blocks')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file name')
    parser.add_argument('images', type=str, nargs='+',
                        help='input images')
    args = parser.parse_args()

    if len(args.images) < 2:
        parser.error("at least 2 input images are needed")

    return args


def getpadding(oldSize, block_size):
    """return the padding needed to be a mutiple of BLOCK_SIZE"""
    return block_size - oldSize % block_size


class BlockGenerator:
    """This class deal with the retrieval and modification of blocks in the image. It will automatically take into account
    overlap and block size"""

    def __init__(self, block_size, overlap):
        self.block_size = block_size
        self.overlap = overlap

    def prepare_image(self, image):
        """add borders to the image so that it can be accessed using the BlockGenerator methods"""
        image = image.astype(np.int16)
        return cv2.copyMakeBorder(
            image,
            self.overlap, getpadding(image.shape[0], self.block_size) + self.overlap,
            self.overlap, getpadding(image.shape[1], self.block_size) + self.overlap,
            cv2.BORDER_CONSTANT, 0)

    def get_block(self, image, i, j, extra_border=0):
        """return the block (i, j) of image. each block has a size of
        (BLOCK_SIZE + 2 * extra_border, BLOCK_SIZE + 2 * extra_border)"""
        im = image[
            self.overlap - extra_border + i * self.block_size:
                self.overlap + extra_border + (i+1) * self.block_size,
            self.overlap - extra_border + j * self.block_size:
                self.overlap + extra_border + (j+1) * self.block_size,
            :]
        return im

    def add_block(self, output, block, i, j, extra_border):
        output[
            self.overlap - extra_border + i * self.block_size: (i+1) * self.block_size + extra_border + self.overlap,
            self.overlap - extra_border + j * self.block_size: (j+1) * self.block_size + extra_border + self.overlap,
            :] += block

    def get_all_blocks(self, image_list, i, j):
        return [self.get_block(image, i, j) for image in image_list]


def create_stencil(image_shape, smooth):
    """The stencil is a mask that will enable a smooth transition between blocks. blocks will be multiplied
    by the stencil so that when they are blitted to the image, transition between them are smoothed out.
    image 1: 1 1 1 1 1 1 1 , image 2: 2 2 2 2 2 2 2, stencil: .25 .75 1 1 1 .75 .25
    image 1 * stencil: .25 .75  1   1   1  .75  .25
                        image 2 * stencil: .5   1.5  2   2   2   1.5 .5
    adding them:       .25 .75  1   1   1  1.25 1.75 2   2   2   1.5 .5
    """
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


def compute_similarity_matrix(blocks):
    nb_elts = len(blocks)
    matrix = np.zeros((nb_elts, nb_elts))
    for i in range(nb_elts):
        for j in range(nb_elts):
            diff = blocks[i] - blocks[j]
            matrix[i, j] = np.sum(np.abs(diff))
    return matrix


def main():
    args = parse_arguments()

    bg = BlockGenerator(args.block_size, args.overlap)

    input_images = []

    print("Loading input images")
    for file_name in args.images:
        image = cv2.imread(file_name, cv2.IMREAD_COLOR)
        if image is None:
            print("Couldn't open image", sys.argv[1])
        originalSize = image.shape
        input_images.append(bg.prepare_image(image))

    output_image = np.zeros_like(input_images[0], dtype=np.float32)

    nb_images = len(input_images)

    blocks_shape = (input_images[0].shape[0] // args.block_size, input_images[0].shape[1] // args.block_size)
    selected_image = np.zeros(blocks_shape, dtype=np.int32)
    similarity_matrix = np.zeros(
            (blocks_shape[0], blocks_shape[1], nb_images, nb_images), dtype=np.int32)

    print("Compute similarity matrix")
    for blkx in range(blocks_shape[0]):
        for blky in range(blocks_shape[1]):
            blocks = bg.get_all_blocks(input_images, blkx, blky)
            blocks = [cv2.cvtColor(b.astype(np.float32) / 255, cv2.COLOR_RGB2LAB) for b in blocks]
            similarity_matrix[blkx, blky, :] = compute_similarity_matrix(blocks)

    print("Find solution")
    for blkx in range(blocks_shape[0]):
        for blky in range(blocks_shape[1]):
            selected_image[blkx, blky] = np.argmin(np.sum(similarity_matrix[blkx, blky], axis=1))

    print("Generate output image")
    stencil = create_stencil(
        (args.block_size + args.overlap * 2, args.block_size + args.overlap * 2, 3),
        args.overlap)

    for blkx in range(blocks_shape[0]):
        for blky in range(blocks_shape[1]):
            block = bg.get_block(input_images[selected_image[blkx, blky]], blkx, blky, args.overlap)
            block = block.astype(np.float32)
            block *= stencil
            bg.add_block(output_image, block, blkx, blky, args.overlap)

    output_image = output_image[
            2*args.overlap:originalSize[0]+args.overlap,
            2*args.overlap:originalSize[1]+args.overlap, :].astype(np.uint8)

    print("Press 's' to save image to file '{}', any other key to exit".format(args.output or DEFAULT_OUTPUT))
    cv2.namedWindow('Result', cv2.WINDOW_NORMAL)
    cv2.imshow("Result", output_image)
    ret_code = cv2.waitKey(0)
    if args.output or ret_code == 115:  # 's' pressed
        cv2.imwrite(args.output or DEFAULT_OUTPUT, output_image)


if __name__ == "__main__":
    main()
