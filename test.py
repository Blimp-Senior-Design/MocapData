from MocapData.mocap import Mocap

cap = Mocap("192.168.1.161", "192.168.1.151")

cap.start()

cap.get_pos()
