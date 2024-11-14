"""Simple test for a standard servo on channel 0 and a continuous rotation servo on channel 1."""
import time
from adafruit_servokit import ServoKit

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
kit = ServoKit(channels=16)

kit.servo[0].angle = 0
#kit.continuous_servo[0].throttle = 1
#kit.servo[0].angle = 0
time.sleep(1)
#kit.continuous_servo[0].throttle = -1
kit.servo[0].angle = 180
time.sleep(1)
kit.servo[0].angle = 0
time.sleep(1)
#kit.continuous_servo[0].throttle = 0
#kit.continuous_servo[0].throttle
kit.servo[0].angle = 90
time.sleep(1)
kit.servo[0].angle = None
#kit.continuous_servo[0].angle = None
#kit.setPWM(0, 0, 300);
#kit.continuous_servo[0].throttle
#print(kit.continuous_servo[0].throttle)
