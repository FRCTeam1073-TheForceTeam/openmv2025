from pyb import CAN
import omv

example_id = 0b01010101011010000000000000001

class frc_can:

    def __init__(self, devid):
        self.can = CAN(2, CAN.NORMAL, baudrate=1000000, sample_point=50)
        self.frame_counter = 0
        # Buffer for receiving data in our callback.

        # Initialize CAN based on which type of board we're on
        if omv.board_type() == "H7":
            print("H7 CAN Interface")
            self.can.init(CAN.NORMAL, extframe=True, prescaler=4,  sjw=1, bs1=8, bs2=3)
        else:
            print("CAN INTERFACE NOT INITIALIZED!")

        self.can.restart()
        print("Camera Initialized")

    # Update counter should be called after each processed frame. Sent to Rio in heartbeat.
    def update_frame_counter(self):
        self.frame_counter = self.frame_counter + 1


    # Send message to my API id: Sends from OpenMV to Rio with our address.
    def send(self, bytes):
        try:
            self.can.send(bytes, example_id, timeout=33)
        except:
            print("CANbus exception.")
            self.can.restart()
