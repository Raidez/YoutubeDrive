import os
import re
import sys
import glob
import math
import numpy as np
from PIL import Image
from utils import BitEncoding

np.set_printoptions(threshold=sys.maxsize)

# TODO: implement image scaling
# DONE: works with different image sizes (whatever ratio)

image_scale = 1
image_size = (10, 10)
filename = "test%num%.png"
image_length = image_size[0] * image_size[1]


def numpy_zoom(array: np.ndarray, factor: int) -> np.ndarray:
    """
    Zoom an array.

    Args:
        array (np.ndarray): The array to zoom.
        factor (int): The zoom factor (negative to zoom out).

    Returns:
        np.ndarray: The zoomed array.
    """
    if factor >= 0:
        return np.repeat(np.repeat(array, factor, axis=0), factor, axis=1)
    else:
        return array[:: abs(factor), :: abs(factor)]


def natural_order(s: str) -> int:
    """
    Get the natural order of a string

    Args:
        s (str): The string.

    Returns:
        int: The natural order.
    """
    if match := re.search(r"\d+", s):
        return int(match.group())
    return 0


################################################################################

# remove previous images
for f in glob.glob("test*.png"):
    os.remove(f)

# encode data to image
data = b"hello world"
ndata = np.array(list(map(int, data)), dtype=np.uint8)
ndata = np.unpackbits(ndata).reshape(-1, 8)
ndata = ndata.flatten()

# split data to chunks of image_size
nbchunk = math.ceil(ndata.size / image_length)
if rchunk := round((nbchunk - ndata.size / image_length) * image_length):
    ndata = np.append(ndata, np.zeros(rchunk, dtype=np.uint8))
    if nbchunk != ndata.size // image_length:
        raise ValueError("Error when chunking data")

# trick to numpy/pillow conversion https://stackoverflow.com/a/32159741
ndatas = np.split(ndata, nbchunk)
for i, ndata in enumerate(ndatas):
    ndata = ndata.reshape(image_size)
    ndata *= 255
    im = Image.fromarray(ndata, mode="L").convert("1")
    im.save(filename.replace("%num%", str(i)), "PNG")

# decode image to array
ndatas = list()
for f in sorted(glob.glob("test*.png"), key=natural_order):
    im = Image.open(f)
    ndata = np.asarray(im.convert("L"))
    ndata = ndata // 255
    ndatas.append(ndata)

# decode array to byte
ndata = np.concatenate([*ndatas])
ndata = ndata.flatten()
ndata = np.resize(ndata, (ndata.size // 8, 8))
ndata = np.packbits(ndata)
data = ndata.tobytes()

# remove endl
data = BitEncoding.remove_endl(data)
print(data)
