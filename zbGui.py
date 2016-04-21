#!/usr/bin/env python
# coding: latin-1

# Import library functions we need 
import ZeroBorg
import zbIrButtonMap as Buttons
import Tkinter

# Setup the ZeroBorg
global ZB
ZB = ZeroBorg.ZeroBorg()            # Create a new ZeroBorg object
ZB.Init()                           # Set the board up (checks the board is connected)
ZB.ResetEpo()                       # Reset the stop switch (EPO) state
                                    # if you do not have a switch across the two pin header then fit the jumper
ZB.SetLedIr(True)                   # Set the LED to flash when an infrared signal is present

# Build a button to name mapping
buttonMap = {}
possibleButtons = Buttons.__dict__.keys()
possibleButtons.sort()
for buttonName in possibleButtons:
    if buttonName.startswith('IR_'):
        code = Buttons.__dict__[buttonName]
        name = buttonName[3:]
        buttonMap[code] = name

# Class representing the GUI dialog
class ZeroBorg_tk(Tkinter.Tk):
    # Constructor (called when the object is first created)
    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.protocol("WM_DELETE_WINDOW", self.OnExit) # Call the OnExit function when user closes the dialog
        self.Initialise()

    # Initialise the dialog
    def Initialise(self):
        global ZB
        self.title('ZeroBorg Example GUI')
        # Setup a grid of 4 sliders which command each motor output
        self.grid()
        self.sld1 = Tkinter.Scale(self, from_ = +100, to = -100, orient = Tkinter.VERTICAL, command = self.sld1_move)
        self.sld1.set(0)
        self.sld1.grid(column = 0, row = 0, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.sld2 = Tkinter.Scale(self, from_ = +100, to = -100, orient = Tkinter.VERTICAL, command = self.sld2_move)
        self.sld2.set(0)
        self.sld2.grid(column = 1, row = 0, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.sld3 = Tkinter.Scale(self, from_ = +100, to = -100, orient = Tkinter.VERTICAL, command = self.sld3_move)
        self.sld3.set(0)
        self.sld3.grid(column = 2, row = 0, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        self.sld4 = Tkinter.Scale(self, from_ = +100, to = -100, orient = Tkinter.VERTICAL, command = self.sld4_move)
        self.sld4.set(0)
        self.sld4.grid(column = 3, row = 0, rowspan = 1, columnspan = 1, sticky = 'NSEW')
        # Setup a stop button for all motors
        self.butOff = Tkinter.Button(self, text = 'All Off', command = self.butOff_click)
        self.butOff['font'] = ("Arial", 20, "bold")
        self.butOff.grid(column = 0, row = 1, rowspan = 1, columnspan = 4, sticky = 'NSEW')
        # Add a display for the analog levels
        self.lblAnalog1 = Tkinter.Label(self, text = '?.?? V', justify = Tkinter.CENTER, bg = '#000', fg = '#0F0')
        self.lblAnalog1['font'] = ('Trebuchet', 20, 'bold')
        self.lblAnalog1.grid(column = 0, row = 2, rowspan = 1, columnspan = 2, sticky = 'NSEW')
        self.lblAnalog2 = Tkinter.Label(self, text = '?.?? V', justify = Tkinter.CENTER, bg = '#000', fg = '#0F0')
        self.lblAnalog2['font'] = ('Trebuchet', 20, 'bold')
        self.lblAnalog2.grid(column = 2, row = 2, rowspan = 1, columnspan = 2, sticky = 'NSEW')
        # Add a display for the IR input
        self.lblIR = Tkinter.Label(self, text = 'No IR', justify = Tkinter.CENTER, bg = '#000', fg = '#F00')
        self.lblIR['font'] = ('Trebuchet', 20, 'bold')
        self.lblIR.grid(column = 0, row = 3, rowspan = 1, columnspan = 4, sticky = 'NSEW')
        # Setup the grid scaling
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)
        self.grid_columnconfigure(3, weight = 1)
        self.grid_rowconfigure(0, weight = 8)
        self.grid_rowconfigure(1, weight = 2)
        self.grid_rowconfigure(2, weight = 1)
        self.grid_rowconfigure(3, weight = 2)
        # Set the size of the dialog
        self.resizable(True, True)
        self.geometry('600x600')
        # Setup the initial motor state
        ZB.MotorsOff()
        # Start polling for readings
        ZB.GetIrMessage()
        self.lastIR = '-none-'
        self.lastButton = '-none-'
        self.after(1, self.Poll)

    # Polling function
    def Poll(self):
        if ZB.HasNewIrMessage():
            self.lastIR = ZB.GetIrMessage()
            if buttonMap.has_key(self.lastIR):
                self.lastButton = buttonMap[self.lastIR]
            else:
                self.lastButton = self.lastIR
            self.lblIR['text'] = 'IR: %s\nCode: %s' % (self.lastButton, self.lastIR)
        else:
            self.lblIR['text'] = 'No IR\nLast: %s' % (self.lastButton)
        analog1 = ZB.GetAnalog1()
        analog2 = ZB.GetAnalog2()
        self.lblAnalog1['text'] = '%01.2f V' % (analog1)
        self.lblAnalog2['text'] = '%01.2f V' % (analog2)

        # Re-run the poll after 100 ms
        self.after(100, self.Poll)

    # Called when the user closes the dialog
    def OnExit(self):
        global ZB
        # Turn drives off and end the program
        ZB.MotorsOff()
        self.quit()
  
    # Called when sld1 is moved
    def sld1_move(self, value):
        global ZB
        ZB.SetMotor1(float(value) / 100.0)

    # Called when sld2 is moved
    def sld2_move(self, value):
        global ZB
        ZB.SetMotor2(float(value) / 100.0)

    # Called when sld3 is moved
    def sld3_move(self, value):
        global ZB
        ZB.SetMotor3(float(value) / 100.0)

    # Called when sld4 is moved
    def sld4_move(self, value):
        global ZB
        ZB.SetMotor4(float(value) / 100.0)

    # Called when butOff is clicked
    def butOff_click(self):
        global ZB
        ZB.MotorsOff()
        self.sld1.set(0)
        self.sld2.set(0)
        self.sld3.set(0)
        self.sld4.set(0)

# if we are the main program (python was passed a script) load the dialog automatically
if __name__ == "__main__":
    app = ZeroBorg_tk(None)
    app.mainloop()

