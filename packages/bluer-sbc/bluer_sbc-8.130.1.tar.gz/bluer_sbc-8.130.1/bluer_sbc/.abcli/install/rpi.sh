#! /usr/bin/env bash

function bluer_ai_install_rpi() {
    pushd $abcli_path_git >/dev/null

    # https://docs.donkeycar.com/guide/robot_sbc/setup_raspberry_pi/
    sudo apt-get update
    sudo apt-get -y upgrade

    sudo apt-get --yes --force-yes install build-essential python3 python3-dev python3-pip \
        python3-virtualenv python3-numpy python3-picamera python3-pandas python3-rpi.gpio \
        i2c-tools avahi-utils joystick libopenjp2-7-dev libtiff5-dev gfortran libatlas-base-dev \
        libopenblas-dev libhdf5-serial-dev libgeos-dev git ntp

    sudo apt-get --yes --force-yes install libilmbase-dev libopenexr-dev libgstreamer1.0-dev \
        libjasper-dev libwebp-dev libatlas-base-dev libavcodec-dev libavformat-dev libswscale-dev \
        libqtgui4 libqt4-test

    # https://rtcbot.readthedocs.io/en/latest/installing.html
    sudo apt-get --yes --force-yes install python3-numpy python3-cffi python3-aiohttp \
        libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev \
        libswscale-dev libswresample-dev libavfilter-dev libopus-dev \
        libvpx-dev pkg-config libsrtp2-dev python3-opencv pulseaudio

    cd
    python3 -m virtualenv -p python3 env --system-site-packages
    echo "source env/bin/activate" >>~/.bashrc
    source env/bin/activate

    cd git
    git clone https://github.com/autorope/donkeycar
    cd donkeycar
    git checkout master
    pip3 install -e .[pi]

    pip3 install numpy --upgrade

    cd
    curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=1DCfoSwlsdX9X4E3pLClE1z0fvw8tFESP" >/dev/null
    CODE="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"
    curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${CODE}&id=1DCfoSwlsdX9X4E3pLClE1z0fvw8tFESP" -o tensorflow-2.2.0-cp37-cp37m-linux_armv7l.whl
    pip3 install tensorflow-2.2.0-cp37-cp37m-linux_armv7l.whl

    sudo apt --yes --force-yes install python3-opencv

    pip3 install PyMySQL==0.10.1
    pip3 install tqdm
    pip3 install boto3
    pip3 install dill
    pip3 install imutils

    # https://rtcbot.readthedocs.io/en/latest/installing.html
    # pip install rtcbot

    pip3 install awscli --upgrade
    if [[ $PATH != *"/home/pi/.local/bin"* ]]; then
        export PATH=/home/pi/.local/bin:$PATH
    fi

    popd >/dev/null
}

if [ "$abcli_is_rpi" == true ]; then
    bluer_ai_install_module rpi 109
fi
