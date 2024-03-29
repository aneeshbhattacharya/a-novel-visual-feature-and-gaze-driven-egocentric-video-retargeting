# a-novel-visual-feature-and-gaze-driven-egocentric-video-retargeting
Official implementation of the paper "A NOVEL VISUAL FEATURE AND GAZE DRIVEN EGOCENTRIC VIDEO RETARGETING" accepted at the IEEE ICIP 2022 <br>
This work was done as part of my summer research internship at IIT Kharagpur under the guidance of Dr. Jayanta Mukhopadhyay and Mr. Sai Phani Kumar Malladi (PhD)

## Overview 
This paper proposes a novel visual feature and gaze driven approach to retarget egocentric videos following the principles of cinematography. This approach is divided into two parts: activity based scene detection and performing panning and zooming to produce visually immersive videos. <br>
<ol>
  <li>Firstly, visually similar frames are grouped using DCT feature matching followed by SURF descriptor matching. These groups are further refined using the gaze data to generate different scenes and transitions occurring within an activity.</li>
  <li>Secondly, the mean 2D gaze positions of scenes are used for generating panning windows enclosing $75\%$ of the frame content. This is done for performing zoom-in and zoom-out operations in the detected scenes and transitions respectively.</li>
</ol>

Our approach has been tested on the GTEA and EGTEA gaze plus datasets witnessing an average accuracy of 88.1% and 72% for sub-activity identification and obtaining an average aspect ratio similarity (ARS) score of 0.967 and 0.73; 60\% and 42\% SIFT similarity index (SSI) respectively.
<br>
<p align="center">
  <img src="https://user-images.githubusercontent.com/68210639/184424239-244ef170-1ab9-4879-b363-0aa96f9192ab.png" width="350">
</p>

## Implementation
### Conda Environment:
```
conda create -n env python=3.7.11
conda activate env
```
### Installing requirements:
```
git clone https://github.com/aneeshbhattacharya/a-novel-visual-feature-and-gaze-driven-egocentric-video-retargeting.git
cd a-novel-visual-feature-and-gaze-driven-egocentric-video-retargeting
pip install -r requirements.txt
```
### GTEA Gaze+ Gaze Data:
```
https://cbs.ic.gatech.edu/fpv/
```
### Running the code:
Place both the video and corresponding gaze data in a folder 'Food_Item/'<br>
Example: 'Pizza/Alireza_Pizza.avi' and 'Pizza/Alireza_Pizza.txt'<br>
```
python DCT_Grouping.py Pizza Alireza
python Dispersion_Metric.py Pizza Alireza
python SURF_SIFT_Grouping.py Pizza Alireza
python Render_RT.py Pizza Alireza
```
## Retargeted vs Non Retargeted 
### Spreading cheese on bagle
<p float="center">
  <img src="https://user-images.githubusercontent.com/68210639/184404868-4d05e7e8-0917-436b-be1a-bfc7c2440d3b.gif" width="400" />
  <img src="https://user-images.githubusercontent.com/68210639/184405440-8d9fd2c8-cb2d-4491-8d87-d60030252d15.gif" width="400" /> 
</p>

### Breaking eggs
<p float="center">
  <img src="https://user-images.githubusercontent.com/68210639/188937372-3b66b8a1-340d-4bbe-8787-733f2d4a1412.gif" width="400" />
  <img src="https://user-images.githubusercontent.com/68210639/188937336-e26b6294-4c64-4718-bd0d-16962b9d7a3e.gif" width="400" /> 
</p>
