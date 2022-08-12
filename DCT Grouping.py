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

# implement 2D DCT
def dct2(a):
    return dct(dct(a.T, norm='ortho').T, norm='ortho')

# implement 2D IDCT
def idct2(a):
    return idct(idct(a.T, norm='ortho').T, norm='ortho') 

def zigzag(a):
    rows = a.shape[0]
    columns = a.shape[1]
    solution=[[] for i in range(rows+columns-1)]
    matrix = a
    r_mat = []  
    for i in range(rows):
        for j in range(columns):
            summer=i+j
            if(summer%2 ==0):


                solution[summer].insert(0,matrix[i][j])
            else:


                solution[summer].append(matrix[i][j])


    # print the solution as it as
    for i in solution:
        for j in i:
            r_mat.append(j)

    return r_mat

mean_list = []
stdev_list = []
blurred_frames = []
for i in range(0,len(frame_list),15):
    img = frame_list[i]
    img = cv2.GaussianBlur(img, (205, 205), 0)
    blurred_frames.append(img)
    dct_transform = dct2(img)
    z = zigzag(dct_transform)
    z = z[:500]
#     m = statistics.mean(z)
    m = z
    std = statistics.stdev(z)
    mean_list.append(m)
    stdev_list.append(std)
#     print("Frame number {} Mean is {} Stdev is {}".format(i,m,std))

# smooth_mean = savgol_filter(mean_list, 51, 3) 

total_dict = {}
scenes_dict = {
    'scene_mean_list' : [],
    'scene_frame_numbers' : [] 
}

temp_list = []
frame_numer_list = []
scene_counter = 0
for i in range(len(mean_list)-1):

#     if(abs(mean_list[i+1]-mean_list[i])<4):
#         temp_list.append(mean_list[i])
#         frame_numer_list.append(i*5)

    m1 = mean_list[i+1]
    m2 = mean_list[i]

    d =  spatial.distance.cosine(m1, m2)

    print(d)

    if(d<0.05):
        temp_list.append(mean_list[i])
        frame_numer_list.append(i*15)
    else:
        if(len(temp_list)>2):
            scenes_dict['scene_mean_list'] = temp_list
            scenes_dict['scene_frame_numbers'] = frame_numer_list
            total_dict[scene_counter] = scenes_dict
            scene_counter+=1
        scenes_dict = {}
        temp_list = []
        frame_numer_list = []

with open('TotalDict.json','w') as f:
    json.dump(total_dict,f)

foundStart = False
totalList = []
with open(FOLDER_NAME+"/"+NAME+'.txt','r') as f:
    for line in f:
        if(line[0] == 'T'):
            foundStart = True
        else:
            if(foundStart==True):
                tempDict = {}

                l = line.split('\t')

                tempDict['ts'] = int(l[0])
                x = round(float(l[3])/1280,2)
                y = round(float(l[4])/960,2)
                tempDict['gp'] = (x,y)
                tempDict['imageNum'] = int(l[5])
                if(x>=0 and y>=0 and x<=1 and y<=1):
                    totalList.append(tempDict)

temp_list = []
for i in range(len(totalList)):
    tempDict = totalList[i]
    if(int(tempDict['imageNum'])<=len(frame_list)):
        temp_list.append(tempDict)

userDataForGP = {}
imageNumPrev = 0
temp_gp_data = []

for i in range(len(temp_list)):

    tempDict = temp_list[i]
    imageNum = int(tempDict['imageNum'])

    if(imageNum!= imageNumPrev or imageNum==0):
        userDataForGP[imageNumPrev] = temp_gp_data
        imageNumPrev = imageNum
        temp_gp_data = []

    gp_data = list(tempDict['gp'])
    temp_gp_data.append(gp_data)
    imageNumPrev = imageNum

userDataForTS = {}
imageNumPrev = 0
temp_ts_data = []

for i in range(len(temp_list)):

    tempDict = temp_list[i]
    imageNum = int(tempDict['imageNum'])

    if(imageNum!= imageNumPrev or imageNum==0):
        userDataForTS[imageNumPrev] = temp_ts_data
        imageNumPrev = imageNum
        temp_ts_data = []

    ts_data = int(tempDict['ts'])
    temp_ts_data.append(ts_data)
    imageNumPrev = imageNum

with open("DataForGP.json","w") as f:
    json.dump(userDataForGP,f)

with open("DataForTS.json","w") as f:
    json.dump(userDataForTS,f)

temp_list = np.array(temp_list)

with open("AllData.npy",'wb') as f:
    np.save(f,temp_list)