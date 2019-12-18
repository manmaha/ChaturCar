import joysticks
from time import sleep
import evdev

## Some helpers ##
def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.

    val: float or int
    src: tuple
    dst: tuple

    example: print(scale(99, (0.0, 99.0), (-1.0, +1.0)))
    """
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def scale_stick(value):
    return scale(value,(0,255),(-100,100))

def clamp(value, floor=-100, ceil=100):
    """
    Clamp the value within the floor and ceiling values.
    """
    return max(min(value, ceil), floor)

## Initializing ##

js = joysticks.JoyStick('Xbox Wireless Controller')
print(js.capabilities())
js = js.joystick

for event in js.read_loop():   #this loops infinitely
    keyevent = evdev.categorize(event)
    if event.type == 1  and event.value == 1 and event.code in [310, 311,307]:
        print('Stopping')
        break
    if event.type == 3 or event.type == 1 :             #One of the sticks is moved
        keyevent = evdev.categorize(event)

        # Add if clauses here to catch more values for your robot.
        if event.code == 1:         #Y axis on left stick
            speed = scale(event.value,(0,255),(-0.45,0.45))
            print(keyevent)
        if event.code == 2:         #X axis on right stick
            turn = scale(event.value,(0,255),(-1.0,1.0))
            print(keyevent)
        #print(speed,turn)
    if event.type ==1 and event.code == 307 and event.value == 1:
            print("X button is pressed. Stopping.")
            break
