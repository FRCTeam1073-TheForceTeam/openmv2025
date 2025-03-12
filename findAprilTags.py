# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# AprilTags Example
#
# This example shows the power of the OpenMV Cam to detect April Tags
# on the OpenMV Cam M7. The M4 versions cannot detect April Tags.

import sensor
import image
import time
import math
import sys
import os
from pyb import UART


print(os.listdir())
import camnet

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=5000)
sensor.set_auto_gain(False)  # must turn this off to prevent image washout...
sensor.set_auto_whitebal(False)  # must turn this off to prevent image washout...
clock = time.clock()

uart = UART(3, 2000000, bits=8, parity=0, stop=1, timeout_char=2000)  # default (200) was too low


# Note! Unlike find_qrcodes the find_apriltags method does not need lens correction on the image to work.

# The apriltag code supports up to 6 tag families which can be processed at the same time.
# Returned tag objects will have their tag family and id within the tag family.

tag_families = 0
tag_families |= image.TAG16H5  # comment out to disable this family
tag_families |= image.TAG25H7  # comment out to disable this family
tag_families |= image.TAG25H9  # comment out to disable this family
tag_families |= image.TAG36H10  # comment out to disable this family
tag_families |= image.TAG36H11  # comment out to disable this family (default family)
tag_families |= image.ARTOOLKIT  # comment out to disable this family

# What's the difference between tag families? Well, for example, the TAG16H5 family is effectively
# a 4x4 square tag. So, this means it can be seen at a longer distance than a TAG36H11 tag which
# is a 6x6 square tag. However, the lower H value (H5 versus H11) means that the false positive
# rate for the 4x4 tag is much, much, much, higher than the 6x6 tag. So, unless you have a
# reason to use the other tags families just use TAG36H11 which is the default family.

cnet = camnet.SerialComms(1)

def family_name(tag):
    if tag.family() == image.TAG16H5:
        return "TAG16H5"
    if tag.family() == image.TAG25H7:
        return "TAG25H7"
    if tag.family() == image.TAG25H9:
        return "TAG25H9"
    if tag.family() == image.TAG36H10:
        return "TAG36H10"
    if tag.family() == image.TAG36H11:
        return "TAG36H11"
    if tag.family() == image.ARTOOLKIT:
        return "ARTOOLKIT"

def handlemsg(msg):
    output = serialcomms.uart.write(msg)


#while True:
#    clock.tick()
#    img = sensor.snapshot()
#    for tag in img.find_apriltags(
#        families=tag_families
#    ):  # defaults to TAG36H11 without "families".
#        img.draw_rectangle(tag.rect(), color=(255, 0, 0))
#        img.draw_cross(tag.cx(), tag.cy(), color=(0, 255, 0))
#        print_args = (family_name(tag), tag.id(), (180 * tag.rotation()) / math.pi)
#        #print("Tag Family %s, Tag ID %d, rotation %f (degrees)" % print_args)
#    #print(clock.fps())

#    img = sensor.snapshot()
#    tags = img.find_apriltags()
#    tag_data = []
#    for tag in tags:
#        distance = math.sqrt(pow(math.sqrt(pow(tag.x_translation(), 2) + pow(tag.y_translation(), 2)), 2) + pow(tag.z_translation(), 2))
#        tag_values = [tag.id(), tag.x(), tag.y(), tag.rotation(), distance, tag.goodness()]
#        tag_data.append(tag_values)
#    print(tag_data)
#    cnet.transmit(tag_data)

data = []


while True:
    output = uart.readline()  # ".read()" by itself doesn't work, there's number of bytes, timeout, etc.
    #output = uart.read(4)
    print(output)
    #output_as_string = str(output)
    #print(output_as_string)
    if output == b'ti\n':
        print('got teleop init')
    elif output == b'ai\n':
        print('got autonomous init')
    elif output == b'di\n':
        print('got disable init')
    else:
        print(f'got something weird: {output}')
    time.sleep_ms(500)

#while True:
#    output = uart.read(1)  # ".read()" by itself doesn't work, there's number of bytes, timeout, etc.
#    print(output)
#    data.append(output)
#    time.sleep_ms(500)

#    if output ==  '\n' or output == '\r' or output == '\r\n':
#        handlemsg(data)
#        data = []


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
