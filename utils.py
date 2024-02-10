import copy
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


def numpy_zoom(array: np.ndarray, factor: int) -> np.ndarray:
    """
    Zoom in/out an array.

    Args:
        array (np.ndarray): The array.
        factor (int): The scale factor (use negative value to zoom out).

    Returns
        np.ndarray: The zoomed array.
    """
    if factor >= 0:
        return np.repeat(np.repeat(array, factor, axis=0), factor, axis=1)
    else:
        return array[:: abs(factor), :: abs(factor)]


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

    BITSIZE = 4

    @staticmethod
    def encode(data: bytes, image_size: tuple[int, int], output_path: str):
        # check if image_size is a multiple of BITSIZE
        if (
            image_size[0] % BitEncoding.BITSIZE != 0
            or image_size[1] % BitEncoding.BITSIZE != 0
        ):
            raise ValueError(
                f"image_size ({image_size}) must be a multiple of {BitEncoding.BITSIZE}"
            )

        ndata = np.array(list(map(int, data)), dtype=np.uint8)
        ndata = np.unpackbits(ndata).reshape(-1, 8)
        ndata = numpy_zoom(ndata, BitEncoding.BITSIZE)

        im = Image.fromarray(ndata, "1")
        draw = ImageDraw.Draw(im)

        # TODO: use numpy manipulation instead of naive rectangle
        i, x, y = 0, 0, 0
        dx, dy = BitEncoding.BITSIZE
        for byte in data:
            for bit in reversed(list(biter(byte))):
                draw.rectangle((x, y, x + dx, y + dy), fill=bit)
                x += dx

                # next row
                if x >= image_size[0]:
                    x = 0
                    y += dy

                # next image
                if y >= image_size[1]:
                    im.save(output_path.replace("%num%", str(i)))
                    im = Image.new("1", image_size)
                    draw = ImageDraw.Draw(im)
                    x, y = 0, 0
                    i += 1

        im.save(output_path.replace("%num%", str(i)))

    @staticmethod
    def decode(path: str) -> bytes:
        im = Image.open(path)
        # TODO: use numpy manipulation instead of naive image resize
        im = im.resize(
            (im.size[0] // BitEncoding.BITSIZE[0], im.size[1] // BitEncoding.BITSIZE[1])
        )

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
