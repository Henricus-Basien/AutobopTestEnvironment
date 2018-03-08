OpenCV_Header='
________                       _____________   ____
\_____  \ ______   ____   ____ \_   ___ \   \ /   /
 /   |   \\\\____ \_/ __ \ /    \/    \  \/\   Y   / 
/    |    \  |_> >  ___/|   |  \     \____\     /  
\_______  /   __/ \___  >___|  /\______  / \___/   
        \/|__|        \/     \/        \/          
.___                 __         .__  .__                       
|   | ____   _______/  |______  |  | |  |   ___________        
|   |/    \ /  ___/\   __\__  \ |  | |  | _/ __ \_  __ \       
|   |   |  \\\\___ \  |  |  / __ \|  |_|  |_\  ___/|  | \/       
|___|___|  /____  > |__| (____  /____/____/\___  >__|          
         \/     \/            \/               \/              
'
printf "${OpenCV_Header}"

printf "Created on 08.03.2018 by Henricus N. Basien (Henricus@Basien.de)"
printf "Based on 'https://www.pyimagesearch.com/2015/06/22/install-opencv-3-0-and-python-2-7-on-ubuntu/'"

#=================================================================================
# Initialization
#=================================================================================

DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
. "$DIR/Installer_Init.sh"

#=================================================================================
PrintHeader "Installation"
#=================================================================================

echo "Please fill in your sudo Password to install OpenCV: "
sudo echo "Thank you!"

#--------------------------------------------------------------
PrintSubHeader "Installing Required Programs"
#--------------------------------------------------------------

Run "$aptInstall_Y build-essential cmake git pkg-config"
Run "$aptInstall_Y libjpeg8-dev libtiff4-dev libjasper-dev libpng12-dev"
Run "$aptInstall_Y libgtk2.0-dev"
Run "$aptInstall_Y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev"
Run "$aptInstall_Y libatlas-base-dev gfortran"


#--------------------------------------------------------------
PrintSubHeader "Installing OpenCV"
#--------------------------------------------------------------

ConfirmQ="Do you want to (re-)install OpenCV [Y/n]?"
result=$(Confirm "$ConfirmQ")
if $result; then
	Run "cd ~"
	Run "git clone https://github.com/Itseez/opencv.git"
	Run "cd opencv"
	Run "git checkout 3.0.0"

	Run "cd ~/opencv"
	Run "mkdir build"
	Run "cd build"
	cmake -D CMAKE_BUILD_TYPE=RELEASE \
		-D CMAKE_INSTALL_PREFIX=/usr/local \
		-D INSTALL_C_EXAMPLES=ON \
		-D INSTALL_PYTHON_EXAMPLES=ON \
		-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
		-D BUILD_EXAMPLES=ON ..

	Run "make -j4"

	Run "sudo make install"
	Run "sudo ldconfig"
else
    Warning "OpenCV is not being installed!"
fi


