from deterrent_utils import Servo, Ultrasonic
from thermal_utils import Thermal
import time


def main():
    try:
        lock = False  # Whether the device has detected a deer
        start_time = time.time()  # time at last detection
        dwell_time = 0  # number of seconds since last detection
        max_dwell = 20  # max time to wait since last detection before sleep

        servo = Servo(pid_enable=False)
        ultrasonic = Ultrasonic()
        thermal = Thermal()

        while lock or (dwell_time < max_dwell):

            # Call thermal camera object to see if there is a deer in the frame
            # Return in the form (lock, target)
            # Where lock is boolean expressing whether there is a deer
            # and target is an integer for the horizotal pixel that aligns with the deer

            lock, target = thermal.detect()  # it should look like this
            # target = 40                         # temporary until the thermal camera is integrated

            if lock:
                servo.track(target)
                # ultrasonic.random()
                start_time = time.time()
                print(target)

            else:
                ultrasonic.off()
                # servo.idle()
                servo.off()
                print("Idle")

            dwell_time = time.time() - start_time

    except KeyboardInterrupt:
        print("\nExited by user")
        ultrasonic.off()
        servo.off()
        thermal.off()

    finally:
        print("\nExited program")
  #      ultrasonic.off()
   #     servo.off()
    #    thermal.off()


main()
