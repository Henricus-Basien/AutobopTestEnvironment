# -*- coding: utf-8 -*-

'''
Created on Friday 09.03.2018
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

from visual import *
import numpy as np

from time import time as getTime

from copy import copy

def absVector(V):

    return np.linalg.norm(V)

#****************************************************************************************
# Drone
#****************************************************************************************

class Drone(sphere):

    def __init__(self,MaxVelocity=2,*args,**kwargs):


        super(Drone,self).__init__(*args,**kwargs)

        self.vel = np.zeros(3).astype(float)
        self.MaxVelocity = float(MaxVelocity)
        startAngle = np.random.random(1)*np.pi*2
        self.vel[0] = MaxVelocity*np.sin(startAngle)
        self.vel[1] = MaxVelocity*np.cos(startAngle)

        self.velArrow     = arrow(pos=self.pos,axis=self.vel,color=[0,0,1],opacity=0.5)
        self.vel_refArrow = arrow(pos=self.pos,axis=self.vel,color=[0,0,0.8],opacity=0.5)

    def Update(self,dt,Obstacles,RoomSize): 

        vel_ref = copy(self.vel)

        #-------------------------------------------
        # Evade Obstacles
        #-------------------------------------------

        if 1:
            for obstacle in Obstacles:
                difpos = np.array(obstacle.pos-self.pos).astype(float)
                # vel_ref+=np.cross(self.vel,difpos)*0.01

                if 0:#1:
                    corVel = difpos/absVector(difpos)
                    corVel*= absVector(difpos) * 0.5#(1./absVector(difpos))**2 * 10#2#0.5#0.2
                else:
                    corVel = np.cross(difpos,np.identity(3)[2])
                    # corVel*= 1./absVector(corVel)
                    corVel*= (1./absVector(corVel))**2 * 2
                    # corVel*=-1

                vel_ref-= corVel

                print absVector(corVel),corVel

        #-------------------------------------------
        # Evade Walls
        #-------------------------------------------
        
        if 1:
            for i in range(2):
                for sign in [1,-1]:
                    pos_dif = sign*RoomSize/2-self.pos[i]
                    if abs(pos_dif)<0.5:
                        vel_ref[i]-=(1./(pos_dif*2))**2 * 0.02*sign

        vel_ref[2] = 0 # No Vertical Motion!

        #--- Normalize Velocity ---
        refSpeed = absVector(vel_ref)
        if refSpeed>self.MaxVelocity:
            vel_ref*=self.MaxVelocity/refSpeed

        print absVector(vel_ref),vel_ref

        #+++++++++++++++++++++++++++++++++++++++++++
        # Update Kinematics
        #+++++++++++++++++++++++++++++++++++++++++++
        
        vel_dif = vel_ref-self.vel
        self.vel+=vel_dif*0.1

        self.pos+=dt*self.vel

        #+++++++++++++++++++++++++++++++++++++++++++
        # Update Visuals
        #+++++++++++++++++++++++++++++++++++++++++++
        
        self.velArrow.pos  = self.pos
        self.velArrow.axis = self.vel

        self.vel_refArrow.pos  = self.pos
        self.vel_refArrow.axis = vel_ref

#****************************************************************************************
# Obstacle
#****************************************************************************************

class Obstacle(cylinder):

    def __init__(self,*args,**kwargs):

        super(Obstacle,self).__init__(*args,**kwargs)

#****************************************************************************************
# Test Code
#****************************************************************************************

if __name__=="__main__":
    
    #+++++++++++++++++++++++++++++++++++++++++++
    # Settings
    #+++++++++++++++++++++++++++++++++++++++++++
    
    RoomSize    = 5 # [m]
    NrObstacles = 5#10#5 # [-]

    MaxVelocity = 1.0#0.5#2 # [m/s]
    ObstacleDiameter = 0.3 # [m]

    RoomSize = float(RoomSize)

    #+++++++++++++++++++++++++++++++++++++++++++
    # Initialization
    #+++++++++++++++++++++++++++++++++++++++++++
    
    Window = display(title="Obstacle Avoidance Test",width=3200,height=1800)

    Window.up = np.identity(3)[2]
    Window.forward = -np.ones(3)
    Window.range = RoomSize*1.5

    for i in range(3):
        arrow(axis=np.identity(3)[i],color=np.identity(3)[i],opacity=0.5)

    Window.stereo = "crosseyed"

    #+++++++++++++++++++++++++++++++++++++++++++
    # Create World
    #+++++++++++++++++++++++++++++++++++++++++++
    
    Floor = box(axis=np.identity(3)[2],width=RoomSize,height=RoomSize,length=0.1,color=[1]*3,opacity=0.8)

    #-------------------------------------------
    # Add Obstacle
    #-------------------------------------------
    
    Obstacles = []

    for i in range(NrObstacles):

        ObstaclePos = (np.random.random(3)*RoomSize  * 0.8 )-RoomSize/2
        ObstaclePos[2] = 0
   
        obstacle = Obstacle(pos=ObstaclePos,radius=ObstacleDiameter/2,length=RoomSize,axis=np.identity(3)[2],color=[1,0.5,0],opacity=0.8)
        Obstacles.append(obstacle)

    #-------------------------------------------
    # Init Drone
    #-------------------------------------------
    
    DronePos = [0,0,RoomSize/2]
    drone = Drone(MaxVelocity=MaxVelocity,pos=DronePos,radius=0.15,color=[1,0,0])

    #+++++++++++++++++++++++++++++++++++++++++++
    # Update Loop
    #+++++++++++++++++++++++++++++++++++++++++++
  
    t0 = getTime()
    t  = getTime()

    while True:
        
        #-------------------------------------------
        # Keep Time
        #-------------------------------------------

        dt = getTime()-t
        t = getTime()
        T = t-t0
        if dt!=0:
            freq = 1./dt
        else:
            freq = 0

        print "T: "+str(round(T,2))+"s"+" - "+str(round(freq,1))+" Hz"

        #-------------------------------------------
        # Update
        #-------------------------------------------

        drone.Update(dt,Obstacles,RoomSize)

        #--- Visualize ---

        rate(60)