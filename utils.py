import copy
import math
import cv2 as cv
import numpy as np
from PIL import Image, ImageDraw


def biter(b: int, step=1):
    """
    Iterate over the bits of an integer.

    Args:
        b (int): The integer to generate binary numbers for.

    Yields:
        int: The binary numbers.
    """
    for i in range(0, 8, step):
        yield b >> i & 1


def fourcc(name: str):
    """
    Get the fourcc code for a codec name.

    Args:
        name (str): The name of the codec.

    Returns:
        str: The fourcc code.
    """
    return getattr(cv, "VideoWriter_fourcc")(*name)


class Encoding:
    """
    Encode/decode byte data to image.
    """

    @staticmethod
    def encode(data: bytes, image_size: tuple[int, int], output_path: str):
        """
        Encode data to image.

        Args:
            data (bytes): The data to encode.
            image_size (tuple[int, int]): The size of the image.
            output_path (str): The path to save the image.
        """
        raise NotImplementedError

    @staticmethod
    def decode(path: str):
        """
        Decode image to data.

        Args:
            path (str): The path to the image.
        """
        raise NotImplementedError


class BitEncoding(Encoding):
    """
    Encode/decode byte data to image where 0 is black and 1 is white (binary).
    """

    @staticmethod
    def encode(data: bytes, image_size: tuple[int, int], output_path: str):
        im = Image.new("1", image_size)

        i, x, y = 0, 0, 0
        for byte in data:
            for bit in reversed(list(biter(byte))):
                im.putpixel((x, y), bit)

                x += 1

                # next row
                if x >= image_size[0]:
                    x = 0
                    y += 1

                # next image
                if y >= image_size[1]:
                    im.save(output_path.replace("%num%", str(i)))
                    im = Image.new("1", image_size)
                    x, y = 0, 0
                    i += 1

        im.save(output_path.replace("%num%", str(i)))

    @staticmethod
    def decode(path: str) -> bytes:
        im = Image.open(path)

        out = bytearray()
        data = list(im.getdata())
        for i in range(0, len(data), 8):
            bits = data[i : i + 8]
            bits = [1 if b == 255 else 0 for b in bits]
            byte = int("".join(map(str, bits)), 2)
            out.append(byte)

        return bytes(out)

    @staticmethod
    def remove_endl(data: bytes) -> bytes:
        """
        Remove last empty block of data.

        Args:
            data (bytes): The data to process.

        Returns:
            bytes: The data without the last empty block.
        """
        i = 0
        for i in range(len(data) - 1, 0, -1):
            if data[i] != 0:
                break

        return bytes(data[: i + 1])


class VideoEncoding:
    """
    Encode/decode images to video.
    """

    @staticmethod
    def encode(images: list[str], video_size: tuple[int, int], output_path: str):
        video_codec = fourcc("RGBA")
        video = cv.VideoWriter(output_path, video_codec, 1, video_size)
        for imagepath in images:
            frame = cv.imread(imagepath)
            video.write(frame)
        video.release()

    @staticmethod
    def decode(path: str, image_output: str):
        cap = cv.VideoCapture(path)
        if not cap.isOpened():
            raise Exception("Can't open video")

        i = 0
        last_frame = None
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # convert color space to RGB
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

            # don't save duplicate frames
            if type(last_frame) is np.ndarray and np.array_equal(frame, last_frame):
                continue

            # save frame
            last_frame = copy.deepcopy(frame)
            Image.fromarray(frame).save(image_output.replace("%num%", str(i)), "PNG")
            i += 1

        cap.release()


class NumpyBitEncoding(Encoding):
    """
    Encode/decode byte data to image where 0 is black and 1 is white (binary).
    """

    @staticmethod
    def encode(data: bytes, image_size: tuple[int, int], output_path: str):
        image = np.zeros(image_size, dtype=np.uint8).T  # inverse x and y axis

        # encode data to image
        ndata = np.array(list(map(int, data)), dtype=np.uint8)
        ndata = np.unpackbits(ndata).reshape(-1, 8)

        # use case
        ndatas = list()
        if ndata.size < image.size:
            # if data is smaller than image
            # flatten data and fill remaining space with 0
            ndata = ndata.flatten()
            ndata = np.append(ndata, np.zeros(image.size - ndata.size, dtype=np.uint8))
            ndatas.append(ndata)
        elif ndata.size > image.size:
            # if data is bigger than image
            # split data to chunks of image_size
            ndata = ndata.flatten()
            nbchunk = math.ceil(ndata.size / image.size)

            # fill remaining space with 0
            if rchunk := round((nbchunk - ndata.size / image.size) * image.size):
                ndata = np.append(ndata, np.zeros(rchunk, dtype=np.uint8))
                if nbchunk != ndata.size // image.size:
                    raise ValueError("Error when chunking data")

            ndatas = np.split(ndata, nbchunk)

        # convert data chunks to image
        for i, ndata in enumerate(ndatas):
            ndata = ndata.reshape(image.shape)
            ndata *= 255
            im = Image.fromarray(ndata, mode="L").convert("1")
            im.save(str(output_path).replace("%num%", str(i)), "PNG")

    @staticmethod
    def decode(*paths: str) -> bytes:
        # decode image to chunk array
        ndatas = list()
        for f in paths:
            im = Image.open(f)
            ndata = np.asarray(im.convert("L"))
            ndata = ndata // 255
            ndatas.append(ndata)

        # decode array to byte
        ndata = np.concatenate(ndatas)
        ndata = ndata.flatten()
        ndata = np.packbits(ndata)
        s = ndata.tobytes()

        return s

    @staticmethod
    def remove_endl(data: bytes) -> bytes:
        """
        Remove last empty block of data.

        Args:
            data (bytes): The data to process.

        Returns:
            bytes: The data without the last empty block.
        """
        i = 0
        for i in range(len(data) - 1, 0, -1):
            if data[i] != 0:
                break

        return bytes(data[: i + 1])
