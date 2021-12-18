#!/bin/bash

echo -e "Hello, and welcome. This script is going to"\
	"help walk you through setting up this RaspberryPi."\
	"It'll take care of configuring some of the"\
	"basic settings that you'll probably be needing (i.e.:"\
	"configuring a static IP). Alrighty, let's get started."\
	"Hit Enter when ready."
read null

#############################################################################################

echo -e "\nFirst things first. I'm going to update your"\
	"system and install some dependencies. FYI, this"\
	"might take a few minutes. Hit Enter to continue."
read null
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y nmap
sudo apt-get autoremove -y

#############################################################################################

echo -e "\nGreat! We're gonna start by setting up a static IP"\
	"for this device. To do this, I'm going to first print"\
	"out a list of the active IP addresses on your"\
	"network. Then I'll need you to enter an IP"\
	"address that isn't in the list that you want this"\
	"RaspberryPi to have. Hit Enter to continue."
read null

if grep -rnw "interface wlan0" /etc/dhcpcd.conf &> /dev/null ; then
	echo -e "It looks like you already have a static IP set for wlan0 (wifi)."\
	"If you want to change it, you'll have to do it manually by going to"\
	"'/etc/dhcpcd.conf'."
	exit 0
fi

echo -e "\nHere are the active IP addresses on your network:\n"
nmap -sn 192.168.1.0/24

read -rep $'\nEnter the static IP address you want to set for this device'\
'(format: x.x.x.x): ' static_ip_address
echo -e "\nPerfect, I'll set this device's static IP address to: ${static_ip_address}"

new_dhcp_interface="\n# This section was set by the rpi_setup.sh script.\n"\
"interface wlan0\n"\
"static ip_address=${static_ip_address}/24\n"\
"static routers=192.168.1.1\n"\
"static domain_name_servers=192.168.1.1\n"
echo -e "${new_dhcp_interface}" >> /etc/dhcpcd.conf
echo -e "\nAdded the following snippet to the /etc/dhcpcd.conf file:\n${new_dhcp_interface}\n"


