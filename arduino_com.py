#!/usr/bin/env python3

import os
import types
import logging

try:
    from cmd2 import Cmd  # , options, make_option
except ImportError as err:
    print("Maybe you should pip3 install cmd2 (the better cmd class)")

try:
    from rip.head.spine.core import get_spine

    from rip.head.spine.appendages.motor import Motor as SpineMotor
    from rip.head.spine.appendages.switch import Switch as SpineSwitch
    from rip.head.spine.appendages.servo import Servo as SpineServo
    from rip.head.spine.appendages.electronic_component_detector import ElectronicComponentDetector as SpineElectronicComponentDetector
    from rip.head.spine.appendages.encoder import Encoder as SpineEncoder
    from rip.head.spine.appendages.arm import Arm as SpineArm
    from rip.head.spine.appendages.four_wheel_drive import FourWheelDrive as SpineFourWheelDrive
    from rip.head.spine.appendages.i2c_encoder import I2CEncoder as SpineI2CEncoder
    from rip.head.spine.appendages.line_sensor import LineSensor as SpineLineSensor
    from rip.head.spine.appendages.pid import Pid as SpinePid
    from rip.head.spine.appendages.stepper import Stepper as SpineStepper
    from rip.head.spine.appendages.ultrasonic import Ultrasonic as SpineUltrasonic
    from rip.head.spine.appendages.velocity_controlled_motor import VelocityControlledMotor as SpineVelocityControlledMotor
except ImportError as err:
    print("Unable to import RIP appendages,")
    print("Try this: git submodule update --init --recursive")
    print("Otherwise, add envvar PYTHONPATH=\"path/to/folder/with/rip\"")
    print("Specific Error: " + str(err))

from appendages.motor import Motor as ACMotor
from appendages.switch import Switch as ACSwitch
from appendages.servo import Servo as ACServo
from appendages.electronic_component_detector import ElectronicComponentDetector as ACElectronicComponentDetector
from appendages.encoder import Encoder as ACEncoder
from appendages.arm import Arm as ACArm
from appendages.four_wheel_drive import FourWheelDrive as ACFourWheelDrive
from appendages.i2c_encoder import I2CEncoder as ACI2CEncoder
from appendages.line_sensor import LineSensor as ACLineSensor
from appendages.pid import Pid as ACPid
from appendages.stepper import Stepper as ACStepper
from appendages.ultrasonic import Ultrasonic as ACUltrasonic
from appendages.velocity_controlled_motor import VelocityControlledMotor as ACVelocityControlledMotor

CURRENT_ARDUINO_CODE_DIR = "/Robot/CurrentArduinoCode"


class ArduinoCom(Cmd):
    intro = "Welcome to ArduinoCom. Type help or ? for commands.\nCtrl-D to exit."
    prompt = "AC> "
    doc_header = "Documentation available for:"
    undoc_header = "Not documented:"
    gs = None
    s = None
    appendages = None

    def __init__(self):
        super().__init__()
        self.registeredDevices = [d for d in os.listdir(CURRENT_ARDUINO_CODE_DIR)
                                  if os.path.isdir("{0:s}/{1:s}".format(CURRENT_ARDUINO_CODE_DIR, d)) and
                                  not d == ".git" and os.path.exists("{0:s}/{1:s}/{1:s}.json"
                                                                     .format(CURRENT_ARDUINO_CODE_DIR, d))]
        self.connectedDevices = [d for d in self.registeredDevices
                                 if os.path.exists("/dev/{0:s}".format(d))]

    def do_connect(self, parseResults):
        args = parseResults.parsed[1].split()
        if len(args) != 1:
            self.help_connect()
            return
        arduinoName = args[0]

        if arduinoName not in self.connectedDevices:
            print("Arduino \"{}\" is not available.".format(arduinoName))
            return

        self.gs = get_spine(devices=[arduinoName])
        self.s = self.gs.__enter__()
        self.appendages = self.s.get_appendage_dict()

        def registerMethods(ACClass):
            self.__dict__["do_" + name] = types.MethodType(ACClass.interact, self)
            self.__dict__["help_" + name] = types.MethodType(ACClass.help, self)
            self.__dict__["complete_" + name] = types.MethodType(ACClass.complete, self)

        for name, appendage in self.appendages.items():
            if isinstance(appendage, SpineMotor):
                registerMethods(ACMotor)
            elif isinstance(appendage, SpineSwitch):
                registerMethods(ACSwitch)
            elif isinstance(appendage, SpineServo):
                registerMethods(ACServo)
            elif isinstance(appendage, SpineElectronicComponentDetector):
                registerMethods(ACElectronicComponentDetector)
            elif isinstance(appendage, SpineEncoder):
                registerMethods(ACEncoder)
            elif isinstance(appendage, SpineArm):
                registerMethods(ACArm)
            elif isinstance(appendage, SpineFourWheelDrive):
                registerMethods(ACFourWheelDrive)
            elif isinstance(appendage, SpineI2CEncoder):
                registerMethods(ACI2CEncoder)
            elif isinstance(appendage, SpineLineSensor):
                registerMethods(ACLineSensor)
            elif isinstance(appendage, SpinePid):
                registerMethods(ACPid)
            elif isinstance(appendage, SpineStepper):
                registerMethods(ACStepper)
            elif isinstance(appendage, SpineUltrasonic):
                registerMethods(ACUltrasonic)
            elif isinstance(appendage, SpineVelocityControlledMotor):
                registerMethods(ACVelocityControlledMotor)

    def help_connect(self):
        print("usage: connect <ArduinoName>")

    def complete_connect(self, text, line, begidx, endidx):
        return [i for i in self.connectedDevices if i.startswith(text)]

    def do_disconnect(self, parseResults):
        if self.appendages is not None:
            for name in self.appendages:
                del self.__dict__["do_" + name]
                del self.__dict__["help_" + name]
                del self.__dict__["complete_" + name]
            self.appendages = None

            self.gs.__exit__(None, None, None)
            self.s = None
            self.gs = None

    def help_disconnect(self):
        print("usage: disconnect")
        print("Disconnects from a connected arduino.")

    def do_exit(self, parseResults):
        self.do_disconnect(None)
        return True

    def help_exit(self):
        print("Disconnects from any connected arduinos, and exits ArduinoCom.")

    def do_quit(self, parseResults):
        return self.do_exit(parseResults)

    def help_quit(self):
        print("Alias for exit")

    def do_EOF(self, parseResults):
        print()
        return self.do_exit(parseResults)
    do_eof = do_EOF

    def help_help(self):
        print("Prints help for commands")

    def get_names(self):
        names = dir(self)
        names.remove("do_EOF")
        names.remove("do_eof")
        names.remove("do_q")
        return names


if __name__ == '__main__':
    ac = ArduinoCom()
    ac.debug = True
    ac.case_insensitive = True
    logging.disable(logging.INFO)
    ac.cmdloop()