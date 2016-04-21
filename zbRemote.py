#!/usr/bin/env python
# coding: Latin-1

# Load library functions we want
import time
import os
import zbIrButtonMap as Buttons
import ZeroBorg

# Setup the ZeroBorg
ZB = ZeroBorg.ZeroBorg()
#ZB.i2cAddress = 0x40                  # Uncomment and change the value if you have changed the board address
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
ZB.SetCommsFailsafe(False)
ZB.ResetEpo()

# Power settings
voltageIn = 8.4                         # Total battery voltage to the ZeroBorg (change to 9V if using a non-rechargeable battery)
voltageOut = 6.0                        # Maximum motor voltage

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

# Remote control commands
def Move(left, right):
    print '%0.2f | %0.2f' % (left, right)
    ZB.SetMotor1(-left * maxPower)
    ZB.SetMotor2(-left * maxPower)
    ZB.SetMotor3(right * maxPower)
    ZB.SetMotor4(right * maxPower)  

def MoveForward():
    Move(+1.0, +1.0)

def MoveBackward():
    Move(-1.0, -1.0)

def SpinLeft():
    Move(-1.0, +1.0)

def SpinRight():
    Move(+1.0, -1.0)

def Stop():
    Move(0.0, 0.0)

def Shutdown():
    global running
    running = False

# Settings for the remote control
buttonCommands = {                      # A list of all the allowed buttons and their corresponding movement settings
    Buttons.SONY_TV.IR_power:           Shutdown,
    Buttons.SONY_TV.IR_up:              MoveForward,
    Buttons.SONY_TV.IR_left:            SpinLeft,
    Buttons.SONY_TV.IR_right:           SpinRight,
    Buttons.SONY_TV.IR_down:            MoveBackward,
    Buttons.SONY_TV.IR_select:          Stop,
    Buttons.SONY_TV.IR_2:               MoveForward,
    Buttons.SONY_TV.IR_4:               SpinLeft,
    Buttons.SONY_TV.IR_5:               Stop,
    Buttons.SONY_TV.IR_6:               SpinRight,
    Buttons.SONY_TV.IR_8:               MoveBackward,
    Buttons.SONY_NETFLIX.IR_tv_power:   Shutdown,
    Buttons.SONY_NETFLIX.IR_power:      Shutdown,
    Buttons.SONY_NETFLIX.IR_up:         MoveForward,
    Buttons.SONY_NETFLIX.IR_left:       SpinLeft,
    Buttons.SONY_NETFLIX.IR_right:      SpinRight,
    Buttons.SONY_NETFLIX.IR_down:       MoveBackward,
    Buttons.SONY_NETFLIX.IR_select:     Stop,
    Buttons.SONY_NETFLIX.IR_pause:      Stop,
    Buttons.SONY_NETFLIX.IR_stop:       Stop,
    Buttons.SAMSUNG_TV.IR_power:        Shutdown,
    Buttons.SAMSUNG_TV.IR_2:            MoveForward,
    Buttons.SAMSUNG_TV.IR_4:            SpinLeft,
    Buttons.SAMSUNG_TV.IR_5:            Stop,
    Buttons.SAMSUNG_TV.IR_6:            SpinRight,
    Buttons.SAMSUNG_TV.IR_8:            MoveBackward,
    Buttons.SAMSUNG_TV.IR_up:           MoveForward,
    Buttons.SAMSUNG_TV.IR_left:         SpinLeft,
    Buttons.SAMSUNG_TV.IR_right:        SpinRight,
    Buttons.SAMSUNG_TV.IR_down:         MoveBackward,
    Buttons.SAMSUNG_TV.IR_select:       Stop,
    Buttons.SAMSUNG_TV.IR_pause:        Stop,
    Buttons.SAMSUNG_TV.IR_stop:         Stop,
}
interval = 0.10                         # Time between updates in seconds, smaller responds faster but uses more processor time
holdToMove = True                       # If True the remote button has to be held. False means it does not

# Hold the LED on for a couple of seconds to indicate we are ready
ZB.SetLedIr(False)
ZB.SetLed(True)
time.sleep(2.0)
ZB.SetLed(False)

# The remote decoding loop
global running
running = True
ZB.SetLedIr(True)
try:
    print 'Press CTRL+C to quit'
    print 'Press the power button on the remote to shutdown the Raspberry Pi'
    # Loop indefinitely
    while running:
        # See if there is a button held
        if ZB.HasNewIrMessage():
            # A button is pressed, see what it is:
            pressedButtonCode = ZB.GetIrMessage()
            if buttonCommands.has_key(pressedButtonCode):
                # We know this code, run the command
                buttonCommands[pressedButtonCode]()
            else:
                # We do not know this button, we will ignore it
                pass
        else:
            # No button is pressed, stop if we expect them to be held
            if holdToMove:
                Stop()
        # Wait for the interval period
        time.sleep(interval)
    # Disable all drives
    ZB.MotorsOff()
    # Shutdown the Raspberry Pi
    os.system("sudo halt")
except KeyboardInterrupt:
    # CTRL+C exit, disable all drives
    ZB.MotorsOff()
print
