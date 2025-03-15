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
    can.update_frame_counter()
    validBlobCount = 0
    tallBlobIsBest = True
    blobCount = 0
    tallBlobH = 0
    tallBlobI = 0
    tallBlobA = 0
    tallBlobRect = (0, 0, 0, 0)
    tallBlobCenter = (0, 0, 0, 0, 0, 0)
    smallestRatioBlobCenter = (0, 0, 0, 0, 0, 0)
    smallestRatioBlobRect = (0, 0, 0, 0)
    smallestRatio = 0
    smallestRatioBlobI = 0
    bestBlob = 0
    clock.tick()
    img = sensor.snapshot()
    can.send_heartbeat()
    blobs = img.find_blobs([threshold], pixels_threshold=100, area_threshold=100, merge=True, margin=2)
    for blob in blobs:
        #print(dir(blob))
        aspect = blob.w() / blob.h()
        if aspect < .3 and 10 < blob.w() and blob.h() > 60:
            if blob.h() > tallBlobH:
                tallBlobI = blobCount
                tallBlobH = blob.h()
                tallBlobA = aspect
                tallBlobRect = (blob.x(), blob.y(), blob.w(), blob.h())
                tallBlobCenter = (blob.cx(), blob.cy(), blob.vx(), blob.vy(), blob.ttype(), blob.qual())
            if aspect < smallestRatio:
                smallestRatioBlobI = blobCount
                smallestRatio = aspect
                smallestRatioRect = (blob.x(), blob.y(), blob.w(), blob.h())
                smallestRatioBlobCenter = (blob.cx(), blob.cy(), blob.vx(), blob.vy(), blob.ttype(), blob.qual())
            validBlobCount += 1
        blobCount += 1

    if validBlobCount != 0:
        if tallBlobI == smallestRatioBlobI:
            bestBlob = tallBlobI
            previousBestBlobA = tallBlobA
        elif tallBlobH > 200:
            bestBlob = tallBlobI
            previousBestBlobA = tallBlobA
        elif previousBestBlobA - .05 < tallBlobI < previousBestBlobA + .05:
            bestBlob = tallBlobI
            previousBestBlobA = tallBlobA
        elif previousBestBlobA - .05 < smallestRatioBlobI < previousBestBlobA + .05:
            bestBlob = smallestRatioBlobI
            previousBestBlobA = smallestRatio
            tallBlobIsBest = False
        else:
            bestBlob = tallBlobI

    if can.get_frame_counter() % 50 == 0:
        can.send_config_data()
        can.send_camera_status(sensor.width(), sensor.height())

    if tallBlobIsBest and validBlobCount != 0:
        img.draw_rectangle(tallBlobRect)
        can.send_track_data(0, tallBlobCenter)
    elif validBlobCount != 0:
        img.draw_rectangle(smallestRatioBlobRect)
        can.send_track_data(0, smallestRatioBlobCenter)
    else:
        can.send_track_data(0, 0, 0, 0, 0, 0, 0)