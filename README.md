# slide-extractor-from-video
This simple python script will extract your video presentation (from url or local filename) into splitted images.
Tested with python3 on windows.

# Required
1) ffmpeg
2) opencv python module
```
$ pip install opencv-python
```
# How to use
Run command like:
```
$ python export-slide.py <url>
  ```
OR
```
$ python export-slide.py <filename>

To create a PDF file out ot images in a Folder:

$ python create-pdf.py "folder" "Outputfile.pdf"


  ```
