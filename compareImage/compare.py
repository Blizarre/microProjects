from PIL import Image as Im
import numpy as np
from scipy import ndimage as nd

import sys

DEFAULT_THRESHOLD = 20

if len(sys.argv) == 4:
	_, refPath, candidatePath, outPath = sys.argv
	threshold = DEFAULT_THRESHOLD
elif len(sys.argv) == 5:
	_, refPath, candidatePath, outPath, threshold = sys.argv
else:
	print "Usage: %s <ref_image> <candidate_image> <output> [threshold]"
	sys.exit(5)

# Converting images to grayscale ('L') gives better results than looking for differences across each channel.
ref = np.asarray( Im.open(refPath).convert("L") ).astype("int")
candidate = np.asarray( Im.open(candidatePath).convert("L") ).astype("int")

# The output image is the reference Image in RGB
output = np.asarray( Im.open(refPath) ).copy()

diff = np.abs( ref - candidate )

# The mask contains the pixels that are different (diff > threshold)
mask = np.zeros_like(diff)
mask[ np.where(diff > threshold) ] = 255

# dila1, dila2 and dila3 are used to generate the outline around the pixels of the mask using dilatation
dila1 = nd.binary_dilation(mask)
dila2 = nd.binary_dilation(dila1)
dila3 = nd.binary_dilation(dila2)

# outline is written on the output image
output[np.where(dila1 - mask > 0)] = [255, 255, 255]
output[np.where(dila2 - dila1 > 0)] = [0, 0, 0]
output[np.where(dila3 - dila2 > 0)] = [255, 0, 0]

Im.fromarray(output.astype("uint8")).save(outPath)
