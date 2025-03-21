# Reef Detector One - By: FRC1073 - Wed Mar 12 2025

import sensor
import time
# import frc_can # this needs to be stored on camera
import frc_can_skeleton

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # must be turned off for color tracking
sensor.set_auto_whitebal(False)  # must be turned off for color tracking

can = frc_can_skeleton.frc_can(1)
# can.set_config(2, 0, 0, 0)
# can.set_mode(1)

clock = time.clock()

threshold = (4, 95, 10, 65, -50, 20)

previousBestBlobA = 0
frame_diff = 10

rect_colored = False
rect_attribute = (0, 0, 0, 0)

while True:
    tallBlobIsBest = True

    # keep track of information about the tallest blob
    tallBlobRect = (0, 0, 0, 0)
    tallBlobCenter = (0, 0)
    tallBlobH = 0 # height
    tallBlobI = 0 # index
    tallBlobA = 0 # aspect
    tallBlobArray = bytearray(3)

    # keep track of infomation about the smallest blob
    smallestRatioBlobCenter = (0, 0)
    smallestRatioBlobRect = (0, 0, 0, 0)
    smallestRatio = 0
    smallestRatioBlobI = 0
    smallestRatioBlobArray = bytearray(3)

    # keep track of the number and best blob
    validBlobCount = 0
    blobCount = 0
    bestBlob = 0

    can.update_frame_counter()
    clock.tick()
    img = sensor.snapshot()
    if can.getFrameCounter() % frame_diff == 0:
        can.send_heartbeat()
    blobs = img.find_blobs([threshold], pixels_threshold=100, area_threshold=100, merge=True, margin=2)

    for blob in blobs:
        aspect = blob.h() / blob.w() # camera is sideways so w and h are swapped
        # check if the blob is valid
        if aspect < 0.15 and blob.h() > 10 and blob.w() > 60:
            # set the tallest blob info if blob is tallest
            if blob.w() > tallBlobH:
                tallBlobI = blobCount
                tallBlobH = blob.w()
                tallBlobA = aspect
                tallBlobRect = (blob.x(), blob.y(), blob.w(), blob.h())
                tallBlobCenter = (blob.cx(), blob.cy())

            # set the smallest blob info if the blob is smallest
            if aspect < smallestRatio:
                smallestRatioBlobI = blobCount
                smallestRatio = aspect
                smallestRatioRect = (blob.x(), blob.y(), blob.w(), blob.h())
                smallestRatioBlobCenter = (blob.cx(), blob.cy())
            validBlobCount += 1

        blobCount += 1

    if validBlobCount != 0:

        # tall blob is the best blob
        if tallBlobI == smallestRatioBlobI or tallBlobH > 200 or previousBestBlobA - 0.05 < tallBlobI < previousBestBlobA + 0.05:
            bestBlob = tallBlobI
            previousBestBlobA = tallBlobA

        # smallest blob is the best if taller than the previous aspect
        elif previousBestBlobA - 0.05 < smallestRatioBlobI < previousBestBlobA + 0.05:
            bestBlob = smallestRatioBlobI
            previousBestBlobA = smallestRatio
            tallBlobIsBest = False

        else:
            bestBlob = tallBlobI

    # run every 50 frames
    # if can.getFrameCounter() % (frame_diff + 5) == 0:
    #    can.send_config_data()
    #
    # if can.get_frame_counter() % (frame_diff + 10) == 0:
    #   can.send_camera_status(sensor.width(), sensor.height())

    # draw a rectangle and send tallest info to RIO
    if can.getFrameCounter() % (frame_diff + 15) == 0:
        if tallBlobIsBest and validBlobCount != 0:
            # can.send_track_data(0, tallBlobCenter[0], smallestRatioBlobCenter[1])
            tallBlobArray[0] = (tallBlobCenter[0] & 0xff0) >> 4
            tallBlobArray[1] = (tallBlobCenter[0] & 0x00f) << 4 | (tallBlobCenter[1] & 0x00f) >> 8
            tallBlobArray[2] = (tallBlobCenter[1] & 0x0ff)
            can.send(tallBlobArray)
            print('found tall blob')
            rect_colored = True
            rect_attribute = tallBlobRect

        # draw a rectangle and send smallest to RIO
        elif validBlobCount != 0:
            img.draw_rectangle(smallestRatioBlobRect[0], smallestRatioBlobRect[1], smallestRatioBlobRect[2], smallestRatioBlobRect[3], color = (255, 255, 0), thickness = 2)
            # can.send_track_data(0, smallestRatioBlobCenter[0], smallestRatioBlobCenter[1])
            smallestRatioBlobArray[0] = (smallestRatioBlobCenter[0] & 0xff0) >> 4
            smallestRatioBlobArray[1] = (smallestRatioBlobCenter[0] & 0x00f) << 4 | (smallestRatioBlobCenter[1] & 0x00f) >> 8
            smallestRatioBlobArray[2] = (smallestRatioBlobCenter[1] & 0x0ff)
            can.send(smallestRatioBlobArray)
            print('found blob!!!')
            rect_colored = True
            rect_attribute = smallestRatioBlobRect

        else:
            # can.send_track_data(0, 0, 0)
            print('no valid blobs')
            can.send(0)
            rect_colored = False

    if(rect_colored):
        img.draw_rectangle(rect_attribute[0], rect_attribute[1], rect_attribute[2], rect_attribute[3], color = (255, 255, 0), thickness = 2)
    else:
        img.draw_rectangle(rect_attribute[0], rect_attribute[1], rect_attribute[2], rect_attribute[3], color = (255, 255, 0), thickness = 0)

    can.update_frame_counter()
