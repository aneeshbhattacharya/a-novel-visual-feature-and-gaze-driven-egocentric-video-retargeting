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

with open("DataForGP.json","r") as f:
    userDataForGP = json.load(f)

with open("DataForTS.json","r") as f:
    userDataForTS = json.load(f)

with open("AllData.npy",'rb') as f:
    temp_list = np.load(f)

temp_list = np.array(temp_list)

temp_frame = frame_list[0]
temp_frame = np.array(temp_frame)
temp_frame.shape

w,h = temp_frame.shape

allGPList = [] 

for key in userDataForGP.keys():
    l = userDataForGP[key]

    for i in l:
        allGPList.append(i)

allGPList = np.array(allGPList)

midGP = np.mean(allGPList,axis=0)

finalDispersion = {}

for key in userDataForGP.keys():
    l = userDataForGP[key]
    temp = []
    for i in l:
        x_change = i[0]-midGP[0]
        y_change = i[1]-midGP[1]

        valM = (x_change**2)+(y_change**2)

        magnitudeOfChange = math.sqrt(valM)

        temp.append(magnitudeOfChange)

    finalDispersion[key] = temp


with open("DispersionMetric.json","w") as f:
    json.dump(finalDispersion,f)

with open('TotalDict.json','r') as f:
    sceneInfo = json.load(f)


frames = frame_list

with open("DispersionMetric.json",'rb') as f:
    dispersionDict = json.load(f)

dispDictKeyList = dispersionDict.keys()

print(sceneInfo)

timeSpans = {}


dispersionExceptScenes = {}

start_index = 0
for key in sceneInfo.keys():
    scene = sceneInfo[key]
    f = scene['scene_frame_numbers']
    start = start_index+1
    end = f[0]

    dispersionList = []
    for i in range(start,end,1):

        if(str(i) in dispDictKeyList):

            disp = dispersionDict[str(i)]
            dispersionList.extend(disp)

    dispersionExceptScenes[key] = dispersionList
    timeS = (end-start)/24
    timeSpans[key] = timeS


    print(start_index, end)
    start_index = f[-1]

betweenScenesData = {}    

for key in dispersionExceptScenes.keys():

    tempDict = {}
    t = timeSpans[key]

    dispersions = dispersionExceptScenes[key]


    dispMid = abs(round(np.mean(dispersions),2))

    dispCounter = 0

    for i in dispersions:
        if(i>dispMid):
            dispCounter+=1

    tempDict['DispersionCount'] = dispCounter
    tempDict['TimeGap'] = t


    betweenScenesData[key] = tempDict


with open("DataBetweenScenes.json","w") as f:
    json.dump(betweenScenesData,f)

betweenScenesData

dataBwScenes = betweenScenesData

disp_count = []
for key in dataBwScenes.keys():
    tempD = dataBwScenes[key]
    disp_count.append(int(tempD['DispersionCount']))

disp_count = np.array(disp_count)
mean_disp = np.mean(disp_count)
print(mean_disp)


refined_dict = {}
for key in betweenScenesData.keys():
    if(int(key)>0):
        data = dataBwScenes[key]
        refined_dict[int(key)-1] = data

with open("DataBetweenScenes.json","w") as f:
    json.dump(refined_dict,f)