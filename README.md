# a-novel-visual-feature-and-gaze-driven-egocentric-video-retargeting
Official implementation of the paper "A NOVEL VISUAL FEATURE AND GAZE DRIVEN EGOCENTRIC VIDEO RETARGETING" accepted at ICIP 2022

## Overview 
Egocentric vision data has become popular due to its unique way of capturing first-person perspective. However they are lengthy, contain redundant information and visual noise caused by head movements which disrupt the story being expressed through them. This paper proposes a novel visual feature and gaze driven approach to retarget egocentric videos following the principles of cinematography. This approach is divided into two parts: activity based scene detection and performing panning and zooming to produce visually immersive videos. Firstly, visually similar frames are grouped using DCT feature matching followed by SURF descriptor matching. These groups are further refined using the gaze data to generate different scenes and transitions occurring within an activity. Secondly, the mean 2D gaze positions of scenes are used for generating panning windows enclosing $75\%$ of the frame content. This is done for performing zoom-in and zoom-out operations in the detected scenes and transitions respectively. Our approach has been tested on the GTEA and EGTEA gaze plus datasets witnessing an average accuracy of 88.1% and 72% for sub-activity identification and obtaining an average aspect ratio similarity (ARS) score of 0.967 and 0.73; 60\% and 42\% SIFT similarity index (SSI) respectively.

<p float="centre">
  <img src="https://user-images.githubusercontent.com/68210639/184404868-4d05e7e8-0917-436b-be1a-bfc7c2440d3b.gif" width="400" />
  <img src="https://user-images.githubusercontent.com/68210639/184405440-8d9fd2c8-cb2d-4491-8d87-d60030252d15.gif" width="400" /> 
</p>
