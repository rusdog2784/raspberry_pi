
#!/usr/bin/python3
"""
Author:         Scott Russell

Date:           02/10/21

Description:    A Python script that is meant to be called during the Raspberry Pi's
                startup procedure. It gathers information about the Pi, then sends
                an email to the STARTUP_RECIPIENTS with the Pi's IP address and the
                information gathered.

Prerequisites:  1) Open the /etc/rc.local file and add the following commands inside
                   the if-statement block, 'if [ "$_IP" ]; then':
                    a) export GMAIL_USERNAME="<your gmail email account>"
                    b) export GMAIL_PASSWORD="<your gmail app password>"
                    c) export STARTUP_RECIPIENTS="<email 1>, <email 2>, etc"
                    d) python3 /home/pi/raspberry_pi/startup_mailer.py
                2) Make sure the python_utilities and raspberry_pi repositories are
                   cloned into your home path, /home/pi.
                3) Within '/var/log', Create a directory called 'startup_mailer'
                   ('mkdir /var/log/startup_mailer').
                4) For good measure, make the startup_mailer.py script executable
                   ('chmod +x startup_mailer.py').

Helpful Links:  Create Gmail App Password - https://support.google.com/accounts/answer/185833?hl=en
                Python Utilities Git Repo - https://github.com/rusdog2784/python_utilities.git
                Raspberry Pi Git Repo     - https://github.com/rusdog2784/raspberry_pi.git
"""
# Import system packages.
import os
import socket
import logging
from datetime import datetime
from pathlib import Path
# Import custom packages.
from gmail import Gmail, GmailException
from logger import setup_custom_logger
from rpi_system_statuses import get_cpu_temp, get_current_cpu_speed, \
    get_min_cpu_speed, get_max_cpu_speed, get_power_usage, get_memory_usage, \
    get_storage_usage


# Setting up this script's global variables.
APP_NAME = "startup_mailer"
LOG_DIRECTORY = Path(f"./logs")
LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

GMAIL_USERNAME = os.getenv("GMAIL_USERNAME")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
RECIPIENTS = os.getenv("STARTUP_RECIPIENTS").replace(" ", "").split(",")
DEFAULT_RECIPIENTS = ["srussell1383@gmail.com"]

if os.path.exists(LOG_DIRECTORY):
    initial_message = f"{APP_NAME} started."
else:
    initial_message = f"{APP_NAME} started, but the logging directory, " \
                      f"{LOG_DIRECTORY}, does not exist."
    LOG_DIRECTORY = Path(__file__).resolve()
LOGGER = setup_custom_logger(APP_NAME, LOG_DIRECTORY)
LOGGER.info(initial_message)


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


def send_an_email(subject: str, message: str, recipients: list) -> bool:
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
        send_an_email(subject=ERROR_SUBJECT, message=message, recipients=RECIPIENTS)
        exit(1)
    # Next, attempt to get the system information:
    try:
        system_information = system_status_information_as_html()
    except Exception as system_info_exception:
        LOGGER.error(f"Error gathering system information: {system_info_exception}")
        message = f"<h4>Error gathering system information: {system_info_exception}</h4>"
        send_an_email(subject=ERROR_SUBJECT, message=message, recipients=RECIPIENTS)
        exit(1)
    # Finally, send the email:
    subject = f"Pi @ {ip_address} started."
    send_an_email(subject=subject, message=system_information, recipients=RECIPIENTS)


if __name__ == "__main__":
    # Before doing anything, make sure the script successfully gathered the required
    # environment variables. If it didn't, notify the default recipient and quit.
    if None in (GMAIL_USERNAME, GMAIL_PASSWORD, RECIPIENTS):
        message = "<h4>The environment variables could not be found.</h4>"
        send_an_email(subject=ERROR_SUBJECT, message=message, recipients=DEFAULT_RECIPIENTS)
        exit(1)
    run_script()
