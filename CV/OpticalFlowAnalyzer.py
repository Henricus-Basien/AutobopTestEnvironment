# -*- coding: utf-8 -*-

'''
Created on Wednesday 07.03.2018
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

from copy import copy

#--- Mathematics ---
import numpy as np

#--- Computer Vision ---
import cv2

#+++++++++++++++++++++++++++++++++++++++++++
# Internal
#+++++++++++++++++++++++++++++++++++++++++++

#--- Console Output ---
try:
    from TTY import PrintWarning
except:
    def PrintWarning(Text):
        print("WARNING: "+Text)

#--- Visualization ---
try:
    from Colors import Colors,GradientColor
except:
    Colors = dict()
    Colors["White"] = [255,255,255]
    Colors["Black"] = [0  ,0  ,0  ]
    Colors["Red"]   = [255,0  ,0  ]
    Colors["Green"] = [0  ,255,0  ]
    Colors["Blue"]  = [0  ,0  ,255]

    for key in Colors:
        Colors[key] = np.array(Colors[key]).astype(float)/255.

    def GradientColor(Value,colors=[Colors["White"],Colors["Black"]],Min=0.,Max=1.):
        """
        Simplified Version of the GradientColor Function!
        """

        Value=float(Value);Min=float(Min);Max=float(Max);colors = np.array(colors).astype(float)

        per = (Value-Min)/(Max-Min)
        if per<=0:
            return colors[0]
        elif per>=1:
            return colors[-1]

        color = colors[0]+(colors[1]-colors[0])*per
        return color

#****************************************************************************************
# Optical Flow Analyzer
#****************************************************************************************

OpenCV_Version = int(cv2.__version__[0])
#print "OpenCV_Version",OpenCV_Version

class OpticalFlowAnalyzer():

    def __init__(self):

        #-------------------------------------------
        # Optical Flow  #2
        #-------------------------------------------

        # params for ShiTomasi corner detection
        self.feature_params = dict( maxCorners = 100,
                               qualityLevel = 0.3,
                               minDistance = 7,
                               blockSize = 7 )
        # Parameters for lucas kanade optical flow
        self.lk_params = dict( winSize  = (15,15),
                          maxLevel = 2,
                          criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        # Create some random colors
        self.colors = np.random.randint(0,255,(100,3))


        self.DerotationScale = 1.0

    #+++++++++++++++++++++++++++++++++++++++++++
    # Optical Flow #1
    #+++++++++++++++++++++++++++++++++++++++++++
    
    def GetOpticalFlow1(self,frame_new,frame_old,Raw=False,FlowManipulationFunction=None):

        #+++++++++++++++++++++++++++++++++++++++++++
        # Settings
        #+++++++++++++++++++++++++++++++++++++++++++
        
        if 0:#hasattr(self,"flow"):
            flow_init = self.flow
            flags = cv2.OPTFLOW_USE_INITIAL_FLOW#0
        else:
            flow_init = None
            flags     = 0

        if 1:#0:
            pyr_scale  = 0.5
            levels     = 3
            winsize    = 15
            iterations = 3
            poly_n     = 5
            poly_sigma = 1.2
        else:
            pyr_scale  = 0.5
            levels     = 2
            winsize    = 15
            iterations = 2
            poly_n     = 5
            poly_sigma = 1.2

        #+++++++++++++++++++++++++++++++++++++++++++

        #--- Get Flow ---
        if OpenCV_Version>=3:
            flow = cv2.calcOpticalFlowFarneback(frame_old,frame_new,flow_init,pyr_scale,levels,winsize,iterations,poly_n,poly_sigma,flags)
        else:
            flow = cv2.calcOpticalFlowFarneback(frame_old,frame_new,pyr_scale,levels,winsize,iterations,poly_n,poly_sigma,flags,flow_init) #0.5,3,15,3,5,1.2,0)
            #flow*=10**6

        self.flow = copy(flow)

        if FlowManipulationFunction is not None:
            flow = FlowManipulationFunction(flow)

        if Raw:
            return flow
        else:
            return self.GetMagAng(flow)

    def GetMagAng(self,flow):
        mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
        return mag, ang

    def PreprocessFrames(self,frame_new,frame_old):

        #--- Change Size ---
        if 0:#1:
            res_new = (320/4,240/4)#(320/2,240/2)#(240,320)
            frame_new = cv2.resize(frame_new, res_new)
            frame_old = cv2.resize(frame_old, res_new)

        if not np.all(frame_new.shape==frame_old.shape): #frame_new.shape is not frame_old.shape:
            #print "Sizeing Mismatch detected!",frame_old.shape,frame_new.shape
            frame_old = cv2.resize(frame_old,frame_new.shape[:2][::-1])
            #print "Sizeing Mismatch detected and Corrected!",frame_old.shape,frame_new.shape

        #--- Convert Colorspace ---
        frame_new_g = cv2.cvtColor(frame_new,cv2.COLOR_BGR2GRAY)
        frame_old_g = cv2.cvtColor(frame_old,cv2.COLOR_BGR2GRAY)

        return frame_new_g,frame_old_g

    def SubstractRotation(self,flow,rps=np.zeros(3),Invert=True):

        for i in range(2):
            #--- Dir ---
            Dir = i
            if Invert:
                Dir = (Dir+1)%2
            #--- Sign ---
            Sign = -1#1
            if Dir==1:
                Sign*=-1
            #--- Augment Flow ---
            Scale = self.DerotationScale # Should be function of viewangle and image resolution!!!
            flow[:,:,Dir]+=int(rps[i]*Scale*Sign)
        #flow-=20
        #ang+=90

        self.flow_corrected = copy(flow)

        return flow

    def ShowOpticalFlow1(self,frame_new,frame_old,Mode=1,InvertColor=True,FlowManipulationFunction=None,ShowResult=True):

        #from functools import partial
        #FlowManipulationFunction = partial(self.SubstractRotation,rps=[10,10,10])

        #--- Preprocess Frames ---
        frame_new_g,frame_old_g = self.PreprocessFrames(frame_new,frame_old)

        #--- Get Flow ---
        mag,ang = self.GetOpticalFlow1(frame_new_g,frame_old_g,FlowManipulationFunction=FlowManipulationFunction)

        #--- Display as HSV ---
        if ShowResult:
            if Mode==1:
                frame = self.DrawHSV_Flowmap(frame_old,mag,ang)
            else:
                if Mode==2:
                    Color = None
                else:
                    Color = "Mag"
                frame = self.DrawArrows(frame_new,frame_new_g.shape,mag,ang,Color=Color,InvertColor=InvertColor)

            return frame
        else:
            return frame_new

    def DrawHSV_Flowmap(frame,mag,ang):

        hsv = np.zeros_like(frame)
        hsv[...,0] = ang*180/np.pi/2
        hsv[...,1] = 255
        hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
        bgr = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)

        return bgr
        #frame = bgr

    def DrawArrows(self,frame,res,mag,ang,Color=None,thickness = 1,InvertColor=True):#4):# BGR!

        #-------------------------------------------
        # Skip (make grid)
        #-------------------------------------------
        
        MinNrArrows = 10
        Skip = int(min(res)/MinNrArrows)#0.05)#50#10#None

        #--- Ensure Centered Grid ---
        x_offset = int((res[1]%Skip)/2)#int(((res[1]-Skip/2)%Skip))#/2)
        y_offset = int((res[0]%Skip)/2)#int(((res[0]-Skip/2)%Skip))#/2)

        if x_offset==0:
            x_offset = Skip/2
        if y_offset==0:
            y_offset = Skip/2

        # print Skip,x_offset,y_offset

        #-------------------------------------------
        # Get Arrows
        #-------------------------------------------
        
        if Color is None:
            color = (255,0,0)
        else:
            color = Color
        
        arrows_x = (mag * np.sin(ang)).astype(int) 
        arrows_y = (mag * np.cos(ang)).astype(int) 

        for y in range(res[0]):
            if Skip is not None and (y-y_offset)%Skip!=0:
                continue    
            for x in range(res[1]):
                if Skip is not None and (x-x_offset)%Skip!=0:
                    continue
                # print x,y
                pt1 = np.array([x,y]).astype(int)

                if 1:
                    dpt = np.array([arrows_y[y,x],arrows_x[y,x]])
                else:
                    M = mag[y,x]
                    A = ang[y,x]
                    dpt = (M*np.array([np.sin(A),np.cos(A)])).astype(int) 
                
                pt2 = pt1 + dpt
                # print dpt,pt2
                if Color=="Mag":
                    Val = mag[y,x]
                    Max = np.max(mag)
                    color = GradientColor(Val,colors=[Colors["Green"],Colors["Red"]],Min=0.,Max=Max)
                    color = (np.array(color)*255).astype(int)
                    if InvertColor:
                        color = color[::-1]
                    color = tuple(color)
                    # print color,Val,Max

                #--- Check Arrow ---

                pt1 = tuple(np.array(pt1).astype(int))
                pt2 = tuple(np.array(pt2).astype(int))

                ArrowsValid = True
                for pt in [pt1,pt2]:
                    for i in range(2):
                        if 0>pt[i]or pt[i]>frame.shape[(i+1)%2]:
                            ArrowsValid = False
                            break
                    if not ArrowsValid:
                        break

                if ArrowsValid:
                    #print "Points '"+str(pt1)+"' & '"+str(pt2)+"' are valid!"
                    if 1:#OpenCV_Version>=3:
                        cv2.arrowedLine(frame, pt1, pt2, color, thickness)
                    else:
                        cv2.line(frame, pt1, pt2, color, thickness)
                else:
                    color = (255,0,0)#(0,0,255)
                    cv2.circle(frame,pt1, thickness, color, -1)
                    #print "Points '"+str(pt1)+"' & '"+str(pt2)+"' are invalid!"
                    pass
                #print "Drawing Arrow",pt1,pt2
                # print frame
        # print frame
        # print frame.shape
        if 0: cv2.imshow("Optical Flow",frame)

        return frame

    #+++++++++++++++++++++++++++++++++++++++++++
    # Optical Flow #2
    #+++++++++++++++++++++++++++++++++++++++++++
    
    def ShowOpticalFlow2(self,frame_new,frame_old):
        
        #-------------------------------------------
        # Initialization
        #-------------------------------------------
        
        if not hasattr(self,"old_gray"):
            self.old_gray = cv2.cvtColor(frame_old, cv2.COLOR_BGR2GRAY)
            self.p0 = cv2.goodFeaturesToTrack(self.old_gray, mask = None, **self.feature_params)

        # Create a mask image for drawing purposes
        if not hasattr(self,"mask"):
            self.mask = np.zeros_like(frame_old)

        #-------------------------------------------
        # Run Optical Flow
        #-------------------------------------------
        
        frame_gray = cv2.cvtColor(frame_new, cv2.COLOR_BGR2GRAY)
        # calculate optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray, self.p0, None, **self.lk_params)
        # Select good points
        if p1 is not None:
            good_new = p1[st==1]
        else:
            PrintWarning("Optical Flow 2 ...No Points found!")
            return frame_new
        good_old = self.p0[st==1]
        # draw the tracks
        for i,(new,old) in enumerate(zip(good_new,good_old)):
            a,b = new.ravel()
            c,d = old.ravel()
            self.mask = cv2.line(self.mask, (a,b),(c,d), self.colors[i].tolist(), 2)
            frame_new = cv2.circle(frame_new,(a,b),5,self.colors[i].tolist(),-1)
        img = cv2.add(frame_new,self.mask)

        # Now update the previous frame and previous points
        self.old_gray = frame_gray.copy()
        self.p0 = good_new.reshape(-1,1,2)

        return img

#****************************************************************************************
# Test Code
#****************************************************************************************

if __name__=="__main__":
    
    from time import sleep as Wait
    from time import time as getTime

    #+++++++++++++++++++++++++++++++++++++++++++
    # Settings
    #+++++++++++++++++++++++++++++++++++++++++++
    
    Title = "Optical Flow Test"

    #-------------------------------------------
    # Source
    #-------------------------------------------
    
    if 1:
        Source = "CyberZoo_TestVideo.mp4"
    else:
        #--- Camera Settings ---
        Source = 0 # Camera #0
        Resolution = [1280,720]
        
    Max_FPS = 60

    Title+=" - Source: "+str(Source)

    #-------------------------------------------
    # Analyzer Mode
    #-------------------------------------------
    
    Analyzer = 1
    Mode = 3

    #+++++++++++++++++++++++++++++++++++++++++++
    # Initialization
    #+++++++++++++++++++++++++++++++++++++++++++
    
    OFA = OpticalFlowAnalyzer()

    Camera = cv2.VideoCapture(Source)
    try:
        CameraNr = int(Source)
        Camera.set(3,Resolution[0])
        Camera.set(4,Resolution[1])
        Wait(1.0) # Needed for Camera Initialization
    except:
        pass # VideoFile is used!

    ret,frame_old = Camera.read()

    #+++++++++++++++++++++++++++++++++++++++++++
    # Run Analysis
    #+++++++++++++++++++++++++++++++++++++++++++
    
    print Title

    t0 = getTime()
    t  = getTime()
    FrameCounter = 0
    while True:
        #-------------------------------------------
        # Counter & Time Keeping
        #-------------------------------------------
        
        FrameCounter+=1
        dt = getTime()-t
        t  = getTime()
        T = t-t0
        if dt!=0:
            freq = 1./dt
        else:
            freq = 0
        print("T="+str(round(T,1))+" s \t @"+str(round(freq,2))+" Hz \t Analyzing Frame #"+str(FrameCounter))

        #-------------------------------------------
        # Read Image
        #-------------------------------------------
        
        ret,frame_new = Camera.read()

        #print frame_new,type(frame_new),frame_new.shape

        #--- Check End of File ---
        if frame_new is None:
            print("Reached End of File!")
            break

        #-------------------------------------------
        # Analyze Image
        #-------------------------------------------
        
        if Analyzer==1:
            frame_analysis = OFA.ShowOpticalFlow1(frame_new,frame_old,Mode)
        elif Analyzer==2:
            frame_analysis = OFA.ShowOpticalFlow1(frame_new,frame_old)
        else:
            PrintWarning("Analyzer '"+str(Analyzer)+"' unknown!")
            break

        #--- Store Old Frame ---
        frame_old = frame_new

        #-------------------------------------------
        # Show Image
        #-------------------------------------------
        
        cv2.imshow(Title,frame_analysis)

        #-------------------------------------------
        # WaitKey & Break on ESC
        #-------------------------------------------
        
        k = cv2.waitKey(1000/Max_FPS)#(33)
        if k==27:    # Esc key to stop
            print("ESC pressed, Test will be Terminated!")
            break

    #+++++++++++++++++++++++++++++++++++++++++++
    # Cleanup
    #+++++++++++++++++++++++++++++++++++++++++++

    Camera.release()
    cv2.destroyAllWindows()
