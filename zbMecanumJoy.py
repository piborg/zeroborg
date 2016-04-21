#!/usr/bin/env python
# coding: Latin-1

# Load library functions we want
import time
import os
import sys
import math
import pygame
import ZeroBorg

# Re-direct our output to standard error, we need to ignore standard out to hide some nasty print statements from pygame
sys.stdout = sys.stderr

# Setup the ZeroBorg
ZB = ZeroBorg.ZeroBorg()
#ZB.i2cAddress = 0x44                  # Uncomment and change the value if you have changed the board address
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
# Ensure the communications failsafe has been enabled!
failsafe = False
for i in range(5):
    ZB.SetCommsFailsafe(True)
    failsafe = ZB.GetCommsFailsafe()
    if failsafe:
        break
if not failsafe:
    print 'Board %02X failed to report in failsafe mode!' % (ZB.i2cAddress)
    sys.exit()
ZB.ResetEpo()

# Settings for the joystick
axisUpDown = 1                          # Joystick axis to read for forward / backward movement
axisUpDownInverted = False              # Set this to True if forward and backward appear to be swapped
axisLeftRight = 0                       # Joystick axis to read for left / right strafing
axisLeftRightInverted = False           # Set this to True if left and right strafing appears to be swapped
axisRotate = 2                          # Joystick axis to read for rotation position
axisRotateInverted = False              # Set this to True if rotation appears to be swapped
buttonResetEpo = 3                      # Joystick button number to perform an EPO reset (Start)
buttonSlow = 8                          # Joystick button number for driving slowly whilst held (L2)
slowFactor = 0.5                        # Speed to slow to when the drive slowly button is held, e.g. 0.5 would be half speed
interval = 0.00                         # Time between updates in seconds, smaller responds faster but uses more processor time

# Power settings
voltageIn = 8.4                         # Total battery voltage to the ZeroBorg
voltageOut = 6.0                        # Maximum motor voltage

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

# Setup pygame and wait for the joystick to become available
ZB.MotorsOff()
os.environ["SDL_VIDEODRIVER"] = "dummy" # Removes the need to have a GUI window
pygame.init()
#pygame.display.set_mode((1,1))
print 'Waiting for joystick... (press CTRL+C to abort)'
while True:
    try:
        try:
            pygame.joystick.init()
            # Attempt to setup the joystick
            if pygame.joystick.get_count() < 1:
                # No joystick attached, toggle the LED
                ZB.SetLed(not ZB.GetLed())
                pygame.joystick.quit()
                time.sleep(0.1)
            else:
                # We have a joystick, attempt to initialise it!
                joystick = pygame.joystick.Joystick(0)
                break
        except pygame.error:
            # Failed to connect to the joystick, toggle the LED
            ZB.SetLed(not ZB.GetLed())
            pygame.joystick.quit()
            time.sleep(0.1)
    except KeyboardInterrupt:
        # CTRL+C exit, give up
        print '\nUser aborted'
        ZB.SetLed(True)
        sys.exit()
print 'Joystick found'
joystick.init()
ZB.SetLed(False)

try:
    print 'Press CTRL+C to quit'
    driveFL = 0.0
    driveFR = 0.0
    driveRL = 0.0
    driveRR = 0.0
    driveGain = math.sqrt(2) # This is the correction so that 100% forward is actually 100%
    running = True
    hadEvent = False
    upDown = 0.0
    leftRight = 0.0
    # Loop indefinitely
    while running:
        # Get the latest events from the system
        hadEvent = False
        events = pygame.event.get()
        # Handle each event individually
        for event in events:
            if event.type == pygame.QUIT:
                # User exit
                running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                # A button on the joystick just got pushed down
                hadEvent = True
            elif event.type == pygame.JOYAXISMOTION:
                # A joystick has been moved
                hadEvent = True
            if hadEvent:
                # Read axis positions (-1 to +1)
                if axisUpDownInverted:
                    upDown = joystick.get_axis(axisUpDown)
                else:
                    upDown = -joystick.get_axis(axisUpDown)
                if axisLeftRightInverted:
                    leftRight = -joystick.get_axis(axisLeftRight)
                else:
                    leftRight = joystick.get_axis(axisLeftRight)
                if axisRotateInverted:
                    rotate = -joystick.get_axis(axisRotate)
                else:
                    rotate = joystick.get_axis(axisRotate)
                # Allow a central 'off' for each axis
                if abs(upDown) < 0.05:
                    upDown = 0.0
                if abs(leftRight) < 0.05:
                    leftRight = 0.0
                if abs(rotate) < 0.05:
                    rotate = 0.0
                # Work out the speed and angle of the strafing
                strafeSpeed = math.sqrt(upDown ** 2 + leftRight ** 2) * driveGain
                strafeAngle = math.atan2(leftRight, upDown)
                # Determine the four drive power levels
                offsetAngle = strafeAngle + (math.pi / 4)
                driveFL = strafeSpeed * math.sin(offsetAngle) + rotate
                driveFR = strafeSpeed * math.cos(offsetAngle) - rotate
                driveRL = strafeSpeed * math.cos(offsetAngle) + rotate
                driveRR = strafeSpeed * math.sin(offsetAngle) - rotate
                # Scale the drive power if any exceed 100%
                driveMax = max(abs(driveFL), abs(driveFR), abs(driveRL), abs(driveRR))
                if driveMax > 1.0:
                    driveFL /= driveMax
                    driveFR /= driveMax
                    driveRL /= driveMax
                    driveRR /= driveMax
                # Check for button presses
                if joystick.get_button(buttonResetEpo):
                    ZB.ResetEpo()
                if joystick.get_button(buttonSlow):
                    driveFL *= slowFactor
                    driveFR *= slowFactor
                    driveRL *= slowFactor
                    driveRR *= slowFactor
                # Set the motors to the new speeds
                ZB.SetMotor1(-driveFL * maxPower)
                ZB.SetMotor2(-driveRL * maxPower)
                ZB.SetMotor3(+driveFR * maxPower)
                ZB.SetMotor4(+driveRR * maxPower)
        # Change the LED to reflect the status of the EPO latch
        ZB.SetLed(ZB.GetEpo())
        # Wait for the interval period
        time.sleep(interval)
    # Disable all drives
    ZB.MotorsOff()
except KeyboardInterrupt:
    # CTRL+C exit, disable all drives
    ZB.MotorsOff()
print
