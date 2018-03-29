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

        #--- Optical Flow ---
        self.OpticalFlowAnalyzer = OpticalFlowAnalyzer()

    #========================================================================================
    # Analyze Frame
    #========================================================================================

    def AnalyzeFrame(self,frame,dt,rps=None):

        self.dt = dt
        self.rps = rps

        #+++++++++++++++++++++++++++++++++++++++++++
        # Calculate Optical Flow
        #+++++++++++++++++++++++++++++++++++++++++++
        
        if 1:
            frame = self.ResizeFrame(frame)

        if hasattr(self,"OpticalFlowAnalyzer"):
            #analysis_frame = copy(frame)
            self.AnalyzeFlow(frame)#(analysis_frame)

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
        res_new = (150,200) #(240*2,320 *2)#(320,240)#(120,160)#(160,120) # (320,240)
        #print frame.shape
        frame = cv2.resize(frame, res_new)#(100, 50)) 
        #print "After",frame.shape
        return frame

    #========================================================================================
    # Flow Data
    #========================================================================================
    
    def AnalyzeFlow(self,frame):
        if hasattr(self,"frame_old"):
            frame_new = frame
            Mode = 3#2
            #FlowManipulationFunction = self.FlowManipulationFunction
            FlowManipulationFunction = partial(self.OpticalFlowAnalyzer.SubstractRotation,rps=self.rps)
            ShowResult = False#True
            frame = self.OpticalFlowAnalyzer.ShowOpticalFlow1(frame_new,self.frame_old,Mode=Mode,InvertColor=False,FlowManipulationFunction=FlowManipulationFunction,ShowResult=ShowResult)
            self.frame_old = frame_new
        else:
            self.frame_old = frame

    def ShowOutliers(self,frame):
        flow_outliers = self.OpticalFlowAnalyzer.flow_corrected

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

        threshold = float(20)#(10)

        frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if 1:#0:#1:
            
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


        if 1:
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
        cv2.circle(frame,tuple(OptimalDirection),radius,color,thickness)

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

        min_scale = 9 # 3#9

        GridSize = (np.array(size).astype(float)*min_scale/np.min(size)).astype(int)
        #print "Detection GridSize",GridSize

        DetectionGrid = cv2.resize(flow_mag,tuple(GridSize))


        if 0:#1:
            pos = np.argmin(DetectionGrid, axis=1)
        else:
            columnAvg = np.mean(DetectionGrid, axis=1)
            #columnMinima = np.argmin(DetectionGrid, axis=0)
            column = np.argmin(columnAvg) #(columnMinima)
            row    = np.argmin(DetectionGrid[column])#[:,column])
            pos = np.array([column,row]).astype(float)

            if 0:
                print "DetectionGrid"
                print DetectionGrid
                print "columnAvg",columnAvg
                #print "columnMinima",columnMinima
                print "column",column
                print "row",row

        OptimalDirection = np.zeros(2)
        for i in range(2):
            OptimalDirection[i] = pos[i]*size[i]/GridSize[i]

        self.OptimalDirection = OptimalDirection.astype(int)

        self.MinColumn = self.OptimalDirection[0]
        self.MinRow    = self.OptimalDirection[1]

        if Raw:
            return self.OptimalDirection
        else:

            if hasattr(self,"CurrentDirection"):

                TF = 2.0 # 10.0#1.0 # [s] # in X seconds it should converge to the new result
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
