# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# UART Control
#
# This example shows how to use the serial port on your OpenMV Cam. Attach pin
# P4 to the serial input of a serial LCD screen to see "Hello World!" printed
# on the serial LCD display.

from pyb import UART
import math
from machine import Pin

CAM_ID = '1'
print('started')

class SerialComms():
    def __init__(self, cam_id, baud_rate = 2000000, bits = 8, parity = 0, stop = 1, timeout_char = 2000):
        self.cam_id = cam_id
        self.baud_rate = baud_rate
        self.bits = bits
        self.parity = parity
        self.stop = stop
        self.timeout_char = timeout_char
        #self.uart = UART(3, self.baud_rate, self.bits, self.parity, self.stop, self.timeout_char)
        self.uart = UART(3, baudrate=self.baud_rate, bits=self.bits, parity=self.parity, stop=self.stop, timeout_char=self.timeout_char)

        self.control_pin = Pin("P3", Pin.OUT)
        self.control_pin.value(0)

    def transmit(self, data):
        self.control_pin.value(1)
        msg = ['1', 'ti'] + data
        for element in msg:
            self.uart.write(element)
            self.uart.write(',')
        self.uart.write('\n')
        self.control_pin.value(0)


class Camera():
    def __init__(self):
        pass

    def apriltags(self, args=6):
        img = sensor.snapshot()
        tags = img.find_apriltags()
        tag_data = []
        for tag in tags:
            distance = math.sqrt(pow(math.sqrt(pow(tag.x_translation(), 2) + pow(tag.y_translation(), 2)), 2) + pow(tag.z_translation(), 2))
            tag_values = [tag.id(), tag.x(), tag.y(), tag.rotation(), distance, tags.goodness()]
            tag_data.append(tag_values)
        return tag_data


# Always pass UART 3 for the UART number for your OpenMV Cam.
# The second argument is the UART baud rate. For a more advanced UART control
# example see the BLE-Shield driver.

serialcomms = SerialComms(1)
camera = Camera()
array = []
#while True:
#    output = serialcomms.uart.read(1)  # ".read()" by itself doesn't work, there's number of bytes, timeout, etc.
#    print(output)
#    array.append(output)
#    time.sleep_ms(500)

#    if output ==  '\n' or output == '\r' or output == '\r\n':
#        continue
#    results = array[0]
#    if(results != CAM_ID):
#        array = []
#        continue
#    else:
#        if(array[2] == 'a'):
#            response = camera.apriltags()
#        elif(array[2] == 'g'):
#            response = camera.gamepiece()
#        #response = array[0] + ',' + array[2] + response
#        response = camera.apriltag()
#        serialcomms.transmit(response)

