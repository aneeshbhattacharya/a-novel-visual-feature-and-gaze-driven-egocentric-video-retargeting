import numpy as np
import cv2
import statistics
from scipy.fftpack import fft, dct, idct
from scipy.signal import savgol_filter
import sys
import json
import math
import matplotlib.pyplot as plt
import collections
import pickle
import glob
import os
from scipy import spatial
import shutil
import json

# Provide the NAME and FOLDER NAME of Video path and Gaze Data path

NAME = NAME+"_"+FOLDER_NAME

frame_list = []
cap = cv2.VideoCapture(FOLDER_NAME+"/"+NAME+".avi")
while True:
    ret,frame = cap.read()
    if ret == True:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_list.append(gray)

    else:
        break
cap.release()

frames = frame_list

with open("TotalDict.json","r") as f:
    totalDict = json.load(f)

with open("FinalScenes.json","r") as f:
    finalScenes = json.load(f)

with open("DataForGP.json","r") as f:
    dataForGP = json.load(f)

mapper = {}
sceneKeys = totalDict.keys()
for key in finalScenes.keys():
    f = finalScenes[key]
    start_frame = f[0]
    end_frame = f[-1]


    l = []

    for k in sceneKeys:

        temp = totalDict[k]['scene_frame_numbers']

        if(int(temp[0])>=int(start_frame) and int(temp[-1])<=int(end_frame)):
            l.append(k)

        else:
            mapper[key] = l   

sceneBreakdown = {}
for key in mapper.keys():
    l = mapper[key]
    tempDict = {}


    if(len(l)>1):
        for i in range(len(l)-1):
            sceneFrames1 = totalDict[l[i]]['scene_frame_numbers']
            sceneFrames2 = totalDict[l[i+1]]['scene_frame_numbers']
            transitionDuration = sceneFrames2[0]-sceneFrames1[-1]
            print(transitionDuration)

            transition_start = sceneFrames1[-1]
            transition_end = sceneFrames2[0]

            transition = [transition_start,transition_end]

            tempDict['scene'+str(i)] = [sceneFrames1[0],sceneFrames1[-1]]
            tempDict['transition'+str(i)] = transition

        tempDict['scene'+str(i+1)] = [sceneFrames2[0],sceneFrames2[-1]]

        sceneBreakdown[key] = tempDict

    else:
        try:
            sceneFrames1 = totalDict[l[0]]['scene_frame_numbers']
            tempDict['scene'] = [sceneFrames1[0],sceneFrames1[-1]]
            sceneBreakdown[key] = tempDict
        except:
            pass



with open("SceneBreakdown.json","w") as f:
    json.dump(sceneBreakdown,f)

with open("SceneBreakdown.json","r") as f:
    sceneBreakdown = json.load(f)



user = NAME
part = "1"
scene_breakdown_location = "SceneBreakdown.json"
data_for_gp_location = "DataForGP.json"

frames = frame_list

with open(scene_breakdown_location,"r") as f:
    sceneBreakdown = json.load(f)

with open(data_for_gp_location,"r") as f:
    dataForGP = json.load(f)

def __zoom(img, scale, center=None,mid = None):
    # actual function to zoom
    height, width = img.shape[:2]
    if center is None:
        #   Calculation when the center value is the initial value
        center_x = int(width / 2)
        center_y = int(height / 2)

        # center_x = 0.5
        # center_y = 0.5
        radius_x, radius_y = int(width / 2), int(height / 2)
    else:
        #   Calculation at a specific location
        rate = 0.5
        try:
            center_x, center_y = center
            center_x = center_x*width
            center_y = center_y*height
        except:
            center_x = int(width / 2)
            center_y = int(height / 2)

    print("CENTER",center_x,center_y)


    #   Calculate centroids for ratio range
    if center_x < width * (1-rate):
        center_x = width * (1-rate)
    elif center_x > width * rate:
        center_x = width * rate
    if center_y < height * (1-rate):
        center_y = height * (1-rate)
    elif center_y > height * rate:
        center_y = height * rate

    center_x, center_y = int(center_x), int(center_y)
    left_x, right_x = center_x, int(width - center_x)
    up_y, down_y = int(height - center_y), center_y
    radius_x = min(left_x, right_x)
    radius_y = min(up_y, down_y)

    # Actual zoom code
    radius_x, radius_y = int(scale * radius_x), int(scale * radius_y)

    # size calculation
    min_x, max_x = center_x - radius_x, center_x + radius_x
    min_y, max_y = center_y - radius_y, center_y + radius_y

    # Crop image to size
    cropped = img[min_y:max_y, min_x:max_x]
    # Return to original size
    new_cropped = cv2.resize(cropped, (width, height))

