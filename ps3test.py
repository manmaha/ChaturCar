import evdev
from time import sleep

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
print("Finding ps3 controller...")
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
for device in devices:
    if device.name == 'PLAYSTATION(R)3 Controller':
        ps3dev = device.fn

gamepad = evdev.InputDevice(ps3dev)

# Initialize globals
speed = 0
turn = 0
for event in gamepad.read_loop():   #this loops infinitely

    if event.type == 3 or event.type == 1 :             #One of the sticks is moved
        keyevent = evdev.categorize(event)

        # Add if clauses here to catch more values for your robot.
        if event.code == 4:         #Y axis on right stick
            speed = scale(event.value,(0,255),(-0.45,0.45))
            print(event.value)
        if event.code == 3:         #X axis on right stick
            turn = scale(event.value,(0,255),(-1.0,1.0))
            print(event.value)
        #print(speed,turn)
    if event.type ==1 and event.code == 304 and event.value == 1:
            print("X button is pressed. Stopping.")
            break
