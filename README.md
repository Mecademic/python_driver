# Mecademic Python API

A python module designed for Robot products from Mecademic. The module offers tools that give access to all the features of the Mecademic Robots such as MoveLin and MoveJoints. The module can be started from a terminal or a python application and controls the Mecademic Products. 

## Getting Started

These instructions will allow you to control the Meca500 from Mecademic through a python script and how to use the module for development and deployment purposes.

## Prerequisites

To be able to use the module with unexpected errors, the user must have a copy of python installed on their machine and is recommended to use python version 3.6 or higher. [Python](https://www.python.org/) can be installed from its main website (a reboot will be require after the installation to complete the setup). 

## Running a Meca500 with the module

To run a Meca500 with the Meca500.py module, two options present itself: interactive terminal or runnable script.

To use the Meca500.py in an interactive terminal, the python file must be started with the -i modifier in a terminal as follows:

```
C:Users\admin> python -i <file-path>/Meca500.py
```
Or
```
C:<file-path>> python -i Meca500.py
```

This will open a python terminal with the module already imported. From there you need to connect to the Meca500 before being able to perform actions. This is done by making an instance of the class Meca500 by passing the IP Address of the Meca500 as an argument and using the function Connect():
```
>> meca = Meca500.Meca500('192.168.0.100')
>> meca.Connect()
```

Once succesfully connected to the Meca500, you are able to start performing actions. To get it ready for operations, it must be activated and homed or it will fall in error. To do so, the following functions are run:

```
>> meca.Activate()
>> meca.Home()
```

The Meca500 is now ready to perform operations. The user programming manual or the documentation in the module is sufficiant to be able to make the Meca500 perform actions and control the robot. When done with the Meca500 and want to turn it off, it must first be deactivated and disconnected from to avoid issues and problems. It is done by two functions:

```
>> meca.Deactivate()
>> meca.Disconnect()
```

If during use the Meca500 encounters an error, it will go into error mode. In this mode, the module will block any command to the Meca500 unless its an error reset. To properly reset errors on the Meca500, the following functions in the corresponding order must be run:

```
>> meca.ResetError()
>> meca.Deactivate()
>> meca.Activate()
>> meca.Home()
```

For making a runnable script, the above functions call remain the same in the script. Actions must be placed between activation and deactivation to avoid errors. Writing the script is like regular programming in python. It is recommended to have an error catcher to get the Meca500 out of error mode and not have the Meca500 stop working in the middle of operation. This can be creatively done by using the isInError() and action functions to catch the Meca500 immediately as it falls in error and bringing it back to operating condition. A method can be made to it like the following:
```py
def AutoRepair(meca500):
    if(meca500.isInError()):
        meca500.ResetError()
        meca500.Deactivate()
        meca500.Activate()
        meca500.Home()
    elif(meca500.GetStatus()['Paused']==1):
        meca500.ResumeMotion()
```
Note: Deactivating and reactivating the Meca500 is not necessary but can be helpful.

An example of a script for the Meca500 would be:
```py
import Meca500
meca = Meca500.Meca500('192.168.0.100')
meca.Connect()
meca.Activate()
meca.Home()
meca.SetBlending(0)
meca.SetJointVel(100)
while True:
	meca.MoveJoints(0,0,0,170,115,175)
	meca.MoveJoints(0,0,0,-170,-115,-175)
	meca.MoveJoints(0,-70,70,0,0,0)
	meca.MoveJoints(0,90,-135,0,0,0)
	meca.GripperClose()
	meca.MoveJoints(0,0,0,0,0,0)
	meca.MoveJoints(175,0,0,0,0,0)
	meca.MoveJoints(-175,0,0,0,0,0)
	meca.MoveJoints(175,0,0,0,0,0)
	meca.GripperOpen()
	meca.MoveJoints(0,0,0,0,0,0)
```
This will make the Meca500 perform a repetitive task until the program is terminated.

A more viable way to make long programs for the Meca500 is by using a string. In python, there are various ways to write strings and the string type useful to making a program script is the triple quotes string. This format can be spread across multiple lines and include newlines into the string without placing them implicitly. This makes it easy to write and easy to read the program you are trying to write. The script can be written easily with the string format as follow:
```py
    TestProgram = """SetBlending(0)
                    SetJointVel(100)
                    MoveJoints(0,0,0,170,115,175)
                    MoveJoints(0,0,0,-170,-115,-175)
                    MoveJoints(0,0,0,170,115,175)
                    MoveJoints(0,0,0,-170,-115,-175)
                    MoveJoints(0,0,0,170,115,175)
                    MoveJoints(0,0,0,-170,-115,-175)
                    MoveJoints(0,0,0,170,115,175)
                    MoveJoints(0,0,0,-170,-115,-175)
                    MoveJoints(0,0,0,170,115,175)
                    MoveJoints(0,0,0,-170,-115,-175)
                    MoveJoints(0,-70,70,0,0,0)
                    MoveJoints(0,90,-135,0,0,0)
                    MoveJoints(0,-70,70,0,0,0)
                    MoveJoints(0,90,-135,0,0,0)
                    MoveJoints(0,-70,70,0,0,0)
                    MoveJoints(0,90,-135,0,0,0)
                    MoveJoints(0,-70,70,0,0,0)
                    MoveJoints(0,90,-135,0,0,0)
                    MoveJoints(0,-70,70,0,0,0)
                    MoveJoints(0,0,0,0,0,0)
                    MoveJoints(175,0,0,0,0,0)
                    MoveJoints(-175,0,0,0,0,0)
                    MoveJoints(175,0,0,0,0,0)
                    MoveJoints(-175,0,0,0,0,0)
                    MoveJoints(175,0,0,0,0,0)
                    MoveJoints(-175,0,0,0,0,0)
                    MoveJoints(175,0,0,0,0,0)
                    MoveJoints(-175,0,0,0,0,0)
                    MoveJoints(175,0,0,0,0,0)
                    MoveJoints(0,0,0,0,0,0)"""
```
Each line has a command with the arguments it requires. The commands are written in the same way as the functions in the module. Once the script is complete, it must be broken down into a list of actions. Python makes it easy by using the available string functions.
```py
Program = TestProgram.replace(' ','')
    movements = Program.split("\n")
```
The variable movement contains the list of actions to perform after getting rid of all the empty spaces and seperating the command by distinguishing commands by line. To go through the actions one by one, it is only required to make a loop that iterates through the actions. Using the __exchangeMsg__ function, it is easy to send the command to the Meca500. The __exchangeMsg__ function is responsable for interpreting the commands and return expected messages back to the user. It is the backbone of most of the functions of the module.
```py
for action in movements:
	meca500.exchangeMsg(action)
	if(meca500.isInError()):
    	AutoRepair(meca500)
```
If the script you wrote is one you wish the Meca500 to repeat until stopped by a user for whatever reason, the previous loop can be placed inside an infinite loop. Using all the information, building blocks and functions provided, you are fully equipped to control and program your Meca500 for your project.

## Built With

* [Visual Studio Code](https://code.visualstudio.com/) - code editor

## Authors 

* **Alexandre Coulombe** - *Continuous work*


