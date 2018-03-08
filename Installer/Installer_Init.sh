#=================================================================================
# Settings
#=================================================================================

#--- Cosmetic ---
HeaderLen=120
SubHeaderLen=80

#=================================================================================
# Functions
#=================================================================================

#+++++++++++++++++++++++++++++++++++++++++++
# Console Output
#+++++++++++++++++++++++++++++++++++++++++++

function MultiString(){
    str=$1
    num=$2
    v=$(printf "%-${num}s" "$str")
    echo "${v// /$str}"
}

#-------------------------------------------
# Headers
#-------------------------------------------

MasterHeader=$(MultiString "*" $HeaderLen)
SubHeader=$(MultiString "=" $SubHeaderLen)
WarningHeader=$(MultiString "!" $SubHeaderLen)

function PrintHeader(){
    printf "\n$MasterHeader\n$1\n$MasterHeader\n"
    #Speak $1
}

function PrintSubHeader(){
    printf "\n$SubHeader\n$1\n$SubHeader\n"
    #Speak $1
}

function Warning(){
    printf "\n$WarningHeader\nWARNING: $1!\n$WarningHeader\n"
}

#+++++++++++++++++++++++++++++++++++++++++++
# Run
#+++++++++++++++++++++++++++++++++++++++++++

function Run(){
    printf "\nCMD: $1\n\n";eval $1
    #result=eval $1
    #echo result
}

#+++++++++++++++++++++++++++++++++++++++++++
# Install Functions
#+++++++++++++++++++++++++++++++++++++++++++

yes="-y"
yesF="$yes" # --force-yes"

#...........................
# apt(-get)
#...........................

apt="apt-get"
aptInstall="sudo $apt install"
aptInstall_Y="$aptInstall $yesF"

#...........................
# pip
#...........................

pipInstall="pip install"

#+++++++++++++++++++++++++++++++++++++++++++
# Confirmation
#+++++++++++++++++++++++++++++++++++++++++++

Confirm() {
    # call with a prompt string or use a default
    read -r -p "${1:-Are you sure? [y/N]} " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            echo true
            ;;
        *)
            echo false
            ;;
    esac
}