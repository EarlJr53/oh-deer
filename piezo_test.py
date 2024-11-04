import time
import board
import pwmio

piezo = pwmio.PWMOut(board.D5, duty_cycle=0, frequency=440, variable_frequency=True)

while True:
    for f in (440, 1000, 10000, 20000, 30000, 40000):
        piezo.frequency = f
        piezo.duty_cycle = 65535 // 2  # On 50%
        time.sleep(0.25)  # On for 1/4 second
        piezo.duty_cycle = 0  # Off
        time.sleep(0.05)  # Pause between notes
    time.sleep(0.5)
