#Created on 22.03.2017 - Wednesday 13.12.2017

#****************************************************************************************
# Settings
#****************************************************************************************

DefaultProfilingFolder ="Profiling-Results/"

#****************************************************************************************
# Imports
#****************************************************************************************

#+++++++++++++++++++++++++++++++++++++++++++
# External
#+++++++++++++++++++++++++++++++++++++++++++

# System
# import sys
import os

# Profiling
import cProfile
import pstats
# Timing
from timeit import default_timer as getTime
from time import sleep as Wait

#+++++++++++++++++++++++++++++++++++++++++++
# Internal
#+++++++++++++++++++++++++++++++++++++++++++

# ProfilingPath = os.path.join(FLARE_CODE_Path,"Debugging","Profiling")

from ExecuteCommands import ExecuteCommands

def PrintCurrentThreads():

    import threading

    print("Currently running Threads:")

    for t in threading.enumerate():
        print(" "*3,t.getName())

#****************************************************************************************
# Profiler Test Functions
#****************************************************************************************

def PrintTest(msg="TestProfilingMessage"):
    print(msg)

def ProfileTestRun(ProfilingTime=10):

    t0 = getTime()
    while getTime()-t0<ProfilingTime:
        PrintTest("Profiling t-"+str(round(ProfilingTime-(getTime()-t0),2))+" s")
        Wait(0.1)

#****************************************************************************************
# Profiler
#****************************************************************************************

