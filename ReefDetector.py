# Reef Detector One - By: FRC1073 - Wed Mar 12 2025

import sensor
import time
# import frc_can # this needs to be stored on camera
import frc_can

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # must be turned off for color tracking
sensor.set_auto_whitebal(False)  # must be turned off for color tracking

can = frc_can.frc_can(1)
can.set_config(2, 0, 0, 0)
can.set_mode(1)
print('Config and Mode set\n')

clock = time.clock()

threshold = (33, 74, 38, 76, -59, -26)

previousBestBlobA = 0

#this is info for drawing a rectangle on the camera
rect_colored = False
rect_attribute = (0, 0, 0, 0)

while True:
    # keep track of information about the tallest blob
    blobRect = (0, 0, 0, 0)
    blobCenter = (0, 0)
    blobH = 0 # height
    blobI = 0 # index
    blobA = 0 # aspect

    # keep track of the number and best blob
    validBlobCount = 0
    blobCount = 0
    bestBlob = 0

    can.update_frame_counter()
    clock.tick()
    img = sensor.snapshot()

    if can.get_frame_counter() % 10 == 0:
         can.send_heartbeat()
         print('Sent Heartbeat')

    blobs = img.find_blobs([threshold], pixels_threshold=100, area_threshold=100, merge=True, margin=2)

    for blob in blobs:
        aspect = blob.w() / blob.h()
        # check if the blob is valid
        if blob.w() > 10 and blob.h() > 60:
            # set the tallest blob info if blob is tallest
            if blob.h() > blobH:
                blobI = blobCount
                blobH = blob.h()
                blobA = aspect
                blobRect = (blob.x(), blob.y(), blob.w(), blob.h())
                blobCenter = (blob.cx(), blob.cy())

            validBlobCount += 1

        blobCount += 1

    if validBlobCount != 0:

        # tall blob is the best blob
        if blobH > 200 or previousBestBlobA - 0.05 < blobI < previousBestBlobA + 0.05:
            bestBlob = blobI
            previousBestBlobA = blobA

        # smallest blob is the best if taller than the previous aspect
        elif previousBestBlobA - 0.05 < blobI < previousBestBlobA + 0.05:
            bestBlob = blobI
            previousBestBlobA = blobA

        else:
            bestBlob = blobI

    # run every 50 frames
    if can.get_frame_counter() % 60 == 0:
       can.send_config_data()
       can.send_camera_status(sensor.width(), sensor.height())

    # send tallest info to RIO
    if can.get_frame_counter() % 2 == 0:
        if validBlobCount != 0:
            can.send_track_data(0, blobCenter[0], blobCenter[1], 0, 0, 0, 0)
            print(f'found blob {can.get_frame_counter()}\n')
            rect_colored = True
            rect_attribute = blobRect

        else:
            can.send_track_data(0, 0, 0, 0, 0, 0, 0)
            print(f'no valid blobs {can.get_frame_counter()}\n')
            rect_colored = False

    if(rect_colored):
        img.draw_rectangle(rect_attribute[0], rect_attribute[1], rect_attribute[2], rect_attribute[3], color=(255, 0, 0), thickness=3)
        img.draw_circle(blobCenter[0], blobCenter[1], 10, color=(0, 0, 255), thickness=3)
    else:
        img.draw_rectangle(rect_attribute[0], rect_attribute[1], rect_attribute[2], rect_attribute[3], color=(255, 0, 0), thickness=0)