#     new_cropped = cv2.circle(new_cropped, (int(mid[0]*width),int(mid[1]*height)), radius=0, color=(0, 0, 0), thickness=2)
    new_cropped = cv2.drawMarker(new_cropped, (int(mid[0]*width),int(mid[1]*height)), markerType=cv2.MARKER_CROSS,markerSize=30, 
                                    color=(0, 0, 0),thickness=3, line_type=cv2.LINE_AA)

    return new_cropped

def progressiveZoomIn(frame_start,frame_end,center,initial,dataForGP):
    list_of_modified_frames = []
    initial = initial
    update_factor = 0.005
    if(frame_end-frame_start)<20:

        #When such a small scene, no zoom

        update_factor = 0
        #0.05

    # print("CENTER",center)

    for i in range(frame_start,frame_end,1):
        f = frames[i]
        try:
            gp_value = dataForGP[str(i)]
        except:
            gp_value = [[0.5,0.5],[0.5,0.5]]
        gp_value = np.array(gp_value)

        if(gp_value.shape[0]==2):
            mid = np.mean(gp_value,axis=0)

        else:
            mid = np.array([0.5,0.5])

        zoomed = __zoom(f,initial,center,mid)
        list_of_modified_frames.append(zoomed)
        # list_of_modified_frames.append(f)

        if(initial>0.75):
            initial -= update_factor

    return list_of_modified_frames

def progressiveZoomOut(frame_start,frame_end,center,initial,dataForGP):
    list_of_modified_frames = []
    initial = initial
    update_factor = 0.01
    if(frame_end-frame_start)<20:
        update_factor = 0.05
        #0.05

    # print("CENTER", center)

    for i in range(frame_start,frame_end,1):
        f = frames[i]



        try:
            gp_value = dataForGP[str(i)]
        except:
            gp_value = [[0.5,0.5],[0.5,0.5]]

        gp_value = np.array(gp_value)

        if(gp_value.shape[0]==2):
            mid = np.mean(gp_value,axis=0)

        else:
            mid = np.array([0.5,0.5])

        zoomed = __zoom(f,initial,center,mid)
        list_of_modified_frames.append(zoomed)
        # list_of_modified_frames.append(f)
        if(initial<1):
            initial += update_factor

    return list_of_modified_frames

finalZoomedAndPanned = {}

for key in sceneBreakdown.keys():
    tempHolder = sceneBreakdown[key]

    entirePannedScene = []

    for k in tempHolder.keys():
        # print(k)
        if(k[:5]=="scene"):
            #Actually a scene
            start_frame = tempHolder[k][0]
            end_frame = tempHolder[k][-1]
            gp_data = []

            for i in range(start_frame,end_frame,1):
                try:
                    gp_data.extend(dataForGP[str(i)])
                except:
                    pass

            # print(gp_data)

            #take central ROI of data gp
            gp_data = np.array(gp_data)  
            mean = np.mean(gp_data,axis=0)

            # print(gp_data)

            print("MEAN",mean)

            listOfModified = progressiveZoomIn(start_frame,end_frame,mean,1,dataForGP)
            entirePannedScene.extend(listOfModified)

        else:
            #Transition Frame
            start_frame = tempHolder[k][0]
            end_frame = tempHolder[k][-1]
            gp_data = []

            for i in range(start_frame,end_frame,1):
                try:
                    gp_value = dataForGP[str(i)]
                except:
                    gp_value = [[0.5,0.5],[0.5,0.5]]

            #take central ROI of data gp
            gp_data = np.array(gp_data)  
            mean = np.mean(gp_data,axis=0)
#             print(mean)

            listOfModified = progressiveZoomOut(start_frame,end_frame,mean,0.75,dataForGP)
            entirePannedScene.extend(listOfModified)

    finalZoomedAndPanned[key] = entirePannedScene



h = 960
w = 1280
for key in finalZoomedAndPanned.keys():
    try:
        os.makedirs("User"+user+"/Part"+part+"/"+key+"/")
    except:
        print("Error making dir")
        print("User"+user+"/Part"+part+"/"+key+"/")
        pass
    frames = finalZoomedAndPanned[key]
    print(len(frames))

    video_name = "User"+user+"/Part"+part+"/"+key+"RT_FINAL.mp4"
    video = cv2.VideoWriter(video_name, 0x7634706d, 24, (1280, 960))

    for x in range(len(frames)):
        filename = "User"+user+"/Part"+part+"/"+key+"/"+str(x)+"NR.jpg"
        cv2.imwrite(filename,frames[x])

        temp_f = "User"+user+"/Part"+part+"/"+key+"/"+str(x)+"NR.jpg"
        frame = cv2.imread(temp_f)
        video.write(frame)
    video.release()
    
    shutil.rmtree("User"+user+"/Part"+part+"/"+key)