import sys
sys.path.append("/home/pi/Python")
from sense_hat import SenseHat, ACTION_RELEASED
from datetime import datetime
from modules.rpi_system_statuses import get_cpu_temp


sense = SenseHat()
sense.set_rotation(180)


def get_calibrated_temp():
    temp = sense.temp
    cpu_temp = float(get_cpu_temp().replace("'C", ""))
    calibrated_temp = temp - ((cpu_temp - temp) / 1.17)
    return calibrated_temp

def get_environment_data():
    temperature = get_calibrated_temp()
    pressure = sense.get_pressure()
    humidity = sense.get_humidity()
    return temperature, pressure, humidity
    
def get_orientation_data():
    orientation = sense.get_orientation()
    yaw = orientation["yaw"]
    pitch = orientation["pitch"]
    roll = orientation["roll"]
    return yaw, pitch, roll

def get_compass_data():
    compass = sense.get_compass_raw()
    x = compass["x"]
    y = compass["y"]
    z = compass["z"]
    return x, y, z

def get_accelerometer_data():
    acc = sense.get_accelerometer_raw()
    x = acc["x"]
    y = acc["y"]
    z = acc["z"]
    return x, y, z

def get_gyroscope_data():
    gyro = sense.get_gyroscope_raw()
    x = gyro["x"]
    y = gyro["y"]
    z = gyro["z"]
    return x, y, z

def button_pushed_middle(event):
    if event.action == ACTION_RELEASED:
        sense.show_message("OW!")
    

sense.stick.direction_middle = button_pushed_middle
