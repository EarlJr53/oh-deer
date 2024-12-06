from deterrent_utils import Servo, Ultrasonic
from thermal_utils import Thermal
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def main():
    now = datetime.now()
    filename = now.strftime("/home/ohdeer/oh-deer/logs/%Y-%m-%d.log")
    logging.basicConfig(
        filename=filename,
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    try:
        lock = False                # Whether the device has detected a deer
        start_time = time.time()    # time at last detection
        dwell_time = 0              # number of seconds since last detection
        max_wait = 3                # time to wait before spinning after seeing a target
        max_spin = 20               # time to spin after last detection before sleeping
        max_sleep = 120             # time to wait before waking from sleep

        servo = Servo(pid_enable=False)
        # ultrasonic = Ultrasonic()
        thermal = Thermal()

        logger.info('Program started')

        # while lock or (dwell_time < max_dwell):
        while True:

            # Call thermal camera object to see if there is a deer in the frame
            # Return in the form (lock, target)
            # Where lock is boolean expressing whether there is a deer
            # and target is an integer for the horizotal pixel that aligns with the deer

            lastlock = lock
            lock, target = thermal.detect()

            if lock:                        # lock onto target
                if not lastlock: logger.info(f"Lock acquired on target at {target}")
                servo.track(target)
                # ultrasonic.random()
                start_time = time.time()
                print(target)

            else:
                if lastlock: logger.info(f"Lock lost")

                if dwell_time < max_wait:       # briefly wait for target to reappear
                    # ultrasonic.off()
                    servo.off()
                    print("Waiting for Target")

                elif dwell_time < max_spin:     # spin to reacquire target
                    # ultrasonic.off()
                    servo.idle()
                    print("Idle Spin")

                elif dwell_time < max_sleep:    # enter sleep mode
                    # ultrasonic.off()
                    servo.off()
                    print("Sleep")

                else:                           # awaken from sleep
                    start_time = time.time()    # no target, but restart scan cycle
                    servo.off()

            dwell_time = time.time() - start_time

    except KeyboardInterrupt:
        logger.exception("Program exited by user", KeyboardInterrupt)
        # print("\nExited by user")
        #ultrasonic.off()
        servo.off()
        thermal.off()

    finally:
        logger.info("Execution ended")
        # print("\nExited program")
  #      ultrasonic.off()
        servo.off()
        thermal.off()

if __name__ == '__main__':
    main()
