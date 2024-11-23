"""Simple test for a standard servo on channel 0 and a continuous rotation servo on channel 1."""
import time
from adafruit_servokit import ServoKit

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
kit = ServoKit(channels=16)

x = 0
#while x <= 180:
#    kit.servo[0].angle = x
#    time.sleep(1)
#    print(x)
#    x += 5

kit.servo[0].angle = None

# kit.servo[0].angle = 0
kit.continuous_servo[0].throttle = 1
#time.sleep(1)
#kit.continuous_servo[0].throttle = -1
# kit.servo[0].angle = 180
#time.sleep(1)
# kit.servo[0].angle = 0
# time.sleep(1)
#kit.continuous_servo[0].throttle = 0
# kit.servo[0].angle = 90
# time.sleep(1)
# kit.servo[0].angle = None
