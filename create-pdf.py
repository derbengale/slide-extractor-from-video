''' 
	This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    Author: Alessandro Capezzera <Demacri>
'''
import os
import sys
import hashlib
import cv2
import numpy as np
import re
from skimage.metrics import structural_similarity as ssim
from PIL import Image, ImageChops
import imagehash

found_and_removed = 0

argument1=''
argument2=''

try:
    argument1=sys.argv[1]
except:
    print('No Arguments were given. Aborting')

try:
    argument2=sys.argv[2]
except:
    argument2='Output.pdf'

#dir_name = sys.argv[1].split("/")[-1].split(".")[0]

#output_dir = './' + dir_name



#need to add commandline parameter to run independently
def checkfolder(dir_name, sensitivity=0.85):

    found_and_removed = 0
    last_frame_read = None
    print("rechecking for duplicates in folder: " + dir_name + " Sensitivity= " + str(sensitivity))

    for filename in os.listdir(dir_name):
        filename = dir_name+"/" + filename
        current_frame = cv2.imread(filename)
        current_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        if(last_frame_read is not None):
            similarity = ssim(current_frame, last_frame_read)
            if(similarity > sensitivity):
                found_and_removed += 1
                #what to do next may be chosen by commandlineparameter

                #os.remove(filename)   
                print("duplicate: " + filename) 
                #os.startfile(filename)


        
        last_frame_read = current_frame

    print("duplicate found: " + str(found_and_removed))


def create_pdf(dir_name, outputfilepath=r'My PDF file.pdf'):
    imagelist = []
    print("creating pdf..")

    i=0
    for filename in os.listdir(dir_name):
        onlyfilename, extension = os.path.splitext(filename)
        if(extension=='.jpg'):
            filename = dir_name+"/" + filename
            
            if(i==0):
                image0=Image.open(filename)
            else:
                imagelist.append(Image.open(filename))
            print("adding " + filename)
            i += 1
    print("Successfully loaded all images. Saving file.")
    image0.save(outputfilepath,save_all=True, append_images=imagelist)
    print("done")
    os.startfile(outputfilepath)


create_pdf(dir_name=argument1, outputfilepath=argument2)