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

NAME = sys.argv[1]
FOLDER_NAME = sys.argv[2]

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

frames = frame_list

with open('TotalDict.json','r') as f:
    sceneInfo = json.load(f)

with open("DataBetweenScenes.json","r") as f:
    refined_dict = json.load(f)



orb = cv2.xfeatures2d.SURF_create()


des_prev = []
bf = cv2.BFMatcher()
key_prev = None
kp_prev = []
counter = 0
sameSURFScenes = {}
listOfSameScenes = []
for key in sceneInfo.keys():

    sceneF = sceneInfo[key]['scene_frame_numbers']
    mid = len(sceneF)//2
    mid = sceneF[mid]
    f = frames[mid]
    kp_next, des_next = orb.detectAndCompute(f, None)
    key_next = key

    if(len(des_prev)>0):
        matches = bf.knnMatch(des_prev,des_next, k=2)
        good = []
        for m,n in matches:
            if m.distance < 0.65*n.distance:
                good.append([m])
                a=len(good)
                percent=(a*100)/len(kp_prev)
                if percent>=100.00:
                    break

        print(percent)
        if(percent>1):
            listOfSameScenes.append(key_prev)
            listOfSameScenes.append(key_next)
        else:
            if(len(listOfSameScenes)>0):
                sameSURFScenes[counter] = set(listOfSameScenes)
                listOfSameScenes = []
                counter+=1

    des_prev = des_next
    key_prev = key_next
    kp_prev = kp_next


if(len(listOfSameScenes)>0):
    sameSURFScenes[counter] = set(listOfSameScenes)


all_done_scenes = []
finalScenes = {}
for key in sameSURFScenes.keys():
    sceneAll = list(sameSURFScenes[key])
    for i in range(len(sceneAll)):
        sceneAll[i] = int(sceneAll[i])

    sceneAll.sort()
    start_scene = str(sceneAll[0])
    end_scene = str(sceneAll[-1])

    print(sceneAll)

    all_done_scenes.extend(sceneAll)

    start = sceneInfo[start_scene]['scene_frame_numbers'][0]
    end = sceneInfo[end_scene]['scene_frame_numbers'][-1]
    frames_list = [start,end]

    finalScenes[int(start_scene)] = frames_list

    print(start,end)

for key in sceneInfo.keys():
    if int(key) not in all_done_scenes:
        scene_frames = sceneInfo[key]['scene_frame_numbers']
        finalScenes[int(key)] = scene_frames


finalScenes = collections.OrderedDict(sorted(finalScenes.items()))

with open("scenesAfterSURF.json","w") as f:
    json.dump(finalScenes,f)

gap_dict = {}
k = list(finalScenes.keys())

for i in range(len(k)-1):
  start = k[i]
  end = k[i+1]

  #must be from start upto end-1
  temp_d = {}
  dc = []
  tg = 0
  for i in range(start,end,1):
    d = refined_dict[i]
    dc.append(d['DispersionCount'])
    tg+= d['TimeGap']

  md = max(dc)

  print(md,tg)

  temp_d['DispersionCount'] = md
  temp_d['TimeGap'] = tg

  gap_dict[start] = temp_d

frames = frame_list

with open("scenesAfterSURF.json","r") as f:
    scenes = json.load(f)

keys = list(scenes.keys())

groupedScenes = {}
counter = 0
temp_group = []

for i in range(len(keys)-1):

  s = keys[i]
  e = keys[i+1] 

  g = gap_dict[int(s)]

  if(g['TimeGap']>5):
    if(g['DispersionCount']<50):
      temp_group.append(s)
      temp_group.append(e)

    else:
      #break scenes
      temp_group.append(s)
      groupedScenes[s] = list(set(temp_group))
      temp_group = []


  else:
    temp_group.append(s)
    temp_group.append(e)


if(len(temp_group)>1):
  groupedScenes[s] = list(set(temp_group))


groupedScenes = collections.OrderedDict(sorted(groupedScenes.items()))

finalScenes = {}
for i in groupedScenes.keys():
  key = i
  l = groupedScenes[key]
  l.sort()

  if(len(l)>1):
    start = scenes[l[0]][0]
    end = scenes[l[-1]][-1]

    finalScenes[key] = [start,end]  

  else:
    scene_frames = scenes[l[0]]
    start = scene_frames[0]
    end = scene_frames[-1]
    finalScenes[key] = [start,end]


with open("FinalScenes.json","w") as f:
    json.dump(finalScenes,f,indent=4)
