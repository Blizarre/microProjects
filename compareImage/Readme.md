# Compare Images

This small script is used to compare two images. It outputs the reference image with an outline around the differences detected.

Currently the script only substract the reference image from the candidate image in grayscale and compare each pixel to the threshold. I plan to improve this later if needed.

  Usage: python compare.py <ref_image> <candidate_image> <output> [threshold]
  
Requirements: PIL and Scipy