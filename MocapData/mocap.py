import sys
import time
from MocapData.NatNetClient import NatNetClient
import MocapData.DataDescriptions
import MocapData.MoCapData


class Mocap():
    def __init__(self, clientAddress, serverAddress, useMulticast=False):
        self.streaming_client = NatNetClient()
        self.streaming_client.set_client_address(clientAddress)
        self.streaming_client.set_server_address(serverAddress)
        self.streaming_client.set_use_multicast(useMulticast)
        self.streaming_client.new_frame_listener = self.receive_new_frame
        self.streaming_client.rigid_body_listener = self.receive_rigid_body_frame
        self.current_position = (0, 0, 0)

    def receive_rigid_body_frame(self, new_id, position, rotation):
        self.current_position = position
        print(position)
        # print("Received frame for rigid body", new_id)

    def get_pos(self):
        return self.current_position

    def receive_new_frame(self, data_dict):
        order_list = ["frameNumber", "markerSetCount",
                      "unlabeledMarkersCount", "rigidBodyCount", "skeletonCount",
                      "labeledMarkerCount", "timecode", "timecodeSub", "timestamp",
                      "isRecording", "trackedModelsChanged"]
        dump_args = False
        if dump_args == True:
            out_string = "    "
            for key in data_dict:
                out_string += key + "="
                if key in data_dict:
                    out_string += data_dict[key] + " "
                out_string += "/"
            print(out_string)

    def start(self):
        is_running = self.streaming_client.run()
        if not is_running:
            print("ERROR: Could not start streaming client.")
            try:
                sys.exit(1)
            except SystemExit:
                print("...")
            finally:
                print("exiting")
        if self.streaming_client.connected() is False:
            print(
                "ERROR: Could not connect properly.  Check that Motive streaming is on.")
            try:
                sys.exit(2)
            except SystemExit:
                print("...")
            finally:
                print("exiting")
