import filecmp
import hashlib
from pathlib import Path
from utils import BitEncoding
from tarfile import open as taropen

SOURCE = Path('test/source')

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

################################################################################

def test_raw_text(tmp_path):
    data = b"hello world"
    image_output = tmp_path / 'test%num%.png'
    image_size = (10, 10)
    
    # encode
    BitEncoding.encode(data, image_size, str(image_output))
    
    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob('test*.png')):
        s += BitEncoding.decode(str(imagepath))
    
    s = BitEncoding.remove_endl(s)
    assert s == data
    assert s.decode() == data.decode()

def test_textfile(tmp_path):
    file_input = SOURCE / 'lorem.txt'
    image_output = tmp_path / 'test%num%.png'
    data = file_input.read_bytes()
    image_size = (200, 200)
    
    # encode
    BitEncoding.encode(data, image_size, str(image_output))
    
    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob('test*.png')):
        s += BitEncoding.decode(str(imagepath))
    
    s = BitEncoding.remove_endl(s)
    file_output = tmp_path / 'lorem_decoded.txt'
    file_output.write_bytes(s)
    
    assert s == data
    assert s.decode() == data.decode()
    assert filecmp.cmp(file_input, file_output)
    assert cmp_hash([file_input, file_output])

def test_image(tmp_path):
    file_input = SOURCE / 'sonic.png'
    image_output = tmp_path / 'test%num%.png'
    data = file_input.read_bytes()
    image_size = (1920, 1080)
    
    # encode
    BitEncoding.encode(data, image_size, str(image_output))
    
    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob('test*.png')):
        s += BitEncoding.decode(str(imagepath))
    
    s = BitEncoding.remove_endl(s)
    file_output = tmp_path / 'sonic_decoded.png'
    file_output.write_bytes(s)
    
    assert s == data
    assert filecmp.cmp(file_input, file_output)
    assert cmp_hash([file_input, file_output])

def test_pdf(tmp_path):
    file_input = SOURCE / 'movies.pdf'
    image_output = tmp_path / 'test%num%.png'
    data = file_input.read_bytes()
    image_size = (400, 400)
    
    # encode
    BitEncoding.encode(data, image_size, str(image_output))
    
    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob('test*.png')):
        s += BitEncoding.decode(str(imagepath))
    
    s = BitEncoding.remove_endl(s)
    file_output = tmp_path / 'movies_decoded.pdf'
    file_output.write_bytes(s)
    
    assert s == data
    assert filecmp.cmp(file_input, file_output)
    assert cmp_hash([file_input, file_output])

def test_archive(tmp_path):
    file_input = SOURCE / 'archive.tar'
    image_output = tmp_path / 'test%num%.png'
    data = file_input.read_bytes()
    image_size = (1920, 1080)
    
    # encode
    BitEncoding.encode(data, image_size, str(image_output))
    
    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob('test*.png')):
        s += BitEncoding.decode(str(imagepath))
    
    file_output = tmp_path / 'archive_decoded.tar'
    file_output.write_bytes(s)
    
    assert cmp_tar([file_input, file_output])
