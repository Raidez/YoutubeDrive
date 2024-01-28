YoutubeDrive
============

Can convert anything to an Youtube video, so you can stock anything.

References:
* [youtube specifications](https://support.google.com/youtube/answer/1722171?hl=en)
* [original video idea](https://www.youtube.com/watch?v=_w6PCHutmb4)
* [opencv librairie](https://docs.opencv.org/3.4/dd/d9e/classcv_1_1VideoWriter.html)
* [python tarfile module](https://docs.python.org/3/library/tarfile.html)

How it works
============
1. Create a TAR archive (uncompressed) with several files
2. Convert the TAR binary data into a set of images
3. Create a video with the images
4. Upload the video to Youtube
5. Download the video
6. Repeat the process in reverse
