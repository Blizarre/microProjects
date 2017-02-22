# coding: utf-8
import cv2
import sys
import numpy as np

DEFAULT_OUTPUT = 'output.jpg'


def update_matrix(orig, second, factor, matrix):
    """Update the warp matrix "matrix" at scale "factor", return a new warp matrix"""
    orig_gray = cv2.resize(
                           orig,
                           None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC)
    second_gray = cv2.resize(
                             second,
                             None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC)
    print("images ready (factor {}): {}".format(factor, orig_gray.shape))

    warp_mode = cv2.MOTION_HOMOGRAPHY
    number_of_iterations = 500

    # Specify the threshold of the increment
    # in the correlation coefficient between two iterations
    termination_eps = 1e-5

    # Define termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations,  termination_eps)

    # Run the ECC algorithm. The results are stored in warp_matrix.
    (cc, warp_matrix) = cv2.findTransformECC(orig_gray, second_gray, matrix, warp_mode, criteria)
    return warp_matrix


def align(orig, second, to_warp):

    # Initialize warp matrix with identity
    warp_matrix = np.eye(3, 3, dtype=np.float32)

    # Incrementally improve the matrix using finer and finer images
    warp_matrix = update_matrix(orig, second, 0.05, warp_matrix)
    warp_matrix = update_matrix(orig, second, 0.1, warp_matrix)
    warp_matrix = update_matrix(orig, second, 0.2, warp_matrix)
    warp_matrix = update_matrix(orig, second, 0.5, warp_matrix)
    warp_matrix = update_matrix(orig, second, 1.0, warp_matrix)

    return cv2.warpPerspective(
                          to_warp,
                          warp_matrix,
                          (orig.shape[1], orig.shape[0]),
                          flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)


reference = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
candidate = cv2.imread(sys.argv[2], cv2.IMREAD_GRAYSCALE)
to_warp = cv2.imread(sys.argv[2])

aligned = align(reference, candidate, to_warp)
cv2.imwrite(sys.argv[3], aligned)
