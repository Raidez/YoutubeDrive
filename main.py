import os
import cv2 as cv

from enum import Enum
from pathlib import Path
from typing import TypeVar
from shutil import rmtree, copy
from PIL import Image, ImageDraw
from dataclasses import dataclass
from tarfile import open as taropen

@dataclass
class Vector:
    x: int
    y: int
    
    def __iter__(self):
        return iter((self.x, self.y))
    
    def __truediv__(self, other: int):
        return Vector(self.x / other, self.y / other)

class Byte(Enum):
    pass

PathLike = TypeVar("PathLike", str, bytes, os.PathLike, Path, None)
ImageSize = TypeVar("ImageSize", tuple[int, int], Vector, None)

def create_tar(source: PathLike, target: PathLike):
    """
    Create a tar file.

    Args:
        source (PathLike): The path to the source directory.
        target (PathLike): The path to save the tar file.
    
    TODO: allow to use a list of file instead of a folder
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
    
    # split data by 3
    # splited_data = [ data[i:i+3] for i in range(0, len(data), 3) ]
    
    # encode tar file to image
    image_size = Vector(1920, 1080)
    bytesize = Vector(4, 4)
    image_mode = '1'
    
    img = Image.new(image_mode, tuple(image_size))
    draw = ImageDraw.Draw(img)
    
    i, x, y = 0, 0, 0
    for b in data:
        # draw the data byte
        draw.rectangle((x, y, x+bytesize.x, y+bytesize.y), fill=b)
        
        # update position
        x += bytesize.x
        if (x + bytesize.x) > image_size.x:
            x = 0
            y += bytesize.y
        if (y + bytesize.y) > image_size.y:
            x, y = 0, 0
            
            # save and create a new image
            img.save(str(target).replace('%num%', str(i)))
            img = Image.new(image_mode, tuple(image_size))
            draw = ImageDraw.Draw(img)
            i += 1
    
    img.save(str(target).replace('%num%', str(i)))
    
    return image_size

def encode_images2video(sources: [PathLike], target: PathLike, image_size: ImageSize, fps = 1):
    """
    Function to encode a tar file to a video.

    Args:
        sources ([PathLike]): The path to the source image files.
        target (PathLike): The path to save the encoded video file.
        image_size (ImageSize): The size of each image.
        fps (int, optional): The frames per second. Defaults to 1.
    """
    video = cv.VideoWriter(str(target), cv.VideoWriter_fourcc(*'mp4v'), fps, tuple(image_size))
    
    for file in sources:
        frame = cv.imread(str(file))
        video.write(frame)
    
    video.release()

def decode_video2images(source: PathLike, target: PathLike):
    """
    Function to decode a video file to multiple images.

    Args:
        source (PathLike): The path to the source video file.
        target (PathLike): The path to save the decoded image files (%num% for each image).

    Raises:
        Exception: If the video can't be opened.
    """
    capture = cv.VideoCapture(str(source))
    
    if not capture.isOpened():
        raise Exception("Can't open video")
    
    i = 0
    while True:
        ret, frame = capture.read()
        if not ret:
            break
        
        cv.imwrite(str(target).replace('%num%', str(i)), frame)
        i += 1
    
    capture.release()

def decode_images2tar(sources: [PathLike], target: PathLike):
    """
    Function to decode multiple images to a tar file.

    Args:
        sources ([PathLike]): The path to the source image files.
        target (PathLike): The path to save the decoded tar file.
    """
    pass

################################################################################

if __name__ == '__main__':
    # print("start encoding process")
    # basename = Path('encode')
    # source_dir = basename / 'source'
    # target_dir = basename / 'target'
    
    # print("clean previous tests")
    # rmtree(target_dir, ignore_errors=True)
    # target_dir.mkdir()
    
    # print("create tar and encode to images")
    # tarname = target_dir / 'target.tar'
    # create_tar(source_dir, tarname)
    # image_size = encode_tar2images(tarname, target_dir / 'target%num%.png')
    
    # print("encode tar to video")
    # images = sorted(list(target_dir.glob('target*.png')))
    # video = target_dir / 'target.mp4'
    # encode_images2video(images, video, image_size)
    
    # # print("upload video")
    # print("copy video")
    # copy(video, 'decode/source/encoded.mp4')
    
    # print("done encoding process")
    
    ############################################################################
    
    print("start decoding process")
    basename = Path('decode')
    source_dir = basename / 'source'
    target_dir = basename / 'target'
    
    print("clean previous tests")
    rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir()
    
    print("decode video to images")
    decode_video2images(source_dir / 'encoded.mp4', target_dir / 'encoded%num%.png')
    # decode_video2images(source_dir / 'download.mp4', target_dir / 'download%num%.png')
    
    print("decode images to tar")
    decode_images2tar(target_dir / 'encoded*.png', target_dir / 'target.tar')
    
    # print("untar files")
    
    print("done decoding process")
