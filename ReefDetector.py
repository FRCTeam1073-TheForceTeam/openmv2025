# Reef Detector - By: FRC1073 - Wed Mar 12 2025

import sensor
import time

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # must be turned off for color tracking
sensor.set_auto_whitebal(False)  # must be turned off for color tracking

clock = time.clock()

threshold = (10, 90, 25, 50, -50, 20)

while True:
    blobs = []
    clock.tick()
    img = sensor.snapshot()
    for blob in img.find_blobs(
        [threshold], pixels_threshold=100, area_threshold=100, merge=True, margin=1):
        #print(blob.__dict__())
        #print(dir(blob))
        aspect = blob.w() / blob.h()
        if aspect < .3:# and 6 < blob.w() < 120 and blob.h() > 80:
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())
            print(f'{blob.h()}, {blob.w()}, {aspect}')
            blobs.append(blob)
