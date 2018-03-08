Paparazzi_Header='
__________                                                 .__ 
\______   \_____  ___________ ____________  _______________|__|
 |     ___/\__  \ \____ \__  \\\\_  __ \__  \ \___   /\___   /  |
 |    |     / __ \|  |_> > __ \|  | \// __ \_/    /  /    /|  |
 |____|    (____  /   __(____  /__|  (____  /_____ \/_____ \__|
                \/|__|       \/           \/      \/      \/   
.___                 __         .__  .__                       
|   | ____   _______/  |______  |  | |  |   ___________        
|   |/    \ /  ___/\   __\__  \ |  | |  | _/ __ \_  __ \       
|   |   |  \\\\___ \  |  |  / __ \|  |_|  |_\  ___/|  | \/       
|___|___|  /____  > |__| (____  /____/____/\___  >__|          
         \/     \/            \/               \/              
'
printf "${Paparazzi_Header}"

printf "Created on 23.02.2018 by Henricus N. Basien (Henricus@Basien.de)"

#=================================================================================
# Settings
#=================================================================================

RootDir="~"
PaparazziDir="$RootDir/paparazzi"

RunPaparazziCmd="./paparazzi"

#Python="sudo python"
Python="python"

#=================================================================================
# Initialization
#=================================================================================

DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
. "$DIR/Installer_Init.sh"

#=================================================================================
PrintHeader "Installation"
#=================================================================================

echo "Please fill in your sudo Password to install Paparazzi: "
sudo echo "Thank you!"

#--------------------------------------------------------------
PrintSubHeader "Installing Required Programs"
#--------------------------------------------------------------

Run "$aptInstall_Y ffmpeg vlc cmake default-jre" 

#--------------------------------------------------------------
PrintSubHeader "Installing Joystick Support"
#--------------------------------------------------------------

Run "$aptInstall_Y jstest-gtk xboxdrv"

## --- Anaconda Fixes ---
#https://askubuntu.com/questions/701246/libpng16-so-16-not-found-how-to-get-it <--------------- This worked!!!

#!!!!! IGNORE THESE !!!!!
#libpng-dev,libcairo2-dev
#Run "$aptInstall_Y --reinstall python-gtk2-dev libpangocairo-1.0-0" # Problems after installing Anaconda!
#Run "conda install -c https://conda.anaconda.org/pmuller cairo"

#Run "$pipInstall pygtk"
#Run "conda install -c ska pygtk -y"	
#!!!!!!!!!!!!!!!!!!!!!!!!

#--------------------------------------------------------------
PrintSubHeader "Installing Paparazzi"
#--------------------------------------------------------------

ConfirmQ="Do you want to (re-)install Paparazzi [Y/n]?"
result=$(Confirm "$ConfirmQ")
if $result; then
	#Run "sudo add-apt-repository -y ppa:paparazzi-uav/ppa && sudo add-apt-repository -y ppa:team-gcc-arm-embedded/ppa && sudo apt-get update && \
	#sudo apt-get -f -y install paparazzi-dev paparazzi-jsbsim gcc-arm-embedded && cd ~ && git clone --origin upstream https://github.com/paparazzi/paparazzi.git && \
	#cd $PaparazziDir && git remote update -p && \
	#git checkout -b v5.12 upstream/v5.12 && sudo cp conf/system/udev/rules/*.rules /etc/udev/rules.d/ && sudo udevadm control --reload-rules && \
	#make && ./paparazzi"
	Run "sudo add-apt-repository -y ppa:paparazzi-uav/ppa && sudo add-apt-repository -y ppa:team-gcc-arm-embedded/ppa && sudo apt-get update"
	Run "$aptInstall_Y -f --reinstall paparazzi-dev paparazzi-jsbsim gcc-arm-embedded && cd $RootDir && git clone --origin upstream https://github.com/paparazzi/paparazzi.git"
	Run "cd $PaparazziDir && git remote update -p"
	Run "git checkout -b v5.12 upstream/v5.12 && sudo cp conf/system/udev/rules/*.rules /etc/udev/rules.d/ && sudo udevadm control --reload-rules"
	Run "make && $RunPaparazziCmd"
else
    Warning "Paparazzi is not being installed!"
fi

#--------------------------------------------------------------
PrintSubHeader "Installing TUDelft MAVLab Remote"
#--------------------------------------------------------------

ConfirmQ="Do you want to integrate the TUDelft MAVLab Remote Code into Paparazzi [Y/n]?"
result=$(Confirm "$ConfirmQ")
if $result; then
	# Add MavlabCourse remote
	Run "cd $PaparazziDir"
	Run "git remote add mavlabCourse https://github.com/tudelft/paparazzi"
	Run "git fetch mavlabCourse mavlabCourse2018"
	Run "git checkout mavlabCourse2018"

	# Initialize Submodules
	Run "git submodule sync"
	Run "git submodule init"
	Run "git submodule update"

	# Build paparazzi
	Run "make clean"
	Run "make"

	## Select the right conf and control panel files using...
	#Run "$Python start.py"
else
    Warning "TUDelft MAVLab Remote is not being installed!"
fi

#--------------------------------------------------------------
PrintSubHeader "Installing Gazebo"
#------------------------------------------------------"--------

ConfirmQ="Do you want to (re-)install the Gazebo Simulator [Y/n]?"
result=$(Confirm "$ConfirmQ")
if $result; then
	Run "$aptInstall_Y --reinstall gazebo7 libgazebo7-dev"
	# --- Add Line to bashrc ---
	bashrc="~/.bashrc"
    Gazebo_bashrc_line="export GAZEBO_MODEL_PATH=\"$PaparazziDir/conf/simulator/gazebo/models:\$GAZEBO_MODEL_PATH\""
    printf "Configuring Gazebo environment by adding the following line '$Gazebo_bashrc_line' to the end of the file $bashrc\n"
    Run "echo $Gazebo_bashrc_line >> $bashrc"
else
    Warning "The Gazebo Simulator is not being installed!"
fi

#--------------------------------------------------------------
PrintSubHeader "Installing Eclipse"
#--------------------------------------------------------------

ConfirmQ="Do you want to (re-)install Eclipse [Y/n]?"
result=$(Confirm "$ConfirmQ")
if $result; then
	#Run "wget https://www.eclipse.org/downloads/download.php?file=/oomph/epp/neon/R2a/eclipse-inst-linux64.tar.gz"
	Run "$aptInstall_Y eclipse eclipse-cdt g++" #eclipse"
else
    Warning "Eclipse is not being installed!"
fi

#--------------------------------------------------------------
PrintSubHeader "Installing OpenCV (Bebop)"
#--------------------------------------------------------------

ConfirmQ="Do you want to build OpenCV for the bebop (THIS TAKES A LONG TIME!) [Y/n]?"
result=$(Confirm "$ConfirmQ")
if $result; then
	Run "cd $PaparazziDir/sw/ext/opencv_bebop"
	Run "make clean"
	Run "make"
else
    Warning "OpenCV (bebop) is not being installed!"
fi

#--------------------------------------------------------------
PrintSubHeader "Setup Paparazzi Config"
#--------------------------------------------------------------

## Setup Paparazzi Config
Run "cd $PaparazziDir"

ConfigInfo='
Select as Conf:         userconf/tudelft/course2018 conf.xml
   and as Controlpanel: userconf/tudelft/course2018 control panel.xml
'
printf "${ConfigInfo}"
Run "$Python start.py"

#----------------------------------------------------------
PrintHeader "Done installing Paparazzi! Run it by: \"\$cd $PaparazziDir && $RunPaparazziCmd\""
#----------------------------------------------------------

#=================================================================================
PrintHeader "Running Paparazzi"
#=================================================================================

Run "cd $PaparazziDir"
Run "$RunPaparazziCmd"
