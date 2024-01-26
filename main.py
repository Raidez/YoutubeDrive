import os
import cv2

from pygame import display
from PIL import Image
from pathlib import Path
from shutil import rmtree
from typing import TypeVar
from tarfile import open as taropen

PathLike = TypeVar("PathLike", str, bytes, os.PathLike, Path, None)
ImageSize = TypeVar("ImageSize", tuple[int, int], None)

def create_tar(source: PathLike, target: PathLike):
    """
    Create a tar file.

    Args:
        source (PathLike): The path to the source directory.
        target (PathLike): The path to save the tar file.
    """
    with taropen(target, 'w') as tar:
        tar.add(source, "")

def encode_tar2images(source: PathLike, target: PathLike) -> ImageSize:
    """
    Function to encode a tar file to multiples images.

    Args:
        source (PathLike): The path to the source tar file.
        target (PathLike): The path to save the encoded image files (%num% for each image).
    
    Returns:
        ImageSize: The size of each image.
    """
    # extrat bytes data from the tar
    data = bytes()
    with open(source, 'rb') as file:
        data = file.read()
    
    # split data by 4
    splited_data = [ data[i:i+4] for i in range(0, len(data), 4) ]
    
    display.init()
    supported_modes = [ mode for mode in sorted(display.list_modes()) if len(splited_data) <= mode[0]*mode[1] ]
    mode = supported_modes[0]
    
    # encode tar file to image
    mode = (20, 20)
    img = Image.new('RGBA', mode)
    i, x, y = 0, 0, 0
    for b in splited_data:
        img.putpixel((x, y), tuple(b))
        
        x += 1
        if x >= mode[0]:
            x = 0
            y += 1
        if y >= mode[1]:
            x, y = 0, 0
            
            img.save(str(target).replace('%num%', str(i)))
            img = Image.new('RGBA', mode)
            i += 1
    
    img.save(str(target).replace('%num%', str(i)))
    
    return mode

def encode_images2avi(sources: [PathLike], target: PathLike, image_size: ImageSize, fps = 1):
    """
    Function to encode a tar file to an avi file.

    Args:
        sources ([PathLike]): The path to the source image files.
        target (PathLike): The path to save the encoded avi file.
        image_size (ImageSize): The size of each image.
        fps (int, optional): The frames per second. Defaults to 1.
    """
    video = cv2.VideoWriter(str(target), cv2.VideoWriter_fourcc(*'RGBA'), fps, image_size)
    
    for file in sources:
        img = cv2.imread(str(file))
        video.write(img)
    
    video.release()

def decode_avi2images(source: PathLike, target: PathLike):
    video = cv2.VideoCapture(str(source))
    
    video.read()
    
    video.release()

################################################################################

if __name__ == '__main__':
    basename = Path('YoutubeDrive')
    source_dir = basename / 'source'
    target_dir = basename / 'target'
    
    # clean previous tests
    rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir()
    
    tarname = target_dir / 'target.tar'
    
    create_tar(source_dir, tarname)
    image_size = encode_tar2images(tarname, target_dir / 'target%num%.png')
    
    images = sorted(list(target_dir.glob('target*.png')))
    encode_images2avi(images, target_dir / 'target.avi', image_size)
    
    print("Done")
