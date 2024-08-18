import sys
import time
from NatNetClient import NatNetClient
import DataDescriptions
import MoCapData
from Viz.Viz import Viz


viz = Viz()


def my_parse_args(arg_list, args_dict):
    # set up base values
    arg_list_len = len(arg_list)
    if arg_list_len > 1:
        args_dict["serverAddress"] = arg_list[1]
        if arg_list_len > 2:
            args_dict["clientAddress"] = arg_list[2]
        if arg_list_len > 3:
            if len(arg_list[3]):
                args_dict["use_multicast"] = True
                if arg_list[3][0].upper() == "U":
                    args_dict["use_multicast"] = False

    return args_dict

# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame


def receive_rigid_body_frame(new_id, position, rotation):
    viz.record_trajectory_real(position, depth=900)
    print("Received frame for rigid body",
          new_id, " ", position, " ", rotation)
    # print("Received frame for rigid body", new_id)


def receive_new_frame(data_dict):
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


def print_configuration(natnet_client):
    natnet_client.refresh_configuration()
    print("Connection Configuration:")
    print("  Client:          %s" % natnet_client.local_ip_address)
    print("  Server:          %s" % natnet_client.server_ip_address)
    print("  Command Port:    %d" % natnet_client.command_port)
    print("  Data Port:       %d" % natnet_client.data_port)

    changeBitstreamString = "  Can Change Bitstream Version = "
    if natnet_client.use_multicast:
        print("  Using Multicast")
        print("  Multicast Group: %s" % natnet_client.multicast_address)
        changeBitstreamString += "false"
    else:
        print("  Using Unicast")
        changeBitstreamString += "true"

    # NatNet Server Info
    application_name = natnet_client.get_application_name()
    nat_net_requested_version = natnet_client.get_nat_net_requested_version()
    nat_net_version_server = natnet_client.get_nat_net_version_server()
    server_version = natnet_client.get_server_version()

    print("  NatNet Server Info")
    print("    Application Name %s" % (application_name))
    print("    MotiveVersion  %d %d %d %d" % (
        server_version[0], server_version[1], server_version[2], server_version[3]))
    print("    NatNetVersion  %d %d %d %d" % (
        nat_net_version_server[0], nat_net_version_server[1], nat_net_version_server[2], nat_net_version_server[3]))
    print("  NatNet Bitstream Requested")
    print("    NatNetVersion  %d %d %d %d" % (nat_net_requested_version[0], nat_net_requested_version[1],
                                              nat_net_requested_version[2], nat_net_requested_version[3]))

    print(changeBitstreamString)
    # print("command_socket = %s"%(str(natnet_client.command_socket)))
    # print("data_socket    = %s"%(str(natnet_client.data_socket)))
    print("  PythonVersion    %s" % (sys.version))


def request_data_descriptions(s_client):
    # Request the model definitions
    s_client.send_request(s_client.command_socket, s_client.NAT_REQUEST_MODELDEF,
                          "",  (s_client.server_ip_address, s_client.command_port))


if __name__ == "__main__":
    optionsDict = {}
    optionsDict["clientAddress"] = "192.168.1.161"
    optionsDict["serverAddress"] = "192.168.1.151"
    optionsDict["use_multicast"] = True

    # This will create a new NatNet client
    optionsDict = my_parse_args(sys.argv, optionsDict)

    streaming_client = NatNetClient()
    streaming_client.set_client_address(optionsDict["clientAddress"])
    streaming_client.set_server_address(optionsDict["serverAddress"])
    streaming_client.set_use_multicast(optionsDict["use_multicast"])

    # Configure the streaming client to call our rigid body handler on the emulator to send data out.
    streaming_client.new_frame_listener = receive_new_frame
    streaming_client.rigid_body_listener = receive_rigid_body_frame

    # Start up the streaming client now that the callbacks are set up.
    # This will run perpetually, and operate on a separate thread.
    is_running = streaming_client.run()
    if not is_running:
        print("ERROR: Could not start streaming client.")
        try:
            sys.exit(1)
        except SystemExit:
            print("...")
        finally:
            print("exiting")

    is_looping = True
    time.sleep(1)
    if streaming_client.connected() is False:
        print("ERROR: Could not connect properly.  Check that Motive streaming is on.")
        try:
            sys.exit(2)
        except SystemExit:
            print("...")
        finally:
            print("exiting")

    streaming_client.set_print_level(0)
    print_configuration(streaming_client)
    print("\n")
    print(streaming_client.can_change_bitstream_version())

    try:
        while is_looping:
            pass
            # streaming_client.send_command("TimelinePlay")
            # request_data_descriptions(streaming_client)
    except KeyboardInterrupt:
        streaming_client.shutdown()
        viz.plot_trajectory("test.png")
    finally:
        sys.exit(0)
