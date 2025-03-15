# Reef Detector One - By: FRC1073 - Wed Mar 12 2025

import sensor
import time
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

clock = time.clock()

threshold = (5, 95, 10, 55, -50, 20)

previousBestBlobA = 0

while True:
    tallBlobIsBest = True

    # keep track of information about the tallest blob
    tallBlobRect = (0, 0, 0, 0)
    tallBlobCenter = (0, 0, 0, 0, 0, 0)
    tallBlobH = 0 # height
    tallBlobI = 0 # index
    tallBlobA = 0 # aspect

    # keep track of infomation about the smallest blob
    smallestRatioBlobCenter = (0, 0, 0, 0, 0, 0)
    smallestRatioBlobRect = (0, 0, 0, 0)
    smallestRatio = 0
    smallestRatioBlobI = 0

    # keep track of the number and best blob
    validBlobCount = 0
    blobCount = 0
    bestBlob = 0

    can.update_frame_counter()
    clock.tick()
    img = sensor.snapshot()
    can.send_heartbeat()
    blobs = img.find_blobs([threshold], pixels_threshold=100, area_threshold=100, merge=True, margin=2)

    for blob in blobs:
        aspect = blob.w() / blob.h()

        # check if the blob is valid
        if aspect < 0.3 and blob.w() > 10 and blob.h() > 60:

            # set the tallest blob info if blob is tallest
            if blob.h() > tallBlobH:
                tallBlobI = blobCount
                tallBlobH = blob.h()
                tallBlobA = aspect
                tallBlobRect = (blob.x(), blob.y(), blob.w(), blob.h())
                tallBlobCenter = (blob.cx(), blob.cy(), blob.vx(), blob.vy(), blob.ttype(), blob.qual())

            # set the smallest blob info if the blob is smallest
            if aspect < smallestRatio:
                smallestRatioBlobI = blobCount
                smallestRatio = aspect
                smallestRatioRect = (blob.x(), blob.y(), blob.w(), blob.h())
                smallestRatioBlobCenter = (blob.cx(), blob.cy(), blob.vx(), blob.vy(), blob.ttype(), blob.qual())

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
    if can.get_frame_counter() % 50 == 0:
        can.send_config_data()
        can.send_camera_status(sensor.width(), sensor.height())

    # draw a rectangle and send tallest info to RIO
    if tallBlobIsBest and validBlobCount != 0:
        img.draw_rectangle(tallBlobRect)
        can.send_track_data(0, tallBlobCenter)

    # draw a rectangle and send smallest to RIO
    elif validBlobCount != 0:
        img.draw_rectangle(smallestRatioBlobRect)
        can.send_track_data(0, smallestRatioBlobCenter)

    else:
        can.send_track_data(0, 0, 0, 0, 0, 0, 0)
