import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from agent import MqttClient
from init import COMM_ROOT

def main():
    mqtt = MqttClient('emu-entry-button')
    mqtt.connect()
    try:
        while True:
            mqtt.publish(f"{COMM_ROOT}sensors/entry/button", 'PRESS')
            time.sleep(7)
    except KeyboardInterrupt:
        mqtt.disconnect()

if __name__ == '__main__':
    main()
