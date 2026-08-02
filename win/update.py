# update.py
# For publishing commands targeting a networked digital signage device running
# mpvlisten.py on the "lutero/sign" topic. 
# This script assumes the MQTT broker is on the same local network and accepts
# anonymous connections.

# Part of Lutero. https://github.com/TheOpponent/Lutero
# This file is in the public domain (Unlicense). https://unlicense.org

import sys

from paho.mqtt import publish

# Set to the IP of the PC running the MQTT broker. Ideally this will be this
# PC, with the listener setting bound to the IP of the NIC (not localhost)
# connected to the digital sign or hub.
BROKER_IP = "192.168.19.1"
BROKER_PORT = 1883

def main():
    msgs = []

    if len(sys.argv) == 1:
        msgs.append(("lutero/sign", "^reset", 2))
    elif len(sys.argv) == 2:
        msgs.append(("lutero/sign", sys.argv[1], 2))
    else:
        print("Incorrect number of arguments.")
        sys.exit()

    publish.multiple(msgs, BROKER_IP, BROKER_PORT)


if __name__ == "__main__":
    main()
