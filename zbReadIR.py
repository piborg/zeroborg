#!/usr/bin/env python
# coding: latin-1

# Import library functions we need
import ZeroBorg
import time

# Setup the ZeroBorg
ZB = ZeroBorg.ZeroBorg()
#ZB.i2cAddress = 0x40                   # Uncomment and change the value if you have changed the board address
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

try:
    # Start by reading any existing messages to clear the new message flag
    ZB.GetIrMessage()
    ZB.SetLedIr(True)
    startTime = time.time()
    print 'Waiting for IR messages...'
    # Loop forever
    while True:
        # See if there is a new message
        if ZB.HasNewIrMessage():
            # Display the message and time
            messageData = ZB.GetIrMessage()
            messageTime = time.time() - startTime
            print '%.3fs received %s' % (messageTime, messageData)
        # Wait a while before checking again
        time.sleep(0.1)
except KeyboardInterrupt:
    # CTRL+C exit
    ZB.SetLedIr(False)
    print 'Terminated'

