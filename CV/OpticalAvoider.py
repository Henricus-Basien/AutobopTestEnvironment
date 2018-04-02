# -*- coding: utf-8 -*-

'''
Created on Friday 13.03.2018
Copyright Henricus N. Basien
Author: Henricus N. Basien
Email: Henricus@Basien.de
'''

#****************************************************************************************
# Imports
#****************************************************************************************

#+++++++++++++++++++++++++++++++++++++++++++
# External
#+++++++++++++++++++++++++++++++++++++++++++

import os,sys,traceback

import time
from time import time as getTime

from functools import partial

from copy import copy

from collections import OrderedDict

#-------------------------------------------
# Mathematics
#-------------------------------------------

import numpy as np

#-------------------------------------------
# Computer Vision
#-------------------------------------------

import cv2

#+++++++++++++++++++++++++++++++++++++++++++
# Internal
#+++++++++++++++++++++++++++++++++++++++++++

from OpticalFlowAnalyzer import OpticalFlowAnalyzer,GradientColor

#****************************************************************************************
# Optical Avoider
#****************************************************************************************

class OpticalAvoider():

    def __init__(self):

        print "Building Analyzer"

        #--- Settings ---
        self.InitializeSettings()
        #--- Optical Flow ---
        self.OpticalFlowAnalyzer = OpticalFlowAnalyzer()

    def InitializeSettings(self):

        self.InitializeBooleanSettings()
        self.InitializeVariableSettings()

    def InitializeBooleanSettings(self):
        self.BooleanSettings = OrderedDict()
        self.BooleanSettings["Resize"]   = True
        self.BooleanSettings["Contrast"] = True#False

        self.BooleanSettings["DeRotateFlow"] = False

        self.BooleanSettings["ShowOpticalFlow"] = False
        self.BooleanSettings["ShowDifMap"]    = True
        self.BooleanSettings["ShowDirData"]   = True
        self.BooleanSettings["ShowDirection"] = True

        self.BooleanSettings["TrackMax"] = False

    def InitializeVariableSettings(self):

        self.VariableSettings = OrderedDict()

        #--- Variable Settings                [Value,Min,Max] ---
        self.VariableSettings["K"]          = [2.0  ,0.0 ,4.0]

        Width = 200 # Resolution
        Angle = 60  # deg
        DF = float(Width)/Angle

        self.VariableSettings["Derotation"] = [DF  ,0.0 ,10.0]

    #========================================================================================
    # Analyze Frame
    #========================================================================================

    def AnalyzeFrame(self,frame,dt,rps=None):

        #print "Frame Size",frame.shape

        self.dt = dt
        self.rps = rps

        #+++++++++++++++++++++++++++++++++++++++++++
        # Prepare Image
        #+++++++++++++++++++++++++++++++++++++++++++
        
        if self.BooleanSettings["Resize"]:
            frame = self.ResizeFrame(frame)

        if self.BooleanSettings["Contrast"]!=False:
            frame = self.EnhanceContrast(frame,self.BooleanSettings["Contrast"])

        #+++++++++++++++++++++++++++++++++++++++++++
        # Analyze Optical Flow
        #+++++++++++++++++++++++++++++++++++++++++++
    
        self.OpticalFlowAnalyzer.DerotationScale = self.VariableSettings["Derotation"][0]

        self.AnalyzeFlow(frame)

        #-------------------------------------------
        # Get Flow Data
        #-------------------------------------------

        if hasattr(self.OpticalFlowAnalyzer,"flow"):

            #-------------------------------------------
            # Get Outliers
            #-------------------------------------------
        
            if 1:
                frame = self.ShowOutliers(frame)

        return frame

    def ResizeFrame(self,frame):
        res_new = [200,150]#(150,200) #(240*2,320 *2)#(320,240)#(120,160)#(160,120) # (320,240)

        if frame.shape[0]>frame.shape[1]:
            res_new = res_new[::-1]

        res_new = tuple(res_new)

        #print frame.shape
        frame = cv2.resize(frame, res_new)#(100, 50)) 
        #print "After",frame.shape
        return frame

    def EnhanceContrast(self,frame,contrast):

        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3., tileGridSize=(8,8))

        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)  # convert from BGR to LAB color space
        l, a, b = cv2.split(lab)  # split on 3 different channels

        l2 = clahe.apply(l)  # apply CLAHE to the L-channel

        lab = cv2.merge((l2,a,b))  # merge channels
        frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)  # convert from LAB to BGR

        return frame

    #========================================================================================
    # Flow Data
    #========================================================================================
    
    def AnalyzeFlow(self,frame):
        if hasattr(self,"frame_old"):
            frame_new = frame
            Mode = 3#2
            #FlowManipulationFunction = self.FlowManipulationFunction
            if self.BooleanSettings["DeRotateFlow"]!=False:
                FlowManipulationFunction = partial(self.OpticalFlowAnalyzer.SubstractRotation,rps=self.rps)
            else:
                FlowManipulationFunction = None
            ShowResult = self.BooleanSettings["ShowOpticalFlow"]
            frame = self.OpticalFlowAnalyzer.ShowOpticalFlow1(frame_new,self.frame_old,Mode=Mode,InvertColor=False,FlowManipulationFunction=FlowManipulationFunction,ShowResult=ShowResult)
            self.frame_old = copy(frame_new)
        else:
            self.frame_old = copy(frame)

    def ShowOutliers(self,frame):

        if self.BooleanSettings["DeRotateFlow"]:
            flow_outliers = self.OpticalFlowAnalyzer.flow_corrected
        else:
            flow_outliers = self.OpticalFlowAnalyzer.flow

        #--- Substract Mean ---
        for i in range(2):
            Mean = np.mean(flow_outliers[:,:,i])
            flow_outliers[:,:,i]-=Mean

        #--- Get Total ---
        flow_mag = np.linalg.norm(flow_outliers,axis=2)

        #--- Show Outliers ---

        if 0:#1:
            return self.ShowOutlierCircles(frame,flow_mag)
        else:
            return self.ShowProbabilityMap(frame,flow_mag)

    def ShowOutlierCircles(self,frame,flow_mag):
        step=5
        threshold = 10
        for i in range(0,flow_mag.shape[0],step):
            #if i%step!=0:
            #    continue
            for j in range(0,flow_mag.shape[1],step):
                #if j%step!=0:
                #    continue
                radius = 1
                pt = (j,i)
                
                #print "flow_mag[i,j]",flow_mag[i,j]
                if abs(flow_mag[i,j])>threshold:#1:
                    cv2.circle(frame,pt,radius,(0,120,0),-1)

        return frame

    def ShowProbabilityMap(self,frame,flow_mag):

        if self.BooleanSettings["ShowDifMap"]:

            threshold = float(20)#(10)

            frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if 0:#1:
                magnitude_map = np.zeros_like(frame)
                colors = [[0,255,0],[255,0,0]]
                for i in range(frame.shape[0]):
                    for j in range(frame.shape[1]):
                        val = abs(flow_mag[i,j])
                        magnitude_map[i,j] = GradientColor(val,colors=colors,Min=0.,Max=threshold)
            else:
                #print "Flow Mag",np.min(flow_mag),np.max(flow_mag)
                magnitude_map = np.abs(flow_mag)/threshold
                ones = np.ones_like(flow_mag)
                Max = np.minimum(magnitude_map,ones)
                #magnitude_map = np.zeros_like(frame)
                #magnitude_map[:,:,0] = (1-Max)*255 # Red
                #magnitude_map[:,:,1] =    Max *255 # Green

                magnitude_map = np.zeros_like(frame)
                #print np.min(Max),np.max(Max)
                #print Max
                R =    Max *255
                G = (1-Max)*255
                B = np.zeros_like(frame_grey)

                magnitude_map[:,:,0] = R
                magnitude_map[:,:,1] = G
                magnitude_map[:,:,2] = B

                #print R.shape,G.shape,B.shape
                #magnitude_map = np.concatenate((R,G,B), axis=2)

            frame_grey = cv2.cvtColor(frame_grey, cv2.COLOR_GRAY2BGR)
            #print frame_grey.shape,magnitude_map.shape,flow_mag.shape
            
            if 1:
                #frame = frame_grey
                #frame = (frame_grey+magnitude_map)/2.#np.einsum('mnd,mnd->mnd', frame_grey/255.,magnitude_map)#np.dot(frame_grey/255.,magnitude_map)#frame_grey/255.*magnitude_map#np.multiply(frame_grey/255.,magnitude_map)
                frame = cv2.addWeighted(frame_grey,0.5,magnitude_map,0.5,0)#frame_grey*magnitude_map/255.#np.multiply(frame_grey/255.,magnitude_map)
            else:
                frame = magnitude_map
            #frame = np.dot(frame_grey/255.,magnitude_map)#frame_grey*magnitude_map


        if self.BooleanSettings["ShowDirection"] or self.BooleanSettings["ShowDirData"]:
            frame = self.ShowOptimalDirection(frame,flow_mag)

        #scalarmap = np.ones_like(frame)
        #print "scalarmap",scalarmap.shape,frame.shape   
        #frame_grey = cv2.cvtColor(frame_grey, cv2.COLOR_GRAY2BGR)
        #frame = np.multiply(frame_grey,scalarmap)
        #print frame.shape,np.max(frame)

        return frame

    def ShowOptimalDirection(self,frame,flow_mag):

        OptimalDirection = self.FindOptimalDirection(flow_mag)

        radius = int(np.min(frame.shape[:2])*0.1/2)
        color  = [0,255,0]
        color2 = [255,255,0]
        thickness = 4#-1

        if self.BooleanSettings["ShowDirection"]:
            cv2.circle(frame,tuple(OptimalDirection),radius,color,thickness)

        if self.BooleanSettings["ShowDirData"]:

            if 1:
                line_color = [255,255,255]
                cv2.line(frame, (0,self.MinRow)   , (frame.shape[1],self.MinRow)   , line_color, thickness)
                cv2.line(frame, (self.MinColumn,0), (self.MinColumn,frame.shape[0]), [255,0,0] , thickness)

            if hasattr(self,"DifDirection"):
                pt1 = tuple(OptimalDirection)
                pt2 = tuple((OptimalDirection+self.DifDirection).astype(int))
                cv2.arrowedLine(frame, pt1, pt2, color2, int(thickness/2))
                pt3 = tuple((OptimalDirection+self.dDifDirection).astype(int))
                cv2.arrowedLine(frame, pt1, pt3, color, int(thickness/2))

                cv2.circle(frame,tuple(self.OptimalDirection),int(radius/2),color2,int(thickness/2))

        return frame

    def FindOptimalDirection(self,flow_mag,Raw=False):

        size = copy(flow_mag.shape)

        min_scale = 3 #9 # 3#9

        GridSize = np.array(size).astype(float)*min_scale/np.min(size)
        if 0:#1:
            GridSize = GridSize[::-1]
        GridSize = (GridSize).astype(int)

        #print "Image Size",size
        #print "Detection GridSize",GridSize

        DetectionGrid = cv2.resize(flow_mag,tuple(GridSize))

        if 0:#1:
            pos = np.argmin(DetectionGrid, axis=1)
        else:
            axis = 1
            columnAvg = np.mean(DetectionGrid, axis=axis)
            #columnMinima = np.argmin(DetectionGrid, axis=axis)

            #print "Nr Avg Columns:",len(columnAvg)

            if self.BooleanSettings["TrackMax"]:
                findfunc = np.argmax
            else:
                findfunc = np.argmin
            column = findfunc(columnAvg) #(columnMinima)
            row    = findfunc(DetectionGrid[column])#[:,column])
            #pos = np.array([row,column]).astype(float)
            pos = np.array([column,row]).astype(float)

            self.OptColumn = column
            self.OptRow    = row

        OptimalDirection = np.zeros(2).astype(float)
        offset = np.array([0.5,0.5])
        for i in range(2):
            j = (i+1)%2
            #print i,j
            #OptimalDirection[i] = (pos[i]+offset[i])*size[i]/GridSize[i]
            #print "OptimalDirection#1",OptimalDirection[i]
            #OptimalDirection[i] = (pos[i]+offset[i])*size[j]/GridSize[j]
            #print "OptimalDirection#2",OptimalDirection[i]
            OptimalDirection[i] = (pos[j]+offset[j])*size[j]/GridSize[i]

        self.OptimalDirection = OptimalDirection.astype(int)

        self.MinColumn = self.OptimalDirection[0]
        self.MinRow    = self.OptimalDirection[1]

        if 0:
            print "DetectionGrid"
            print DetectionGrid
            print "columnAvg",columnAvg
            #print "columnMinima",columnMinima
            print "column",column
            print "row",row
            print "OptimalDirection",self.OptimalDirection

        if Raw:
            return self.OptimalDirection
        else:

            if hasattr(self,"CurrentDirection"):

                TF = self.VariableSettings["K"][0]
                #TF = 2.0 # 10.0#1.0 # [s] # in X seconds it should converge to the new result
                K = self.dt/TF # 0.1

                if 1: # Scale by total Magnitude!
                    Mean = np.abs(np.mean(flow_mag))
                    threshold = 20
                    Scale = Mean/threshold
                    if Mean>1:
                        Mean = 1

                    K*=Mean**0.5

                self.DifDirection = OptimalDirection-self.CurrentDirection
                self.dDifDirection = self.DifDirection*K
                self.CurrentDirection += self.dDifDirection

            else:
                self.CurrentDirection = np.array(size).astype(float)/2.

            return self.CurrentDirection.astype(int)
