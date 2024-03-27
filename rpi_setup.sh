#!/bin/bash

WARNING_COUNT=0

### Welcome Message ############################################################

echo -e "Hello, and welcome!"
echo
echo -e "This script is going to help walk you through setting up this"\
		"RaspberryPi. We're going to install some basic dependencies, set up"\
		"a static IP address, and create a startup mailer script that will"\
		"send an email with the system statistics of this device when the"\
		"device boots up."
echo
echo -e "If you're ready to get started, please enter the following details,"\
		"otherwise press Ctrl-C at anytime to exit."
echo

echo -en "Thank you! We'll get started in "
sleep 1 && echo -en "3... "
sleep 1 && echo -en "2... "
sleep 1 && echo -e "1... "
echo

### Install Dependencies #######################################################

dependencies=("nmap" "git")

echo -e "First things first. I'm going to update your system and install the"\
		"following dependencies: "
for dependency in "${dependencies[@]}"; do
	echo -e "\t- ${dependency}"
done
sleep 2
echo

echo -e "[START] Updating system (running apt update and apt upgrade)..."
sudo apt update && sudo apt upgrade -y
echo -e "[SUCCESS] System updated."
echo

echo -e "[START] Setting raspberry pi config to wait for network on boot..."
sudo raspi-config nonint do_boot_wait 0
echo -e "[SUCCESS] Raspberry pi config set to wait for network on boot."
echo

echo -e "[START] Installing dependencies..."
sudo apt install -y "${dependencies[@]}"
echo -e "[SUCCESS] Dependencies installed."
echo

### Static IP Configuration ####################################################

network_interface="$(route | grep '^default' | grep -o '[^ ]*$')"
router_ip_address="$(ip route show | grep -i 'default via'| awk '{print $3 }')"
home_network_subnet="$router_ip_address/24"

echo -e "Great! Next we're going to set a static IP for this device. To do"\
		"this, I'm going to print out a list of available IP addresses on your"\
		"network, then you're going to enter one."
sleep 2
echo

echo -e "Here are the active IP addresses on your network (this may take a"\
		"minute):"
nmap -v -sn -n $home_network_subnet -oG - | awk '/Status: Down/{print $2}'
echo
echo -e "Please review the list of IPs above then enter one that you'd like to"\
		"set for this device."
read -rep $'\tStatic IP Address: ' static_ip_address
echo
echo -e "Ok, I'll set this device's static IP address to: ${static_ip_address}"
echo

echo -e "[START] Configuring static IP for $network_interface in /etc/dhcpcd.conf..."
# Create the static IP configuration for the network interface
dhcp_static_ip_configuration="
# $network_interface Static IP Configuration:
interface $network_interface
static ip_address=$static_ip_address/24
static routers=$router_ip_address
static domain_name_servers=1.1.1.1  # Cloudflare Public DNS
"
# Checking if the network interface is already configured in /etc/dhcpcd.conf
if grep -qE "^\s*interface\s+$network_interface\b" /etc/dhcpcd.conf; then
	((WARNING_COUNT++))
    echo -e "[WARNING] Interface $network_interface already seems to be"\
			"configured in /etc/dhcpcd.conf. Please update the configuration "\
			"manually with the following settings:"
	echo -e "\t$dhcp_static_ip_configuration"
else
    sudo bash -c "echo -e \"\n\n$dhcp_static_ip_configuration\n\" >> /etc/dhcpcd.conf"
	echo -e "[SUCCESS] Static IP configuration added to /etc/dhcpcd.conf."
fi
echo

### Startup Mailer Setup #######################################################

gmail_username=""	# default value
gmail_password=""	# default value
email_recipient=""	# default value

echo -e "Fantastic! Lastly, we're going to setup the startup mailer service so"\
		"that you receive an email with the IP and system statistics of this"\
		"device when it boots up."
sleep 2
echo

echo -e "Before continuing, please enter the following details:"
read -rep $'\tEnter the Gmail username (sender account): ' gmail_username
read -rep $'\tEnter the Gmail password (sender account): ' gmail_password
read -rep $'\tEnter the email address for the recipient: ' email_recipient
echo

echo -e "[START] Creating the environment file for the startup mailer service..."
echo -e "# Entries set by the rpi_setup.sh script" > ./startup_mailer.env
echo "GMAIL_USERNAME=\"$gmail_username\"" >> ./startup_mailer.env
echo "GMAIL_PASSWORD=\"$gmail_password\"" >> ./startup_mailer.env
echo "STARTUP_RECIPIENT_EMAIL=\"$email_recipient\"" >> ./startup_mailer.env
sudo chmod 600 ./startup_mailer.env
sudo chmod +x ./startup_mailer.py
echo -e "[SUCCESS] Environment file created."
echo

echo -e "[START] Copying the startup_mailer.service file into /etc/systemd/system/..."
sudo cp ./startup_mailer.service.copy /etc/systemd/system/startup_mailer.service
echo -e "[SUCCESS] startup_mailer.service file copied."
echo

echo -e "[START] Enabling the startup_mailer service..."
sudo systemctl daemon-reload
sudo systemctl enable startup_mailer.service
echo -e "[SUCCESS] startup_mailer service enabled."
echo

### Closing Message #############################################################

# If WARNING_COUNT is greater than 0, print a message to the user saying that 
# they should review the printed messages and address any [WARNING] messages.
if [ $WARNING_COUNT -gt 0 ]; then
	echo -e "\n*** IMPORTANT ***"
	echo -e "Please review the printed messages and address any [WARNING] messages."
	echo -e "*** IMPORTANT ***\n"
fi

echo -e "Congratulations! The setup process is complete. Your Raspberry Pi is"\
		"now configured with the necessary dependencies, a static IP address,"\
		"and the startup mailer service. You're all set to start using your "\
		"Raspberry Pi!"
echo
echo -e "If you encounter any issues or have any questions, please refer to the"\
		"documentation or seek assistance from the github page."
echo
echo -e "Have a great day!"

#############################################################################################
