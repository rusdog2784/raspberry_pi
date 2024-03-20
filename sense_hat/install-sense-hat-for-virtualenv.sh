#!/bin/bash

###
# Instructions from https://github.com/astro-pi/python-sense-hat/issues/58#issuecomment-374414765
###

# Clone and install RTIMULib dependency
git clone https://github.com/RPi-Distro/RTIMULib/ RTIMU
cd RTIMU/Linux/python
sudo apt install python3-dev
python setup.py build
python setup.py install

# Install libopenjp2-7 package
sudo apt install libopenjp2-7

# Install sense-hat package
sudo apt install sense-hat

# Install SenseHat python module
pip install sense-hat

# Remove RTIMULib git repo
cd ../../..
rm -rf RTIMU

echo "DONE."
