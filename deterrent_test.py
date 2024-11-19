from deterrent_utils import Servo, Ultrasonic
import time
import random

lock = False        # Whether the device has detected a deer
start_time = time.time() # time at last detection
dwell_time = 0      # number of seconds since last detection
max_dwell = 10     # max time to wait since last detection before sleep

servo = Servo(pid_enable = False)
ultrasonic = Ultrasonic(10000, 0)
# thermal = Thermal()

lock = False
target = 40

while (dwell_time < max_dwell):

    # Call thermal camera object to see if there is a deer in the frame
    # Return in the form (lock, target)
    # Where lock is boolean expressing whether there is a deer
    # and target is an integer for the horizotal pixel that aligns with the deer

    # lock, target = thermal.detect()   # it should look like this
    # target = 40                         # temporary until the thermal camera is integrated
    #target = input()
    #if target == -1: lock = False
    #else: lock = True
    #rand = random.randint(1, 80)
    if target == 40:
        lock = False
        target = random.randint(1, 80)
    else:
        if target < 43 and target > 37:
            lock = True
        else:
            lock = False

        if target > 40:
            target -= 1
        elif target < 40:
            target += 1

    if lock:
        servo.track(target)
        ultrasonic.random()
        #start_time = time.time()

        # temporary
        #if (time.time() - start_time) > 5:
           # lock = False
    else:
        ultrasonic.off()
#        servo.idle()


    dwell_time = time.time() - start_time
#    print(dwell_time)

ultrasonic.off()
servo.off()
# thermal.off()
