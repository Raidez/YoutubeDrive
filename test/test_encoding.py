import pytest
import shutil
import filecmp
import hashlib
import cv2 as cv
from pathlib import Path
from utils import BitEncoding
from tarfile import open as taropen

SOURCE = Path('test/source')
TARGET = Path('test/target')

def cmp_hash(files: list[str]) -> bool:
    """
    Compare the hash of two files.

    Args:
        files (list[str]): The list of files to compare.

    Returns:
        bool: If the files are the same.
    """
    diggests = []
    for filename in files:
        diggests.append(
            hashlib.md5(filename.read_bytes()).hexdigest()
        )
    return diggests[0] == diggests[1]

def cmp_tar(files: list[str]) -> bool:
    """
    Compare the content of two tar files.

    Args:
        files (list[str]): The list of files to compare.

    Returns:
        bool: If the files had the same content.
    """
    diggests = [[], []]
    for i, filename in enumerate(files):
        f = taropen(filename)
        for m in f.getmembers():
            diggests[i].append({
                'name': m.name,
                'size': m.size,
                'chksum': m.chksum
            })
    return diggests[0] == diggests[1]

@pytest.fixture(scope='session', autouse=True)
def teardown():
    # before
    yield
    # after
    shutil.rmtree(TARGET)
    TARGET.mkdir()

############################# encode file to image #############################

def test_raw_text(tmp_path):
    data = b"hello world"
    image_size = (10, 10)
    image_output = tmp_path / 'frame%num%.png'
    
    # encode
    BitEncoding.encode(data, image_size, str(image_output))
    
    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob('*.png')):
        s += BitEncoding.decode(str(imagepath))
    
    s = BitEncoding.remove_endl(s)
    assert s == data
    assert s.decode() == data.decode()

def test_textfile(tmp_path):
    file_input = SOURCE / 'lorem.txt'
    data = file_input.read_bytes()
    image_size = (200, 200)
    image_output = tmp_path / 'frame%num%.png'
    file_output = tmp_path / 'lorem_decoded.txt'
    
    # encode
    BitEncoding.encode(data, image_size, str(image_output))
    
    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob('*.png')):
        s += BitEncoding.decode(str(imagepath))
    
    s = BitEncoding.remove_endl(s)
    file_output.write_bytes(s)
    
    assert s == data
    assert s.decode() == data.decode()
    assert filecmp.cmp(file_input, file_output)
    assert cmp_hash([file_input, file_output])

def test_image(tmp_path):
    file_input = SOURCE / 'sonic.png'
    data = file_input.read_bytes()
    image_size = (1920, 1080)
    image_output = tmp_path / 'frame%num%.png'
    file_output = tmp_path / 'sonic_decoded.png'
    
    # encode
    BitEncoding.encode(data, image_size, str(image_output))
    
    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob('*.png')):
        s += BitEncoding.decode(str(imagepath))
    
    s = BitEncoding.remove_endl(s)
    file_output.write_bytes(s)
    
    assert s == data
    assert filecmp.cmp(file_input, file_output)
    assert cmp_hash([file_input, file_output])

def test_pdf(tmp_path):
    file_input = SOURCE / 'movies.pdf'
    data = file_input.read_bytes()
    image_size = (400, 400)
    image_output = tmp_path / 'frame%num%.png'
    file_output = tmp_path / 'movies_decoded.pdf'
    
    # encode
    BitEncoding.encode(data, image_size, str(image_output))
    
    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob('*.png')):
        s += BitEncoding.decode(str(imagepath))
    
    s = BitEncoding.remove_endl(s)
    file_output.write_bytes(s)
    
    assert s == data
    assert filecmp.cmp(file_input, file_output)
    assert cmp_hash([file_input, file_output])

def test_archive(tmp_path):
    file_input = SOURCE / 'archive.tar'
    data = file_input.read_bytes()
    image_size = (1920, 1080)
    image_output = tmp_path / 'frame%num%.png'
    file_output = tmp_path / 'archive_decoded.tar'
    
    # encode
    BitEncoding.encode(data, image_size, str(image_output))
    
    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob('*.png')):
        s += BitEncoding.decode(str(imagepath))
    file_output.write_bytes(s)
    
    assert cmp_tar([file_input, file_output])

############################# encode image to video ############################

@pytest.fixture
def images(tmp_path):
    file_input = SOURCE / 'archive.tar'
    data = file_input.read_bytes()
    image_size = (1920, 1080)
    image_output = tmp_path / 'frame%num%.png'
    
    BitEncoding.encode(data, image_size, str(image_output))
    return sorted(tmp_path.glob('*.png'))

def test_video(images, tmp_path):
    tmp_path = TARGET
    video_fps = 1
    video_size = (1920, 1080)
    video_output = tmp_path / 'video.avi'
    video_codec = cv.VideoWriter_fourcc(*'RGBA')
    image_output = tmp_path / 'frame%num%.png'
    file_output = tmp_path / 'archive_decoded.tar'
    file_input = SOURCE / 'archive.tar'
    
    # encode images to video
    video = cv.VideoWriter(str(video_output), video_codec, video_fps, video_size)
    for imagepath in images:
        frame = cv.imread(str(imagepath))
        video.write(frame)
    video.release()
    
    # decode video to images
    cap = cv.VideoCapture(str(video_output))
    if not cap.isOpened(): raise Exception("Can't open video")
    
    i = 0
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        cv.imwrite(str(image_output).replace('%num%', str(i)), frame)
        i += 1
    
    cap.release()
    
    # decode archive
    s = bytes()
    for imagepath in sorted(tmp_path.glob('*.png')):
        s += BitEncoding.decode(str(imagepath))
    
    file_output.write_bytes(s)
    
    assert cmp_tar([file_input, file_output])
