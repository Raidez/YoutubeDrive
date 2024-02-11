import re
import sys
import glob
import math
import pytest
import numpy as np
from PIL import Image
from utils import BitEncoding

# TODO: implement image scaling
# TODO: use RGB for bits encoding


def numpy_rescale(array: np.ndarray, factor: int) -> np.ndarray:
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


################################################################################


def test_smaller(tmp_path):
    """
    Use case: data is smaller than image
    -> flatten data and fill remaining space with 0

    Example:
        ndata = [
            [a, b],
            [c, d]
        ]
        image_size = (3, 3)

        f(ndata, image_size) => [
            [a, b, c],
            [d, _, _],
            [_, _, _]
        ]
    """
    data = b"hello"
    image_size = np.zeros((10, 10), dtype=np.uint8)
    image_output = tmp_path / "frame%num%.png"

    ############################### ENCODE ###############################
    # encode data to image
    ndata = np.array(list(map(int, data)), dtype=np.uint8)
    ndata = np.unpackbits(ndata).reshape(-1, 8)
    idata = ndata.view()

    # use case
    if ndata.size < image_size.size:
        # if data.shape is smaller than image.shape
        # flatten data and fill remaining space with 0
        ndata = ndata.flatten()
        ndata = np.append(ndata, np.zeros(image_size.size - ndata.size, dtype=np.uint8))

    # convert data to image
    ndata = ndata.reshape(image_size.shape)
    ndata *= 255
    im = Image.fromarray(ndata, mode="L").convert("1")
    im.save(str(image_output).replace("%num%", str(0)), "PNG")

    ############################### DECODE ###############################
    # decode image to array
    for f in sorted(tmp_path.glob("frame*.png")):
        im = Image.open(f)
        ndata = np.asarray(im.convert("L"))
        ndata = ndata // 255

    # decode array to byte
    ndata = ndata.flatten()
    ndata = np.packbits(ndata)
    s = ndata.tobytes()

    # remove endl
    s = BitEncoding.remove_endl(s)
    assert s == data
    assert s.decode() == data.decode()


def test_bigger(tmp_path):
    """
    Use case: data is bigger than image
    -> split data to chunks of image_size

    Example:
        ndata = [
            [a, b, c],
            [d, e, f],
            [g, h, i]
        ]
        image_size = (2, 2)

        f(ndata, image_size) => [[
            [a, b],
            [c, d]
        ],
            [e, f],
            [g, h]
        ],
            [i, _],
            [_, _]
        ]]
    """
    data = b"hello world"
    image_size = np.zeros((4, 4), dtype=np.uint8)
    image_output = tmp_path / "frame%num%.png"

    ############################### ENCODE ###############################
    # encode data to image
    ndata = np.array(list(map(int, data)), dtype=np.uint8)
    ndata = np.unpackbits(ndata).reshape(-1, 8)
    idata = ndata.view()

    # use case
    ndatas = list()
    if ndata.size > image_size.size:
        ndata = ndata.flatten()
        nbchunk = math.ceil(ndata.size / image_size.size)
        if rchunk := round((nbchunk - ndata.size / image_size.size) * image_size.size):
            ndata = np.append(ndata, np.zeros(rchunk, dtype=np.uint8))
            if nbchunk != ndata.size // image_size.size:
                raise ValueError("Error when chunking data")
        ndatas = np.split(ndata, nbchunk)

    # convert data chunks to image
    for i, ndata in enumerate(ndatas):
        ndata = ndata.reshape(image_size.shape)
        ndata *= 255
        im = Image.fromarray(ndata, mode="L").convert("1")
        im.save(str(image_output).replace("%num%", str(i)), "PNG")

    ############################### DECODE ###############################
    # decode image to chunk array
    ndatas = list()
    for f in sorted(tmp_path.glob("frame*.png")):
        im = Image.open(f)
        ndata = np.asarray(im.convert("L"))
        ndata = ndata // 255
        ndatas.append(ndata)

    # decode array to byte
    ndata = np.concatenate(ndatas)
    ndata = ndata.flatten()
    ndata = np.packbits(ndata)
    s = ndata.tobytes()

    # remove endl
    s = BitEncoding.remove_endl(s)
    assert s == data
    assert s.decode() == data.decode()


def test_weirder(tmp_path):
    """
    Use case: data has a weird shape than image
    """
    data = b"hello world"
    image_size = np.zeros((20, 4))
    image_output = tmp_path / "frame%num%.png"

    #################################### ENCODE ####################################
    # encode data to image
    ndata = np.array(list(map(int, data)), dtype=np.uint8)
    ndata = np.unpackbits(ndata).reshape(-1, 8)
    idata = ndata.view()

    # use case
    ndatas = list()
    if ndata.size < image_size.size:
        # if data is smaller than image
        # flatten data and fill remaining space with 0
        ndata = ndata.flatten()
        ndata = np.append(ndata, np.zeros(image_size.size - ndata.size, dtype=np.uint8))
        ndatas.append(ndata)
    elif ndata.size > image_size.size:
        # if data is bigger than image
        # split data to chunks of image_size
        ndata = ndata.flatten()
        nbchunk = math.ceil(ndata.size / image_size.size)

        ## fill remaining space with 0
        if rchunk := round((nbchunk - ndata.size / image_size.size) * image_size.size):
            ndata = np.append(ndata, np.zeros(rchunk, dtype=np.uint8))
            if nbchunk != ndata.size // image_size.size:
                raise ValueError("Error when chunking data")

        ndatas = np.split(ndata, nbchunk)

    # convert data chunks to image
    for i, ndata in enumerate(ndatas):
        ndata = ndata.reshape(image_size.shape)
        ndata *= 255
        im = Image.fromarray(ndata, mode="L").convert("1")
        im.save(str(image_output).replace("%num%", str(i)), "PNG")

    #################################### DECODE ####################################
    # decode image to chunk array
    ndatas = list()
    for f in sorted(tmp_path.glob("frame*.png")):
        im = Image.open(f)
        ndata = np.asarray(im.convert("L"))
        ndata = ndata // 255
        ndatas.append(ndata)

    # decode array to byte
    ndata = np.concatenate(ndatas)
    ndata = ndata.flatten()
    ndata = np.packbits(ndata)
    s = ndata.tobytes()

    # remove endl
    s = BitEncoding.remove_endl(s)
    assert s == data
    assert s.decode() == data.decode()
