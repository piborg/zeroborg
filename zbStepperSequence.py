#!/usr/bin/env python
# coding: latin-1

# Import library functions we need
import ZeroBorg
import time
import threading

# Power settings
voltageIn = 8.4                         # Total battery voltage to the ZeroBorg (change to 9V if using a non-rechargeable battery)
voltageOut = 3.0                        # Maximum stepper motor voltage when holding / turning

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

# Tell the system how to drive the stepper
sequence = [                            # Order for stepping 
        [+maxPower, +maxPower],
        [+maxPower, -maxPower],
        [-maxPower, -maxPower],
        [-maxPower, +maxPower]] 
stepDelay = 0.002                       # Delay between steps
stepsPerRotation = 360 / 1.8            # Steps required to fully rotate the motor

# Name the global variables
global ZB

# Setup the ZeroBorg
ZB = ZeroBorg.ZeroBorg()
#ZB.i2cAddress = 0x44                   # Uncomment and change the value if you have changed the board address
ZB.Init()
if not ZB.foundChip:
    boards = ZeroBorg.ScanForZeroBorg()
    if len(boards) == 0:
        print 'No ZeroBorg found, check you are attached :)'
    else:
        print 'No ZeroBorg at address %02X, but we did find boards:' % (ZB.i2cAddress)
        for board in boards:
            print '    %02X (%d)' % (board, board)
        print 'If you need to change the I²C address change the setup line so it is correct, e.g.'
        print 'ZB.i2cAddress = 0x%02X' % (boards[0])
    sys.exit()
#ZB.SetEpoIgnore(True)                 # Uncomment to disable EPO latch, needed if you do not have a switch / jumper
ZB.ResetEpo()

# Stepper movement thread
class StepperController(threading.Thread):
    def __init__(self, stepper):
        super(StepperController, self).__init__()
        self.startMove = threading.Event()
        self.endMove = threading.Event()
        self.startMove.clear()
        self.endMove.set()
        self.terminated = False
        self.count = 0
        self.speed = 1.0
        self.step = -1
        self.stepper = stepper
        self.start()

    # Function to perform a sequence of steps on one of the motor pairs at a speed
    def PerformMove(self, stepper, count, speed):
        global ZB

        # Choose direction based on sign (+/-)
        if count < 0:
            dir = -1
            count *= -1
        else:
            dir = 1

        # Work out the delay for the speed chosen
        if speed < 0:
            speed *= -1
        if speed > 1:
            speed = 1
        elif speed == 0:
            speed = 0.01
        timedDelay = stepDelay / speed

        # Loop through the steps
        while (count > 0) and (not self.terminated):
            # Set a starting position if this is the first move
            if self.step == -1:
                drive = sequence[-1]
                if stepper == 1:
                    ZB.SetMotor1(drive[0])
                    ZB.SetMotor2(drive[1])
                elif stepper == 2:
                    ZB.SetMotor3(drive[0])
                    ZB.SetMotor4(drive[1])
                self.step = 0
                time.sleep(timedDelay)
            else:
                self.step += dir

            # Wrap step when we reach the end of the sequence
            if self.step < 0:
                self.step = len(sequence) - 1
            elif self.step >= len(sequence):
                self.step = 0

            # For this step set the required drive values
            if self.step < len(sequence):
                drive = sequence[self.step]
                if stepper == 1:
                    ZB.SetMotor1(drive[0])
                    ZB.SetMotor2(drive[1])
                elif stepper == 2:
                    ZB.SetMotor3(drive[0])
                    ZB.SetMotor4(drive[1])
            time.sleep(timedDelay)
            count -= 1

    def StartMove(self, count, speed):
        self.count = count
        self.speed = speed
        self.startMove.set()
        self.endMove.clear()

    def WaitUntilComplete(self):
        while not self.terminated:
            # Wait for a move completion to be signalled
            if self.endMove.wait(1):
                # Done, return control
                return
            else:
                # No event seen, wait again
                pass

    def run(self):
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for a new move to be signalled
            if self.startMove.wait(1):
                # Run the movement
                self.startMove.clear()
                print '[START %d] %d @ %.0f %%' % (self.stepper, self.count, self.speed * 100)
                self.PerformMove(self.stepper, self.count, self.speed)
                print '[END %d] %d @ %.0f %%' % (self.stepper, self.count, self.speed * 100)
                self.endMove.set()
            else:
                # No event seen, wait again
                pass

# Start by turning all drives off
ZB.MotorsOff()

# Setup a thread for each stepper
leftStepper  = StepperController(1)      # Left stepper motor (M1 and M2)
rightStepper = StepperController(2)      # Right stepper motor (M3 and M4)

# Convenience function to wait for both steppers to finish
def WaitUntilComplete():
    leftStepper.WaitUntilComplete()
    rightStepper.WaitUntilComplete()

# Convenience function to convert rotations to steps
def StepsToMove(rotations):
    return int(stepsPerRotation * rotations)

try:
    # Loop forever
    while True:
        print '\n<< Drive the left motor only at half speed >>'
        leftStepper.StartMove(StepsToMove(5), 0.5)
        WaitUntilComplete()

        print '\n<< Drive the right motor only at half speed >>'
        rightStepper.StartMove(StepsToMove(5), 0.5)
        WaitUntilComplete()

        print '\n<< Drive both motors forward for 10 rotations at full speed >>'
        leftStepper.StartMove(StepsToMove(10), 1.0)
        rightStepper.StartMove(StepsToMove(10), 1.0)
        WaitUntilComplete()

        print '\n<< Drive both motors reverse for 10 rotations at full speed >>'
        leftStepper.StartMove(StepsToMove(-10), 1.0)
        rightStepper.StartMove(StepsToMove(-10), 1.0)
        WaitUntilComplete()

        print '\n<< Drive both motors forwards slowly for 2 rotations >>'
        leftStepper.StartMove(StepsToMove(-2), 0.2)
        rightStepper.StartMove(StepsToMove(-2), 0.2)
        WaitUntilComplete()

        print '\n<< Drive both motors at different speeds and directions >>'
        leftStepper.StartMove(StepsToMove(-4), 0.4)
        rightStepper.StartMove(StepsToMove(8), 0.8)
        WaitUntilComplete()
except KeyboardInterrupt:
    # CTRL+C exit, terminate the threads and turn off the drives
    leftStepper.terminated = True
    rightStepper.terminated = True
    leftStepper.join()
    rightStepper.join()
    ZB.MotorsOff()
    print 'Terminated'

