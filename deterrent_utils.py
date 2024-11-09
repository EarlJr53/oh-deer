

"""Helper functions for servo, ultrasonic deterrent, and light deterrent"""
import time
import board
import pwmio
from adafruit_servokit import ServoKit
from simple_pid import PID
import random

ideal_pos = 40 # I think since we're 80 pixels wide, we are aiming for roughly pixel 40 as the middle
Kp = 1
Ki = 0
Kd = 0    


class Servo():
    def __init__(self, p=Kp, i=Ki, d=Kd, setpoint=ideal_pos):
        """_summary_

        Args:
            p (_type_, optional): _description_. Defaults to Kp.
            i (_type_, optional): _description_. Defaults to Ki.
            d (_type_, optional): _description_. Defaults to Kd.
            setpoint (_type_, optional): _description_. Defaults to ideal_pos.
        """
        self.pid = PID(p, i, d, setpoint=setpoint, output_limits=(-1, 1))
        self.bonnet = ServoKit(channels=16)
        self.off()

    def off(self):
        """Set servo to off"""
        self.bonnet.continuous_servo[0].throttle = 0

    def idle(self):
        """Set servo to slowly spin at a continuous speed"""
        self.bonnet.continuous_servo[0].throttle = 0.1
    
    def track(self, target):
        """Adjust servo speed using PID to track deer.

        Args:
            target (float): Position of target to align with
        """
        error = target - self.pid.setpoint
        update = self.pid(error)
        self.bonnet.continuous_servo[0].throttle = update
        print("Speed updated to: " + update)

class Ultrasonic(pwmio.PWMOut):
    def __init__(self, frequency = 20000, base_power = 50):
        super().__init__(board.D5, duty_cycle=0, frequency=frequency, variable_frequency=True)
        self.base_power = base_power

    def set_power(self, power=50):
        """Set ultrasonic emitter power to a given percentage

        Args:
            power (int, optional): Percentage to set emitter power to. Defaults to 50.
        """
        self.duty_cycle = 65535 // (100/power)

    def off(self):
        """Set ultrasonic emitter to off (duty cycle 0)"""
        self.duty_cycle = 0

    def random(self):
        """Randomly beep in annoying patterns. Rudimentary version"""
        rand = random.randint(1, 10)
        if rand > 5:
            self.set_power(self.base_power)
        else:
            self.off()
