from pathlib import Path
from PIL import Image, ImageDraw
# https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes

def biter(b: int, step = 1):
    """
    Iterate over the bits of an integer.

    Args:
        b (int): The integer to generate binary numbers for.

    Yields:
        int: The binary numbers.
    """
    for i in range(0, 8, step):
        yield b >> i & 1

class Encoding:
    """
    Encode/decode byte data to image.
    """
    @staticmethod
    def encode(data: bytes, image_size: tuple[int, int], output_path: str):
        raise NotImplementedError
    
    @staticmethod
    def decode(path: str):
        raise NotImplementedError

class BitEncoding(Encoding):
    @staticmethod
    def encode(data: bytes, image_size: tuple[int, int], output_path: str):
        im = Image.new('1', image_size)
    
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
                    im.save(output_path.replace('%num%', str(i)))
                    im = Image.new('1', image_size)
                    x, y = 0, 0
                    i += 1
        
        im.save(output_path.replace('%num%', str(i)))
    
    @staticmethod
    def decode(path: str) -> bytes:
        im = Image.open(path)
        
        out = bytearray()
        data = list(im.getdata())
        for i in range(0, len(data), 8):
            bits = data[i:i+8]
            bits = [1 if b == 255 else 0 for b in bits]
            byte = int(''.join(map(str, bits)), 2)
            out.append(byte)
        
        return bytes(out)
    
    @staticmethod
    def remove_endl(data: bytes) -> bytes:
        for i in range(len(data) - 1, 0, -1):
            if data[i] != 0:
                break
        
        return bytes(data[:i+1])
