from time import sleep
from sense_hat import SenseHat, ACTION_RELEASED, ACTION_HELD

sense = SenseHat()
sense.clear()
sense.set_rotation(180)
sense.low_light = True

X = [255, 0, 0]
O = [255, 255, 0]
bulls_eye = [
	X, X, O, O, O, O, X, X,
	X, O, X, X, X, X, O, X,
	O, X, X, O, O, X, X, O,
	O, X, O, O, O, O, X, O,
	O, X, O, O, O, O, X, O,
	O, X, X, O, O, X, X, O,
	X, O, X, X, X, X, O, X,
	X, X, O, O, O, O, X, X
]
up_arrow = [
	X, X, X, O, O, X, X, X,
	X, X, O, O, O, O, X, X,
	X, O, O, O, O, O, O, X,
	X, O, O, O, O, O, O, X,
	X, X, X, O, O, X, X, X,
	X, X, X, O, O, X, X, X,
	X, X, X, O, O, X, X, X,
	X, X, X, O, O, X, X, X
]


def to_fahrenheit(degrees_c):
	fahrenheit = (degrees_c * (9/5)) + 32
	return fahrenheit


def button_pressed_up(event):
	if event.action == ACTION_RELEASED:
		sense.set_pixels(up_arrow)
		sleep(1.5)
		sense.clear()


def button_pressed_down(event):
	if event.action == ACTION_RELEASED:
		temp_c = sense.get_temperature()
		temp_f = to_fahrenheit(temp_c)
		temp = f"{temp_f:.2f} F"
		sense.show_message(temp)


def button_pressed_middle(event):
	if event.action == ACTION_RELEASED:
		sense.set_pixels(bulls_eye)
		sleep(1.5)
		sense.clear()


sense.stick.direction_down = button_pressed_up
sense.stick.direction_up = button_pressed_down
sense.stick.direction_middle = button_pressed_middle


while True:
	pass

