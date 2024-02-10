import pytest
import shutil
import filecmp
import hashlib
from pathlib import Path
from utils import BitEncoding, VideoEncoding
from tarfile import open as taropen

SOURCE = Path("test/source")
TARGET = Path("test/target")


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
        with open(filename, "rb") as f:
            diggests.append(hashlib.md5(f.read()).hexdigest())
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
            diggests[i].append({"name": m.name, "size": m.size, "chksum": m.chksum})
    return diggests[0] == diggests[1]


@pytest.fixture(scope="session", autouse=True)
def teardown():
    # before
    yield
    # after
    shutil.rmtree(TARGET)
    TARGET.mkdir()


############################# encode file to image #############################


def test_raw_text(tmp_path):
    data = b"hello world"
    image_size = (40, 40)
    image_output = tmp_path / 'frame%num%.png'
    
    # encode
    BitEncoding.encode(data, image_size, str(image_output))

    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob("frame*.png")):
        s += BitEncoding.decode(str(imagepath))

    s = BitEncoding.remove_endl(s)
    assert s == data
    assert s.decode() == data.decode()


def test_textfile(tmp_path):
    file_input = SOURCE / "lorem.txt"
    data = file_input.read_bytes()
    image_size = (200, 200)
    image_output = tmp_path / "frame%num%.png"
    file_output = tmp_path / "lorem.txt"

    # encode
    BitEncoding.encode(data, image_size, str(image_output))

    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob("frame*.png")):
        s += BitEncoding.decode(str(imagepath))

    s = BitEncoding.remove_endl(s)
    file_output.write_bytes(s)

    assert s == data
    assert s.decode() == data.decode()
    assert filecmp.cmp(file_input, file_output)
    assert cmp_hash([str(file_input), file_output])


def test_image(tmp_path):
    file_input = SOURCE / "sonic.png"
    data = file_input.read_bytes()
    image_size = (1920, 1080)
    image_output = tmp_path / "frame%num%.png"
    file_output = tmp_path / "sonic.png"

    # encode
    BitEncoding.encode(data, image_size, str(image_output))

    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob("frame*.png")):
        s += BitEncoding.decode(str(imagepath))

    s = BitEncoding.remove_endl(s)
    file_output.write_bytes(s)

    assert s == data
    assert filecmp.cmp(file_input, file_output)
    assert cmp_hash([str(file_input), file_output])


def test_pdf(tmp_path):
    file_input = SOURCE / "movies.pdf"
    data = file_input.read_bytes()
    image_size = (400, 400)
    image_output = tmp_path / "frame%num%.png"
    file_output = tmp_path / "movies.pdf"

    # encode
    BitEncoding.encode(data, image_size, str(image_output))

    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob("frame*.png")):
        s += BitEncoding.decode(str(imagepath))

    s = BitEncoding.remove_endl(s)
    file_output.write_bytes(s)

    assert s == data
    assert filecmp.cmp(file_input, file_output)
    assert cmp_hash([str(file_input), file_output])


def test_archive(tmp_path):
    file_input = SOURCE / "archive.tar"
    data = file_input.read_bytes()
    image_size = (1920, 1080)
    image_output = tmp_path / "frame%num%.png"
    file_output = tmp_path / "archive.tar"

    # encode
    BitEncoding.encode(data, image_size, str(image_output))

    # decode
    s = bytes()
    for imagepath in sorted(tmp_path.glob("frame*.png")):
        s += BitEncoding.decode(str(imagepath))
    file_output.write_bytes(s)

    assert cmp_tar([str(file_input), file_output])


############################# encode image to video ############################


@pytest.fixture
def images(tmp_path):
    file_input = SOURCE / "archive.tar"
    data = file_input.read_bytes()
    image_size = (1920, 1080)
    image_output = tmp_path / "original-frame%num%.png"

    BitEncoding.encode(data, image_size, str(image_output))
    return map(str, sorted(tmp_path.glob("original-frame*.png")))


def test_raw_video(images, tmp_path):
    video_size = (1920, 1080)
    video_output = tmp_path / "video.avi"
    image_output = tmp_path / "frame%num%.png"
    file_output = tmp_path / "archive.tar"
    file_input = SOURCE / "archive.tar"

    # encode/decode video
    VideoEncoding.encode(images, video_size, str(video_output))
    VideoEncoding.decode(str(video_output), str(image_output))

    # decode archive
    s = bytes()
    for imagepath in sorted(tmp_path.glob("frame*.png")):
        s += BitEncoding.decode(str(imagepath))

    file_output.write_bytes(s)

    assert cmp_tar([str(file_input), file_output])


@pytest.mark.skip(reason="Video encoding give a too blurry result")
def test_upload_video(tmp_path):
    tmp_path = TARGET
    video_input = SOURCE / "video_360p.mp4"
    file_input = SOURCE / "archive.tar"
    image_output = tmp_path / "frame%num%.png"
    file_output = tmp_path / "archive.tar"

    # decode video
    VideoEncoding.decode(str(video_input), str(image_output))

    # decode archive
    s = bytes()
    for imagepath in sorted(tmp_path.glob("frame*.png")):
        s += BitEncoding.decode(str(imagepath))

    file_output.write_bytes(s)

    assert cmp_tar([str(file_input), str(file_output)])
