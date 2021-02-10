"""
Author:       Scott Russell
Date:         12-15-2020
Description:  Contains functions capable of returning information about
              a RaspberryPi system.
"""
import os
import re


def get_cpu_temp() -> str:
    """
    Using the os command, cvgencmd measure_temp, this function returns the current
    cpu temperature for the system.
    :return: String value of the current cpu temperature (in degrees Celcius).
    """
    cpu_temp = str(os.popen('vcgencmd measure_temp').read()).replace("\n", "")
    return cpu_temp.split('temp=')[-1]    # Only care about the value.


def get_current_cpu_speed() -> str:
    """
    Using the os command, cvgencmd measure_clock, this function returns the current
    cpu frequency for the system.
    :return: String value of the current cpu frequency (in MHz).
    """
    cpu_speed = str(os.popen('vcgencmd measure_clock arm').read()).replace("\n", "")
    cpu_speed = int(cpu_speed.split('frequency(48)=')[-1]) / 1000000    # Convert from Hz to Mhz.
    return str(round(cpu_speed, 2)) + "MHz"


def get_max_cpu_speed() -> str:
    """
    Using the config file, cpuinfo_max_freq, this function returns the maximum cpu
    frequency for the system.
    :return: String value of the maximum cpu frequency (in MHz).
    """
    max_cpu_speed = os.popen('cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq').read()
    max_cpu_speed = int(max_cpu_speed) / 1000    # Convert from kHz to MHz.
    return str(max_cpu_speed) + "MHz"


def get_min_cpu_speed() -> str:
    """
    Using the config file, cpuinfo_min_freq, this function returns the minimum cpu
    frequency for the system.
    :return: String value of the minimum cpu frequency (in MHz).
    """
    min_cpu_speed = os.popen('cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq').read()
    min_cpu_speed = int(min_cpu_speed) / 1000    # Convert from kHz to MHz.
    return str(min_cpu_speed) + "MHz"


def get_power_usage() -> str:
    """
    Using the os command, cvgencmd measure_volts, this function returns the current
    voltage being used by the system.
    :return: String value of the voltage being used (in Volts).
    """
    power_usage = str(os.popen('vcgencmd measure_volts').read()).replace("\n", "")
    return power_usage.split('volt=')[-1]    # Only care about the value.


def get_memory_usage() -> dict:
    """
    Using the os command, free, this function gathers the current memory
    information of the system.
    :return: Dictionary in the format: {
        'total': {
            'memory': <total normal memory in the system>,
            'swap': <total swap memory in the system>
        },
        'used': {
            'memory': <amount of used normal memory>,
            'swap': <amount of used swap memory>
        },
        'free': {
            'memory': <amount of free normal memory>,
            'swap': <amount of free swap memory>
        }
    }
    """
    free_cmd = os.popen('free -h').read()
    rows = free_cmd.split('\n')
    # Extract the titles and memory values (memory, swap) into their own variables.
    titles = str(rows[0]).strip()
    memory = str(rows[1]).strip()
    swap = str(rows[2]).strip()
    # Massage the extracted data into lists.
    titles = str(re.sub(' +', ' ', titles)).split(' ')
    memory = str(re.sub(' +', ' ', memory)).split(' ')[1:]
    swap = str(re.sub(' +', ' ', swap)).split(' ')[1:]
    # Combine everything into a dictionary.
    memory_usage = dict()
    for i in range(3):
        memory_usage[titles[i]] = {
            'memory': memory[i],
            'swap': swap[i]
        }
    return memory_usage


def get_storage_usage() -> dict:
    """
    Using the os command, df, this function gathers the current storage
    information of the system.
    :return: Dictionary in the format: {
        'total': <total size of the filesystem>,
        'used': <amount of used storage>,
        'free': <amount of free storage>,
        'used %': <percent value of used storage>,
        'free %': <percent value of free storage>
    }
    """
    titles = ["total", "used", "free", "used %"]
    storage_data = os.popen('df -h | grep "/dev/root"').read()
    storage_data = re.sub(' +', ' ', storage_data).split(' ')[1:]
    storage_usage = dict()
    for i in range(len(titles)):
        storage_usage[titles[i]] = storage_data[i]
    storage_usage['free %'] = str(
        100 - int(storage_usage.get('used %').replace("%", ""))
    ) + "%"
    return storage_usage
    
