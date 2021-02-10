#!/usr/bin/python3

"""
Author:       Scott Russell
Date:         01-05-2020
Description:  Script responsible for gathering and saving 5 days worth of environment
              data, fetched every hour.
"""

# Add pi's Python directory as a valid package repo:
import sys
sys.path.append("/home/pi/Python")

# Personal Imports
from modules.rpi_system_statuses import get_cpu_temp
from modules.logger import setup_custom_logger
# System Imports:
from time import sleep
from pathlib import Path
from sense_hat import SenseHat

# Environment Variables:
APP_NAME = "environment_data"
LOG_DIR = Path("/var/log/senseHAT")
LOGGER = setup_custom_logger(APP_NAME, LOG_DIR, 3)


sense = SenseHat()


def get_environment_data():
    """
    Returns the SenseHAT's environment data.
    :return: A tuple with in the following format:
        1) temperature
        2) pressure
        3) humidity
    """
    temperature = sense.get_temperature()
    pressure = sense.get_pressure()
    humidity = sense.get_humidity()
    return temperature, pressure, humidity


def save_environment_data():
    """
    Logs the SenseHAT environment data to a log file specified at the top of this
    script.
    :return: None.
    """
    temperature, pressure, humidity = get_environment_data()
    message = f"Temperature: {temperature}, Pressure: {pressure}, Humidity: {humidity}"
    LOGGER.info(message)


save_environment_data()
