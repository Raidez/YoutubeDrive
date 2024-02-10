import os
import glob
import math
import numpy as np
from PIL import Image
from utils import BitEncoding

image_scale = 1
image_size = (10, 10)
filename = "test%num%.png"
image_length = image_size[0] * image_size[1]


def numpy_zoom(array: np.ndarray, factor: int) -> np.ndarray:
    if factor >= 0:
        return np.repeat(np.repeat(array, factor, axis=0), factor, axis=1)
    else:
        return array[:: abs(factor), :: abs(factor)]


# remove previous images
for f in glob.glob("test*.png"):
    os.remove(f)

# encode data to image
data = b"hello world"
ndata = np.array(list(map(int, data)), dtype=np.uint8)
ndata = np.unpackbits(ndata).reshape(-1, 8)
ndata = numpy_zoom(ndata, image_scale).flatten()

# split data by image_size
nbchunk = math.ceil(ndata.size / image_length)
if rchunk := int((nbchunk - ndata.size / image_length) * image_length):
    ndata = np.append(ndata, np.zeros(rchunk, dtype=np.uint8))
    if nbchunk != ndata.size // image_length:
        raise ValueError("Error when chunking data")

# trick to numpy/pillow conversion https://stackoverflow.com/a/32159741
ndatas = np.split(ndata, nbchunk)
for i, ndata in enumerate(ndatas):
    ndata = ndata.reshape(image_size)
    ndata *= 255
    im = Image.fromarray(ndata, mode="L").convert("1")
    im.save(filename.replace('%num%', str(i)), 'PNG')

# decode image to array
ndatas = list()
for f in glob.glob("test*.png"):
    im = Image.open(f)
    ndata = np.asarray(im.convert("L"))
    ndatas.append(ndata)

# decode array to byte
data = bytearray()
ndata = np.concatenate(*ndatas).flatten() // 255
ndata = np.resize(ndata, (ndata.size // 8, 8))
for bits in ndata:
    byte = int("".join(map(str, bits)), 2)
    data.append(byte)

# remove endl
data = BitEncoding.remove_endl(data)
print(data)
