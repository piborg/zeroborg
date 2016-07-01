# ZeroBorg
API and examples for using ZeroBorg.
![](zeroborg.jpg?raw=true)
![](mecanum-robot.jpg?raw=true)

This repository contains the API for controlling ZeroBorg from Python.
There are examples for all of the various features of the ZeroBorg:
* Driving DC motors
* Driving stepper motors
* Reading IR remote buttons
* Reading analog inputs

[You can find out more about ZeroBorg here](https://www.piborg.org/zeroborg)

## Downloading the code
To get the code we will clone this repository to the Raspberry Pi.
In a terminal run the following commands
```bash
cd ~
sudo apt-get -y install git
git clone https://github.com/piborg/zeroborg.git
cd zeroborg
chmod +x *.sh
./install.sh
```
After the installer has completed you may need to restart the Raspberry Pi.
If you have the GUI setup there should be a shortcut to the demo GUI on the desktop.

## The API - ZeroBorg.py
This script provides the various functions used by all of the other examples.
It does all of the I2C handling so that you can concentrate on controlling your robot :)

At its simplest you can setup the ZeroBorg using these commands in your Python script:
```python
import ZeroBorg
ZB = ZeroBorg.ZeroBorg()
ZB.Init()
ZB.ResetEpo()
```

You can then control motors with:
```python
ZB.SetMotor1(x)
ZB.SetMotor2(x)
ZB.SetMotor3(x)
ZB.SetMotor4(x)
ZB.MotorsOff()
```
where `x` is a value between `1.0` (full forward) and `-1.0` (full reverse), use `0.0` for off.

You can read the IR sensor for messages using:
```python
if ZB.HasNewIrMessage():
    x = ZB.GetIrMessage()
else:
    x = ""
```
`x` will contain a string sequence such as `"FAD6DAD5"` which represents the held button on the remote.

You can read the analog pins using:
```python
x = ZB.GetAnalog1()
x = ZB.GetAnalog2()
```
`x` will contain the voltage seen on the pin, a value between `0.0` and `3.3`.

To get a full list of functions use this Python code:
```python
import ZeroBorg
ZB = ZeroBorg.ZeroBorg()
ZB.Help()
```
You can use SHIFT + PAGE UP and SHIFT + PAGE DOWN to scroll the terminal output to view all of the commands

## The GUI - zbGui.py
![](zeroborg-gui.png?raw=true)

Can be run from the shortcut on the desktop or using
```bash
cd ~/zeroborg
./zbGui.py
```

The GUI shows off all the basic functions of the ZeroBorg:
* The sliders control the motors individually
* The button turns all of the motors off
* The two green values are the analog pin readings
* The red status displays the currently held button and code, or the last button it saw

The button name decoding comes from the codes provided by `zbIrButtonMap.py`.

## Joystick motor control - zbJoystick.py and zbMecanumJoy.py
These scripts use a joystick input and drive a set of robot wheels.
They can be run using
```bash
cd ~/zeroborg
./runJoystick.sh
```
and
```bash
cd ~/zeroborg
./runMecanumJoy.sh
```

These examples are setup for a 4Borg and should be wired as follows:
* Front left wheel → Motor 1
* Rear left wheel → Motor 2
* Front right wheel → Motor 3
* Rear right wheel → Motor 4

The mecanum wheel script is the same one we used in the Kickstarter video and on our stand at the 4th Raspberry Pi Birthday Party.

## Stepper motor control - zbStepper.py and zbStepperSequence.py
These scripts drive stepper motors and can be run using
```bash
cd ~/zeroborg
./zbStepper.py
```
and
```bash
cd ~/zeroborg
./zbStepperSequence.py
```

`zbStepper.py` drives a single four wire stepper attached to motor outputs 1 and 2.
The script asks how many steps to make and then rotates the stepper as fast as it has been allowed to.

`zbStepperSequence.py` drives two four wire steppers attached to:
1. Motor outputs 1 and 2
2. Motor outputs 3 and 4
The script runs a set pattern of movements at different speeds.

## Reading remote signals - zbReadIR.py and zbSaveIR.py
These scripts show how the IR remote sensor can be read and programmed
They can be run using
```bash
cd ~/zeroborg
./zbReadIR.py
```
and
```bash
cd ~/zeroborg
./zbSaveIR.py
```

`zbReadIR.py` waits for a remote button press and then displays the raw code set as a hexadecimal string.
You can use that same string to check what button has been pressed.

`zbSaveIR.py` allows you to create named constants for the buttons on your remote.
It works by the following sequence:

1. Run the script
2. Hold the button you wish to name (keep holding)
3. Type the name for this button and press ENTER
4. Wait for the script to display the code, then release the button
5. Keep repeating from 2 until you have named all of the buttons you want to
6. Press ENTER without typing a name to finish

The names are saved into the `zbIrButtonMap.py` script like this:
```python
IR_info = "FAD6DAD5"
IR_power = "FB5AD5AA"
IR_wide = "FB5B6D56AD"
```
In order to use the names in your own script you can then check the value from `GetIrMessage` like this:
```python
import zbIrButtonMap.py as Buttons
# ...
if ZB.HasNewIrMessage():
    irCode = ZB.GetIrMessage()
else:
    # No button held, GetIrMessage would give the last button that was pressed instead
    irCode = ""
if irCode == Buttons.IR_info:
    print "Info button pressed"
elif irCode == Buttons.IR_power:
    print "Power button pressed"
elif irCode == "":
    print "No button pressed"
else:
    print "Some other button pressed, code: " + irCode
```

There are some examples already for different remotes:
* `zbIrMapBN59_01015A.py` → Samsung TV remote
* `zbIrMapRM_ED009.py` → Sony TV remote
* `zbIrMapRMT_VB100L.py` → Sony Netflix remote

## Controlling a robot with a remote control - zbRemote.py
This script is exactly like the joystick example, but using a TV remote :)
Can be run using
```bash
cd ~/zeroborg
./zbRemote.py
```

The standard example allows control from a Samsung or Sony TV remote with these controls:
* Move forward: UP or 2
* Move backward: DOWN or 8
* Spin left: LEFT or 4
* Spin right: RIGHT or 6
* Stop (normally not needed): SELECT, 5, PAUSE, or STOP
* Shutdown the RPi: POWER

The controls can be changed by editing the `buttonCommands` dictionary using the IR constants or string codes.
When no button is pressed the robot will stop, meaning he should also stop if he gets out of range.

## Reading the analog pins - zbReadAnalog.py
This script displays the two analog readings in volts.
Can be run using
```bash
cd ~/zeroborg
./zbReadAnalog.py
```

When nothing is connected to the pins they should read almost `0.00 V`, we usually see readings up-to `0.06 V` in this case.
