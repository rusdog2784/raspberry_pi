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
sudo raspi-config nonint do_boot_wait 0

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
	"'/etc/dhcpcd.conf'.\n"
else
	echo -e "\nHere are the active IP addresses on your network:\n"
	nmap -sn 192.168.1.0/24

	read -rep $'\nEnter the IP address you want to set for this device (i.e.: x.x.x.x): ' static_ip_address
	echo -e "\nPerfect, I'll set this device's static IP address to: ${static_ip_address}"

	new_dhcp_interface="\n# This section was set by the rpi_setup.sh script.\n"\
"interface wlan0\n"\
"static ip_address=${static_ip_address}/24\n"\
"static routers=192.168.1.1\n"\
"static domain_name_servers=192.168.1.1\n"
	echo -e "${new_dhcp_interface}" >> /etc/dhcpcd.conf
	echo -e "\nAdded the following snippet to the /etc/dhcpcd.conf file:\n${new_dhcp_interface}\n"
fi

#############################################################################################

echo -e "\nOk, now we're gonna set up the startup mailer script. Once set"\
	"up, it'll send an email to a recipient of your choosing with"\
	"the system statistics of this RaspberryPi (i.e.: its IP address,"\
	"current storage, etc.). Hit Enter to continue."
read null

if grep -rnw "export GMAIL_USERNAME" /etc/rc.local &> /dev/null ; then
        echo -e "It looks like you already have the startup mailer script setup."\
	"If you want to change it, you'll have to do it manually by going to"\
	"'/etc/rc.local'.\n"
else
	echo -e "\nTo start, please enter the following details..."
	read -rep $'Enter GMAIL_USERNAME: ' gmail_username
	read -rep $'Enter GMAIL_PASSWORD: ' gmail_password
	read -rep $'Enter email recipient: ' email_recipient

	text_to_replace="fi"
	new_rc_local_entry="\t# This section was set by the rpi_setup.sh script.\n"\
"\texport GMAIL_USERNAME=\"${gmail_username}\"\n"\
"\texport GMAIL_PASSWORD=\"${gmail_password}\"\n"\
"\texport STARTUP_RECIPIENTS=\"${email_recipient}\"\n"\
"\tpython3 $(pwd)/startup_mailer.py\n"\
"fi"

	sudo sed -i "s|${text_to_replace}|${new_rc_local_entry}|g" /etc/rc.local
	echo -e "\nAdded the following snippet to the /etc/rc.local file:\n${new_rc_local_entry}\n"
fi


echo -e "\n\nThat's all folks!\n"
