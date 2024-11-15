from deterrent_utils import Servo, Ultrasonic
import time
import random

lock = False        # Whether the device has detected a deer
start_time = time.time() # time at last detection
dwell_time = 0      # number of seconds since last detection
max_dwell = 10     # max time to wait since last detection before sleep

servo = Servo()
ultrasonic = Ultrasonic(10000, 0)
# thermal = Thermal()

lock = True
target = 50

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
    rand = random.randint(20, 60)
    if rand % 5 == 1:
        lock = True
        target = rand
    else:
        lock = False

    if lock:
        servo.track(target)
        ultrasonic.random()
        #start_time = time.time()

        # temporary
        #if (time.time() - start_time) > 5:
           # lock = False
    else:
        ultrasonic.off()
        servo.idle()


    dwell_time = time.time() - start_time
    print(dwell_time)

ultrasonic.off()
servo.off()
# thermal.off()
