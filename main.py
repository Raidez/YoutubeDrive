import os
import glob
import numpy as np
from PIL import Image

filename = "test%num%.png"
image_size = (8, 8)
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
ndata = numpy_zoom(ndata, 2).reshape(-1)

## split data by image_size
nbchunk = 1
nbchunk = ndata.size // image_length
if rchunk := ndata.size % image_length:
    ndata = np.append(ndata, np.zeros(rchunk, dtype=np.uint8))
    nbchunk = ndata.size // image_length

# https://github.com/python-pillow/Pillow/issues/350
ndatas = np.split(ndata, nbchunk)
for i, ndata in enumerate(ndatas):
    ndata = ndata.reshape(image_size)
    im = Image.fromarray(ndata, mode="L").convert("1")
    d = np.asarray(im.convert("L"))
    print(d)
    # im.save(filename.replace('%num%', str(i)), 'PNG')

print("done")

# im = Image.fromarray(ndata)
# im.save(filename)

# # decode image
# im = Image.open(filename)
# ndata = np.asarray(im, dtype=np.uint8)
# ndata = numpy_zoom(ndata, -2)

# data = bytearray()
# for bits in ndata:
#     byte = int("".join(map(str, bits)), 2)
#     data.append(byte)

# print(data)
