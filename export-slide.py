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
import cv2
import numpy as np
import re
from skimage.metrics import structural_similarity as ssim
from PIL import Image, ImageChops
import imagehash
from pathlib import Path
 

totalslides=0

def removePointer(images, target):
    onlyfilename =Path(target).stem

    #print('My target is' + target)
    i=0
    #print(len(images))
    if len(images) <= 1:
        cv2.imwrite(target, images[0])
        print(onlyfilename + ": Only one frame captured! Can't remove pointer because I don't have enough frames.")
        return None
    if(len(images) == 2):
        avg_img = np.mean(images, axis=0)
        avg_img = avg_img.astype(np.uint8)
        cv2.imwrite(target, avg_img)

        print(onlyfilename + ": Only two distinct frames collected. Averaging images.")
        return None
    else: 
        # images are scanned for significant diffences, 
        # boxes are put around the differences and saved coordniates,
        # these are cut out of every image in the series and compared.
        # The box with the most often ocurring content is finally copied to the output image,
        # and considered the "pointerless". It keeps the pointer if the mouse was not moved in the images of the series.
        # To fix this, filterig out of 
        # "near identical matches" (Structural Similarity>0.9995) 
        # happens beforehand, to delete identical images from the series. 
        # If there were only two distinct frames, they are averaged, so at least the pointers become transparent.
        
        print(onlyfilename + ": Removing pointer by comparing " + str(len(images)) + " distinct frames.")
        greyimages = []
        boxes = []
        fragments = []

        for image in images:
            greyimages.append(cv2.cvtColor(images[i], cv2.COLOR_BGR2GRAY))
            #greyimages.append(images[i])
            i+=1

        before=images[0]

        i=0
        for image in images:
            if(i < len(images)-1):
                #print(len(greyimages))
                (score, diff) = ssim(greyimages[0], greyimages[i+1], full=True)

                diff = (diff * 255).astype("uint8")
                thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
                contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours = contours[0] if len(contours) == 2 else contours[1]

                mask = np.zeros(before.shape, dtype='uint8')

                for c in contours:
                    area = cv2.contourArea(c)
                    if area > 40:
                        x,y,w,h = cv2.boundingRect(c)
                        boxes.append(((x, y), (x + w, y + h)))
                
                i+=1

        for box in boxes:
            fragments.append([])

        i=0
        for image in images:
            j=0
            for box in boxes:
                y   = box[0][1]     #y
                y1  = box[1][1]    #y+h
                x   = box[0][0]     #x
                x1  = box[1][0]    #x+w
                fragment = image[y:y1, x:x1]
                fragments[j].append(fragment)
                #cv2.imwrite('./fragments/' + str(j) + ' ' + str(i) + '.jpg', fragment)
                j+=1
            i+=1

        i=0
        for fragment in fragments:
            j=0
            distict_hashes= []
            occurences = []
            allhashes=[]
            for subfragment in fragment:
                subfragment = Image.fromarray(subfragment)
                hash = imagehash.average_hash(subfragment)
                allhashes.append(hash)  #contains all hashes 
                
                if hash in distict_hashes:
                    occurences[distict_hashes.index(hash)] +=1
                else:
                    distict_hashes.append(hash)
                    occurences.append(1)

                j+=1
            mostoccuring = occurences.index(max(occurences))
            mostcommonhash = distict_hashes[mostoccuring]
            best = allhashes.index(mostcommonhash)
                
            #fragment[best] contains the most often ocurring image fragment (the one without a pointer) in the borders saved in boxes[i], so lets insert that in our slide

            bestfragment = fragment[best] #contains pointerless image fragment 
                
            y   = boxes[i][0][1]     #y
            y1  = boxes[i][1][1]    #y+h
            x   = boxes[i][0][0]     #x
            x1  = boxes[i][1][0]    #x+w
                
            before[y:y1, x:x1] = bestfragment

            i+=1
            #print('target: ' + target )
        cv2.imwrite(target, before)

def remove_stepbacks(dir_name):    
    found_and_removed = 0
    imagehashes = []
    print("checking for stepbacks in folder: " + dir_name)

    for filename in os.listdir(dir_name):
        filename = dir_name+"/" + filename
        hash = imagehash.average_hash(Image.open(filename))
        if hash in imagehashes:
            os.remove(filename)
            
            print('removed ' + filename + '.')
            #print(hash)
            found_and_removed += 1
        else:
            imagehashes.append(hash)
        
    print("stepbacks found and removed: " + str(found_and_removed))
    return found_and_removed

step = 2.5 #take snapshot every n seconds
loglevel = 'panic' #otherwise: warning -- loglevel ffmpeg

regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

if(re.match(regex, sys.argv[1]) is not None):
	os.system('wget ' + sys.argv[1]+'')

dir_name = sys.argv[1].split("/")[-1].split(".")[0]
output_dir = './' + dir_name
os.system('mkdir ' + dir_name)
last_frame_read = None
filename = output_dir+'/%04d.jpg'
onlyfn =Path(sys.argv[1]).stem
print("extracting images with ffmpeg..")
os.system('ffmpeg -loglevel '+loglevel+' -i ' + sys.argv[1] + ' -vf fps=1/'+ str(step) +' -q:v 2 '+filename)

found_and_removed = 0
slide_group_images = []
n_of_this_slide=1
rem_of_this_slide=0
target= ''

for filename in os.listdir(output_dir):

    target = output_dir+"/" + onlyfn + '-Slide' + str(totalslides).zfill(4) +'.jpg'

    filename = output_dir+"/"+filename

    current_framec = cv2.imread(filename) #colored frames will be given to removepointer
    current_frame = cv2.cvtColor(current_framec, cv2.COLOR_BGR2GRAY)
    if(last_frame_read is not None):
        similarity = ssim(current_frame, last_frame_read)
        if(similarity > 0.90):
            n_of_this_slide +=1
            if(similarity>0.9995):
                os.remove(filename)
                #os.rename(filename, filename + '.toosimilar.jpg')  #rename instead of removing
                #print(filename + " Similarity " + str(similarity) + ". Pointer didn't move. Slide too similar.  Removing.")
                rem_of_this_slide += 1
            else:
                #print(filename + " Similarity " + str(similarity) + ". Pointer moved. Appending for pointer removal.")
                slide_group_images.append(current_framec) #keep other distinct frames in RAM 
                os.remove(filename)
        else:
            #print("Deleted " + str(rem_of_this_slide) + " distinct frames of a total of " + str(n_of_this_slide))
            #print(filename +  " Similarity " + str(similarity) + ". This seems to be another slide.")
            n_of_this_slide=1
            rem_of_this_slide=0
            if slide_group_images == []:  #if the first slide does not belong to a group it would crash here
                slide_group_images = [current_framec]
            removePointer(slide_group_images,target)
            totalslides += 1
            slide_group_images = [current_framec]
            os.remove(filename)
    
    last_frame_read = current_frame

#remove slides that were generated because the lecturer stepped back in the slides
removed = remove_stepbacks(output_dir)

print("found " + str(totalslides-removed) + " slides in total.")
