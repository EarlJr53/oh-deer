

"""Helper functions for servo, ultrasonic deterrent, and light deterrent"""
import time
import board
import pwmio
from adafruit_servokit import ServoKit
from simple_pid import PID
import random

ideal_pos = 40 # I think since we're 80 pixels wide, we are aiming for roughly pixel 40 as the middle
Kp = .1
Ki = .01
Kd = .01


class Servo():
    def __init__(self, pid_enable=True, setpoint=ideal_pos, p=Kp, i=Ki, d=Kd, ):
        """_summary_

        Args:
            p (_type_, optional): _description_. Defaults to Kp.
            i (_type_, optional): _description_. Defaults to Ki.
            d (_type_, optional): _description_. Defaults to Kd.
            setpoint (_type_, optional): _description_. Defaults to ideal_pos.
        """
        if pid_enable:
            self.pid = PID(p, i, d, setpoint=setpoint, output_limits=(50, 180))
        self.pid_enable = pid_enable
        self.setpoint = setpoint
        self.bonnet = ServoKit(channels=16)
        self.off()

    def off(self):
        """Set servo to off"""
        self.bonnet.servo[0].angle = None
        print("Servo Off")

    def idle(self):
        """Set servo to slowly spin at a continuous speed"""
        self.bonnet.servo[0].angle = 90
        print("idle")

    def track(self, target):
        """Adjust servo speed using PID to track deer.

        Args:
            target (float): Position of target to align with
        """
        if self.pid_enable:
            error = target - self.pid.setpoint
            update = self.pid(error)
        else:
            if target > self.setpoint:
                update = 150
            elif target < self.setpoint:
                update = 80
        self.bonnet.servo[0].angle = update
        print(f"Target: {target}, Speed updated to: {update}")

class Ultrasonic(pwmio.PWMOut):
    def __init__(self, frequency = 20000, base_power = 50):
        super().__init__(board.D5, duty_cycle=0, frequency=frequency, variable_frequency=True)
        self.base_power = base_power

    def set_power(self, power=50):
        """Set ultrasonic emitter power to a given percentage

        Args:
            power (int, optional): Percentage to set emitter power to. Defaults to 50.
        """
        if self.base_power == 0:
            self.duty_cycle = 0
            print("Ultrasonic Activated")
        else:
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
