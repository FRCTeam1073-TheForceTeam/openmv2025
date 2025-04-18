# Import the frc_CAN library for talking with the RoboRio
# import frc_CAN

# This module implements the FRC CAN support library
# for our OpenMV cameras to talk to the RoboRio using
# FRC Can Arbitration IDs.
#

from pyb import CAN
import omv

canbuffer = bytearray(8)
candata = [0, 0, 0, memoryview(canbuffer)]

# Puts all the CAN support for FRC into one reusable place.
# This class uses FIFO 1 for callbacks in the API Class = 1
# space for mode control. FIFO 0 is used for other messages.
class frc_can:

    def __init__(self, devid):
        self.can = CAN(2, CAN.NORMAL, baudrate=1000000, sample_point=50)
        # Device id [0-63]
        self.devid = devid
        # Mode of the device
        self.mode = 0
        # Configuration data
        self.config_simple_targets = 0
        self.config_line_segments = 0
        self.config_color_detect = 0
        self.config_advanced_targets = 0
        self.frame_counter = 0
        # Buffer for receiving data in our callback.
        self.read_buffer = bytearray(8)
        self.read_data = [0, 0, 0, memoryview(self.read_buffer)]

        # Initialize CAN based on which type of board we're on
        if omv.board_type() == "H7":
            print("H7 CAN Interface")
        else:
            print("CAN INTERFACE NOT INITIALIZED!")

        self.can.restart()
        print("Camera Initialized")

    # Set config: This is reported to rio when we send config.
    def set_config(self, simple_targets, line_segments, color_detect, advanced_targets):
        self.config_simple_targets = simple_targets
        self.config_line_segments = line_segments
        self.config_color_detect = color_detect
        self.config_advanced_targets = advanced_targets

    # Update counter should be called after each processed frame. Sent to Rio in heartbeat.
    def update_frame_counter(self):
        self.frame_counter = self.frame_counter + 1

    def get_frame_counter(self):
        return self.frame_counter


    # Arbitration ID helper packs FRC CAN indices into a CANBus arbitration ID
    def arbitration_id(devtype, mfr, devid, apiid): # dev_type = 10, apiid = 0, dev_id = 1
        retval = (devtype & 0x1f) << 24 # retval = 167772160, hex = 0xa000000
        retval = retval | ((mfr & 0xff) << 16) # retval = 179109888, hex = 0xaad0000
        retval = retval | ((apiid & 0x3ff) << 6) # retval = 179109888, hex = 0xaad0000
        retval = retval | (devid & 0x3f) # retval = 179109889, hex = 0xaad0001
        return retval # bin = 0b1010101011010000000000000001 --> discounting 0b 28 bits
        # and first bit is zero making 29 (0b01010101011010000000000000001)


    # Arbitration ID helper, assumes devtype, mfr, and instance devid.
    def my_arb_id(self, apiid):
        devtype = 10   # FRC Miscellaneous is our device type
        mfr = 173      # Team 1073 ID to avoid conflict with all COTS devices
        retval = (devtype & 0x1f) << 24
        retval = retval | ((mfr & 0xff) << 16)
        retval = retval | ((apiid & 0x3ff) << 6)
        retval = retval | (self.devid & 0x3f)
        return retval

    # Return the combined API number of an API class and index:
    def api_id(self, api_class, api_index):
        return ((api_class & 0x3f) << 4) | (api_index & 0x0f)

    # Send message to my API id: Sends from OpenMV to Rio with our address.
    def send(self, apiid, bytes):
        sendid = self.my_arb_id(apiid)
        try:
            self.can.send(bytes, sendid, extframe=True,  timeout=33)
        except:
            print("CANbus exception.")
            self.can.restart()

    # API Class - 1:  Configuration
    # Whenever we set the mode from here we send it to the RoboRio
    def set_mode(self, mode):
        self.mode = mode
        self.send_config_data()

    # Allows us to read back mode in case Rio sets the mode.
    def get_mode(self):
        return self.mode

    # Called by filter when FIFO 0 gets a message.
    def incoming_callback_0(can, reason):
        if reason:
            print("CAN Message FIFO 0 REASON %d" % reason)
        else:
            print("CAN FIFO 0 CB: NULL REASON")

        message = can.recv(0, list = None, timeout=10)

        print("ARBID %d"%message[0])


    # Send our Config data to RoboRio
    def send_config_data(self):
        cb = bytearray(8)
        cb[0] = self.mode
        cb[2] = self.config_simple_targets
        cb[3] = self.config_line_segments
        cb[4] = self.config_color_detect
        cb[5] = self.config_advanced_targets
        self.send(self.api_id(1,0), cb)

    # Send our camera status data to RoboRio
    def send_camera_status(self, width, height):
        cb = bytearray(8)
        cb[0] = int(width/4);
        cb[1] = int(height/4);
        self.send(self.api_id(1,1), cb)


    # Called to update mode if it is changed.
    def check_mode(self):
        try:
            self.can.recv(0, self.read_data, timeout=10)
            if self.read_data[0] == self.my_arb_id(self.api_id(1,3)):
                self.mode = self.read_data[3][0]
                print("GOT MODE: %d" % self.mode)
            return True
        except:
            return False

    # Send the RIO the heartbeat message with our mode and frame counter:
    def send_heartbeat(self):
        hb = bytearray(3)
        hb[0] = (self.mode & 0xff)
        hb[1] = (self.frame_counter & 0xff00) >> 8
        hb[2] = (self.frame_counter & 0x00ff)
        self.send(self.api_id(1,2), hb)

    # API Class - 2: Simple Target Tracking

    # Send tracking data for a given tracking slot to RoboRio.
    def send_track_data(self, slot, cx, cy):
        tdb = bytearray(7)
        tdb[0] = (cx & 0xff0) >> 4
        tdb[1] = (cx & 0x00f) << 4 | (cy & 0xf00) >> 8
        tdb[2] = (cy & 0x0ff)
        tdb[3] = (0 & 0xff)
        tdb[4] = (0 & 0xff)
        tdb[5] = (0 & 0xff)
        tdb[6] = (0 & 0xff)
        self.send(self.api_id(2, slot), tdb)

    # Track is empty when quality is zero, send empty slot /w 0 quality.
    def clear_track_data(self, slot):
        # Assume fills with zero.
        tdb = bytearray(7)
        self.send(self.api_id(2, slot), tdb)


    # Line Segment Tracking API Class: 3

    # Send line segment data to a slot to RoboRio.
    def send_line_data(self, slot, x0, y0, x1, y1, ttype, qual):
        ldb = bytearray(8)
        ldb[0] = (x0 & 0xff0) >> 4
        ldb[1] = ((x0 & 0x00f) << 4) | ((y0 & 0xf00) >> 8)
        ldb[2] = (y0 & 0x0ff)
        ldb[3] = (x1 & 0xff0) >> 4
        ldb[4] = ((x1 & 0x00f) << 4) | ((y1 & 0xf00) >> 8)
        ldb[5] = (y1 & 0x0ff)
        ldb[6] = (ttype & 0xff)
        ldb[7] = (qual & 0xff)
        self.send(self.api_id(3,slot), ldb)

    # Send null, 0 quality line to clear a slot for RoboRio.
    def clear_line_data(self, slot):
        ldb = bytearray(8)
        self.send(self.api_id(3,slot), ldb)

    # Color Detection API Class: 4

    # Send the given color segmentation data to the RoboRio
    def send_color_data(self, c0,p0,c1,p1,c2,p2,c3,p3):
        cdb = bytearray(8)
        cdb[0] = c0 & 0xff
        cdb[1] = p0 & 0xff
        cdb[2] = c1 & 0xff
        cdb[3] = p1 & 0xff
        cdb[4] = c2 & 0xff
        cdb[5] = p2 & 0xff
        cdb[6] = c3 & 0xff
        cdb[7] = p3 & 0xff
        self.send(self.api_id(4,0), cdb)

    # Send empty color data / invalid colors to RoboRio.
    def clear_color_data(self):
        cdb = bytearray(8)
        self.send(self.api_id(4,0), cdb)

    # Advanced Target Tracking API Class: 5

    # Send advanced target tracking data to RoboRio
    def send_advanced_track_data(self, cx, cy, area, ttype, qual, skew, slot=1):
        atb = bytearray(8)
        atb[0] = (cx & 0xff0) >> 4
        atb[1] = ((cx & 0x00f) << 4) | ((cy & 0xf00) >> 8)
        atb[2] = (cy & 0x0ff)
        atb[3] = (area & 0xff00) >> 8
        atb[4] = (area & 0x00ff)
        atb[5] = (ttype & 0xff)
        atb[6] = (qual & 0xff)
        atb[7] = (skew & 0xff)
        self.send(self.api_id(5, slot), atb)

    # Send a null / 0 quality update to clear track data to RoboRio
    def clear_advanced_track_data(self, slot=1):
        atb = bytearray(8)
        self.send(self.api_id(5, slot), atb)

    #send LiDar range sensing data to the RIO using API class 6
    #r stands for range
    def send_range_data(self, r, qual):
        atb = bytearray(3)
        atb[0] = (r & 0xff00) >> 8
        atb[1] = (r & 0x00ff)
        atb[2] = (qual & 0xff)
        self.send(self.api_id(6, 1), atb)
