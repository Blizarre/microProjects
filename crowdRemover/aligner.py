# coding: utf-8
import cv2
import sys
import numpy as np

DEFAULT_OUTPUT = 'output.jpg'


def update_matrix(orig, second, factor, matrix):
    """Update the warp matrix "matrix" at scale "factor", return a new warp matrix"""

    reprojThresh = 4.0

    orig_gray = cv2.resize(
                           cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY),
                           None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC)
    second_gray = cv2.resize(
                             cv2.cvtColor(second, cv2.COLOR_BGR2GRAY),
                             None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC)
    print("images ready factor{}: {}".format(factor, orig_gray.shape))

    print("compute descriptors")
    descriptor = cv2.xfeatures2d.SIFT_create()
    (kpsOrig, featuresOrig) = descriptor.detectAndCompute(orig_gray, None)

    (kpsSecond, featuresSecond) = descriptor.detectAndCompute(second_gray, None)

    kpsOrig = np.float32([kp.pt for kp in kpsOrig])
    kpsSecond = np.float32([kp.pt for kp in kpsSecond])
    print("Descriptors found for orig: {}, second:{}".format(len(kpsOrig), len(kpsSecond)))

    print("match descriptors")
    matcher = cv2.DescriptorMatcher_create("BruteForce")
    rawMatches = matcher.knnMatch(featuresOrig, featuresSecond, 2)

    print("found {} raw matches", len(rawMatches))

    ratio = 0.5
    matches = []
    # loop over the raw matches
    for m in rawMatches:
        # ensure the distance is within a certain ratio of each
        # other (i.e. Lowe's ratio test)
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            matches.append((m[0].trainIdx, m[0].queryIdx))

    print("found {} filtered (lowe's) matches".format(len(matches)))

    # matches = rawMatches
    ptsOrig = np.float32([kpsOrig[i] for (_, i) in matches])
    ptsSeccond = np.float32([kpsSecond[i] for (i, _) in matches])

    print("find homography")
    (H, status) = cv2.findHomography(ptsOrig, ptsSeccond, cv2.RANSAC,
                                     reprojThresh)
    return H


def align(orig, second):

    # Initialize warp matrix with identity
    warp_matrix = np.eye(3, 3, dtype=np.float32)

    # Incrementally improve the matrix using finer and finer images
    warp_matrix = update_matrix(orig, second, 1.0, warp_matrix)

    # Use warpAffine for Translation, Euclidean and Affine
    return cv2.warpPerspective(
                          second,
                          warp_matrix,
                          (orig.shape[1], orig.shape[0]),
                          flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)


reference = cv2.imread(sys.argv[1])
candidate = cv2.imread(sys.argv[2])

aligned = align(reference, candidate)
cv2.imwrite(sys.argv[3], aligned)