class Profiler():

    def __init__(self):

        self.MasterClass = None

    def Profile(self,ProfilingCommand=None,FileName="ProfilingResults.pstats",ctx=False,delay=0,AutoVisualize=True,PrintInfo=True,PrintStats=True,PrintTime=True,ShowFullGraph = False):

        #========================================================================================
        # Initialization
        #========================================================================================

        #+++++++++++++++++++++++++++++++++++++++++++
        # Check Results Folder
        #+++++++++++++++++++++++++++++++++++++++++++
        
        if (not ("/" in FileName)) and (not ("\\" in FileName)):
            if not os.path.exists(DefaultProfilingFolder):
                os.makedirs(DefaultProfilingFolder)
            FileName = DefaultProfilingFolder+FileName

        #-------------------------------------------
        # Fix Filename
        #-------------------------------------------

        ForbiddenChars = []
        ForbiddenChars.append([" ","_"]) # Remove Spaces!
        ForbiddenChars.append(["=","_"]) # Equal signs are not allowed!
        if 1: # These are guesses! (Not sure whether they cause problems...)
            ForbiddenChars.append(["#","Nr"])
            # ForbiddenChars.append(["-","_"])
            #ForbiddenChars.append([".",","])

        for ForbiddenCharPair in ForbiddenChars:
            B,G = ForbiddenCharPair
            if B in FileName:
                #if PrintInfo: print("CAUTION: '"+B+"' in FileName (not allowed) will be replaced by '"+G+"'")
                FileName = FileName.replace(B,G) 

        if " " in FileName:
            print("WARNING: The profiling Filename contains spaces! '"+str(FileName)+"' causes issues when calling cmd commands!")

        #+++++++++++++++++++++++++++++++++++++++++++
        # Default TestRun
        #+++++++++++++++++++++++++++++++++++++++++++
        
        if ProfilingCommand==None:
            DefaultProfilingTime = 10
            ProfilingCommand = "ProfileTestRun("+str(DefaultProfilingTime)+")"

        #+++++++++++++++++++++++++++++++++++++++++++
        # MasterClass
        #+++++++++++++++++++++++++++++++++++++++++++

        if self.MasterClass!=None and type(ProfilingCommand)==str:
            ProfilingCommand = ProfilingCommand.replace("self.","self.MasterClass.")

        #========================================================================================
        # Start Profiling
        #========================================================================================

        if PrintInfo:
            print("="*50)
            print(">>>!!!Starting Profiling!!!<<<")
            ProfCMD = str(ProfilingCommand)
            if len(ProfCMD)<100:
                print(">>>'"+ProfCMD+"'<<<")
            else:
                print(">>>'"+ProfCMD[:100]+"[...]"+"'<<<")
            print("="*50)

        t0 = getTime()

        if type(ProfilingCommand)==str:
            if ctx:
                Result = cProfile.runctx(ProfilingCommand,globals(),locals(),FileName)
            else:
                Result = cProfile.run(ProfilingCommand,FileName)
        else:
            Result = self.Profile_Function(ProfilingCommand,FileName)

        t_Profiling = getTime()-t0

        if PrintInfo:
            print("="*50)
            print(">>>!!!Profiling Finished (in "+str(round(t_Profiling,1))+"s"+")!!!<<<")
            print(">>>Writing Results to: "+FileName)
            print("="*50)
        elif PrintTime:
            print(">>>!!!Profiling of '"+str(ProfilingCommand)+"' Finished (in "+str(round(t_Profiling,1))+"s"+")!!!<<<")

        #--- Delay ---
        if delay>0:
            Wait(delay)

        #========================================================================================
        # Print Stats
        #========================================================================================
        
        if PrintStats:
            if 1:#Threaded:
                PrintCurrentThreads()
            if 0:
                raw_input("View Profiling Results?")

            self.PrintStats(FileName)

        #+++++++++++++++++++++++++++++++++++++++++++
        # Visualize
        #+++++++++++++++++++++++++++++++++++++++++++
        
        if AutoVisualize: #and os.name!="nt":
            self.Visualize(FileName,ShowFullGraph=ShowFullGraph)

        # print("ProfilingResult:",Result)
        return Result

    def Profile_Function(self,Function,FileName):

        pr = cProfile.Profile()
        pr.enable()
        Result = Function() # ... do something ...
        pr.disable()

        pr.dump_stats(FileName)

        return Result

    def Profile_ctx(self,ProfilingCommand=None,FileName="ProfilingResults.pstats"):
        self.Profile(ProfilingCommand=ProfilingCommand,FileName=FileName,ctx=True)

    def PrintStats(self,FileName):

        p = pstats.Stats(FileName)
        p = p.strip_dirs()

        if 0:#1:
            print("="*50)
            print(">>>PROFILING RESULTS: SORTED BY 'NAME'<<<")
            print("="*50)
            p.sort_stats('name')
            p.print_stats()
            print("")

        if 1:
            print("="*50)
            print(">>>PROFILING RESULTS: SORTED BY 'TOTAL TIME'<<<")
            print("="*50)
            p.sort_stats('time')
            p.print_stats()
            print("")

        try:
            from kivy.utils import platform
        except:
            platform = None

        if platform != 'android':
            print("="*50)
            print(">>>PROFILING RESULTS: SORTED BY 'CUMULATIVE TIME'<<<")
            print("="*50)
            p.sort_stats('cumtime')
            p.print_stats()
            print("")

    def SetMasterClass(self,MasterClass):

        self.MasterClass = MasterClass

    def Visualize(self,pstatsFile,OutputFile=None,ImageFormat=".png",ShowFullGraph = False):

        #+++++++++++++++++++++++++++++++++++++++++++
        # Settings
        #+++++++++++++++++++++++++++++++++++++++++++
        
        PrintOutput = True

        #+++++++++++++++++++++++++++++++++++++++++++
        # Set FileNames
        #+++++++++++++++++++++++++++++++++++++++++++
        
        if OutputFile==None:
            if ".pstats" in pstatsFile:
                OutputFile = pstatsFile.replace(".pstats",ImageFormat)
            else:
                OutputFile = pstatsFile+ImageFormat

        # OutputFile = OutputFile.replace(" ","_") # Remove Spaces!

        dotFile = OutputFile.replace(ImageFormat,".dot")

        #+++++++++++++++++++++++++++++++++++++++++++
        # Set Comamnds
        #+++++++++++++++++++++++++++++++++++++++++++
    
        if ShowFullGraph:
            Additional_gprof2dot_options = "-n0 -e0"
        else:
            Additional_gprof2dot_options = ""

        gprof2dot_Commands = [\
        "gprof2dot "+pstatsFile+" -f pstats "+Additional_gprof2dot_options+" > "+dotFile,\
        "dot "+dotFile+" -T"+ImageFormat.replace(".","")+" -o "+OutputFile\
        ]

        #+++++++++++++++++++++++++++++++++++++++++++
        # Execute Commands
        #+++++++++++++++++++++++++++++++++++++++++++
        
        if 0:
            ExecuteCommands(gprof2dot_Commands,sudo=True,PrintCmd=PrintOutput,PrintOutput=PrintOutput)
        else:
            for Cmd in gprof2dot_Commands:
                if PrintOutput:
                    print("Executing cmd: "+Cmd)
                os.system(Cmd)

Profiler = Profiler()

#****************************************************************************************
# Test Code
#****************************************************************************************

if __name__=="__main__":

    Profiler.Profile()

    
