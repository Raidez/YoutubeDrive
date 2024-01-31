import hashlib
from pathlib import Path
from utils import BitEncoding

BASE = Path('test')
SOURCE = BASE / 'source'
TARGET = BASE / 'target'

def test_raw_text():
    data = b"hello world"
    image_size = (10, 10)
    print(len(data) * 8, image_size[0] * image_size[1])
    
    # encode
    BitEncoding.encode(data, image_size, str(TARGET / 'test%num%.png'))
    
    # decode
    s = bytes()
    for imagepath in sorted(TARGET.glob('test*.png')):
        s += BitEncoding.decode(str(imagepath))
    
    assert s == data
    assert s.decode() == data.decode()

def test_textfile():
    data = (SOURCE / 'lorem.txt').read_bytes()
    image_size = (200, 200)
    print(len(data) * 8, image_size[0] * image_size[1])
    
    # encode
    BitEncoding.encode(data, image_size, str(TARGET / 'test%num%.png'))
    
    # decode
    s = bytes()
    for imagepath in sorted(TARGET.glob('test*.png')):
        s += BitEncoding.decode(str(imagepath))
    
    (TARGET / 'lorem_decoded.txt').write_bytes(s)
    
    assert s == data
    assert s.decode() == data.decode()
    
    diggests = []
    for filename in [(SOURCE / 'lorem.txt'), (TARGET / 'lorem_decoded.txt')]:
        diggests.append(
            hashlib.md5(filename.read_bytes()).hexdigest()
        )
    assert diggests[0] == diggests[1]

def test_pdf():
    data = (SOURCE / 'movies.pdf').read_bytes()
    image_size = (400, 400)
    print(len(data) * 8, image_size[0] * image_size[1])
    
    # encode
    BitEncoding.encode(data, image_size, str(TARGET / 'test%num%.png'))
    
    # decode
    s = bytes()
    for imagepath in sorted(TARGET.glob('test*.png')):
        s += BitEncoding.decode(str(imagepath), False)
    
    (TARGET / 'movies_decoded.pdf').write_bytes(s)
    
    assert s == data
    assert s.decode() == data.decode()
    
    diggests = []
    for filename in [(SOURCE / 'movies.pdf'), (TARGET / 'movies_decoded.pdf')]:
        diggests.append(
            hashlib.md5(filename.read_bytes()).hexdigest()
        )
    assert diggests[0] == diggests[1]
