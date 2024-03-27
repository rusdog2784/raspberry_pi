#!/usr/bin/python3

"""
Author:         Scott Russell

Date Created:   02/10/21
Date Updated:   03/27/24

Description:    A Python script that is meant to be called during the Raspberry 
                Pi's startup procedure. It gathers information about the Pi, 
                then sends an email with the Pi's IP address and the information 
                gathered.

Prerequisites:  1) Run the `rpi_setup.sh` script.

Helpful Links:  Create Gmail App Password - https://support.google.com/accounts/answer/185833?hl=en
                Python Utilities Git Repo - https://github.com/rusdog2784/python_utilities.git
                Raspberry Pi Git Repo     - https://github.com/rusdog2784/raspberry_pi.git
"""
# Import system packages.
import os
import socket
from pathlib import Path
# Import custom packages.
from gmail import Gmail
from logger import setup_custom_logger
from rpi_system_statuses import (
    get_cpu_temp,
    get_power_usage,
    get_memory_usage,
    get_storage_usage
)


# Setting up this script's global variables.
APP_NAME = "startup_mailer"
LOG_DIRECTORY = Path(f"./logs")
LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)    
LOGGER = setup_custom_logger(APP_NAME, LOG_DIRECTORY)
LOGGER.info(f"Starting the '{APP_NAME}' script.")
DEFAULT_RECIPIENT = ["srussell1383@gmail.com"]
try:
    PI_HOSTNAME = socket.gethostname()
    GMAIL_USERNAME = os.getenv("GMAIL_USERNAME")
    GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
    RECIPIENT = [os.getenv("STARTUP_RECIPIENT_EMAIL", "")]
    ERROR_SUBJECT = f"Startup script failed for '{PI_HOSTNAME}'"
except Exception as global_exception:
    LOGGER.critical(f"Error setting up global variables: {global_exception}")
    exit(1)


def get_ip() -> str:
    """
    Returns the IP address for the Raspberry Pi.
    :return: IP address string.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 53))
    return s.getsockname()[0]


def system_status_information_as_html() -> str:
    """
    Using the raspberry_pi.rpi_system_statuses module, this function gathers important
    Raspberry Pi system information then packs it into a formatted HTML table, which
    can be sent in an email body.
    :return: Large string containing a formatted HTML table showing the Raspberry Pi's
        system information.
    """
    cpu_temp = get_cpu_temp()
    power_usage = get_power_usage()
    memory_info = get_memory_usage()
    total_memory = memory_info.get('total').get('memory')
    used_memory = memory_info.get('used').get('memory')
    free_memory = memory_info.get('free').get('memory')
    storage_info = get_storage_usage()
    total_storage = storage_info.get('total')
    used_storage = storage_info.get('used')
    used_storage_percent = storage_info.get('used %')
    free_storage = storage_info.get('free')
    free_storage_percent = storage_info.get('free %')
    html = f"""
    <h2>Here are your system's statistics:</h2>
    <table>
        <tr>
            <th style="text-align: left;">CPU Temp:</th>
            <td>{cpu_temp}</td>
        </tr>
        <tr>
            <th style="text-align: left;">Power:</th>
            <td>{power_usage}</td>
        </tr>
        <tr>
            <th>Memory Information:</th>
        </tr>
        <tr>
            <th>Total:</th>
            <td>{total_memory}</td>
        </tr>
        <tr>
            <th>Used:</th>
            <td>{used_memory}</td>
        </tr>
        <tr>
            <th>Free:</th>
            <td>{free_memory}</td>
        </tr>
        <tr>
            <th>Storage Information:</th>
        </tr>
        <tr>
            <th>Total:</th>
            <td>{total_storage}</td>
        </tr>
        <tr>
            <th>Used:</th>
            <td>{used_storage} ({used_storage_percent})</td>
        </tr>
        <tr>
            <th>Free:</th>
            <td>{free_storage} ({free_storage_percent})</td>
        </tr>
    </table>
    """
    return html


def send_an_email(subject: str, message: str, recipients : list) -> bool:
    """
    Using the imported Gmail module, this function sends an email to the provided
    recipients with the provided subject and message.
    :param subject: Subject of the email.
    :param message: HTML string containing the message of the email.
    :param recipients: List of email addresses.
    :return: Boolean where True means the email was sent successfully, and False
        means the email failed to send.
    """
    # Attempt to configure the gmail object.
    try:
        gmail = Gmail(GMAIL_USERNAME, GMAIL_PASSWORD)
        gmail.set_recipients(recipients)
        gmail.set_subject(subject)
        gmail.add_html(message)
    except Exception as email_config_exception:
        LOGGER.error(f"Error configuring the gmail object: {email_config_exception}")
        return False
    # Attempt to send the email.
    try:
        gmail.send_email()
        LOGGER.info("Email successfully sent.")
    except Exception as email_exception:
        LOGGER.error(f"Error sending the email: {email_exception}")
        return False
    return True


def run_script() -> None:
    """
    Function that gets called when the script is run. Controls what gets executed.
    :return: Void.
    """
    message = str()
    
    # First, attempt to get the IP address:
    try:
        ip_address = get_ip()
    except Exception as ip_exception:
        LOGGER.error(f"Error gathering the IP address: {ip_exception}")
        message = f"<h4>Error gathering the IP address: {ip_exception}</h4>"
        send_an_email(subject=ERROR_SUBJECT, message=message, recipients=RECIPIENT)
        exit(1)
        
    # Next, attempt to get the system information:
    try:
        system_information = system_status_information_as_html()
    except Exception as system_info_exception:
        LOGGER.error(f"Error gathering system information: {system_info_exception}")
        message = f"<h4>Error gathering system information: {system_info_exception}</h4>"
        send_an_email(subject=ERROR_SUBJECT, message=message, recipients=RECIPIENT)
        exit(1)
    
    # If everything works out, send the success email:
    subject = f"'{PI_HOSTNAME}' successfully started @ {ip_address}"
    send_an_email(subject=subject, message=system_information, recipients=RECIPIENT)


if __name__ == "__main__":
    run_script()
