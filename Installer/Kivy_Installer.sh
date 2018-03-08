Kivy_Header='
 ____  __.__              
|    |/ _|__|__  _____.__.
|      < |  \  \/ <   |  |
|    |  \|  |\   / \___  |
|____|__ \__| \_/  / ____|
        \/         \/     
.___                 __         .__  .__                       
|   | ____   _______/  |______  |  | |  |   ___________        
|   |/    \ /  ___/\   __\__  \ |  | |  | _/ __ \_  __ \       
|   |   |  \\\\___ \  |  |  / __ \|  |_|  |_\  ___/|  | \/       
|___|___|  /____  > |__| (____  /____/____/\___  >__|          
         \/     \/            \/               \/              
'
printf "${Kivy_Header}"

printf "Created on 08.03.2018 by Henricus N. Basien (Henricus@Basien.de)"

#=================================================================================
# Initialization
#=================================================================================

DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
. "$DIR/Installer_Init.sh"

#=================================================================================
PrintHeader "Installation"
#=================================================================================

echo "Please fill in your sudo Password to install Kivy: "
sudo echo "Thank you!"

#--------------------------------------------------------------
PrintSubHeader "Installing Required Programs"
#--------------------------------------------------------------

Run "sudo $apt update"
Run "$pipInstall cython"

# Install necessary system packages
sudo apt-get install -y \
    python-pip \
    build-essential \
    git \
    python \
    python-dev \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev

# Install gstreamer for audio, video (optional)
sudo apt-get install -y \
    libgstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good

#Note: Depending on your Linux version, you may receive error messages related to the “ffmpeg” package. In this scenario, use “libav-tools ” in place of “ffmpeg ” (above), or use a PPA (as shown below):

sudo add-apt-repository ppa:mc3man/trusty-media
sudo apt-get update
sudo apt-get install ffmpeg



#--------------------------------------------------------------
PrintSubHeader "Installing Kivy"
#--------------------------------------------------------------

ConfirmQ="Do you want to (re-)install Kivy [Y/n]?"
result=$(Confirm "$ConfirmQ")
if $result; then
	Run "$aptInstall_Y python-kivy"
else
    Warning "Kivy is not being installed!"
fi


