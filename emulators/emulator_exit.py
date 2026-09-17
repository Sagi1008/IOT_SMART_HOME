import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time, random
from agent import MqttClient
from init import COMM_ROOT, MAX_SPOTS

INTERVAL_SEC = 6

def main():
    mqtt = MqttClient('emu-exit')
    mqtt.connect()
    try:
        while True:
            n = random.randint(1, MAX_SPOTS)
            mqtt.publish(f"{COMM_ROOT}sensors/spot-{n}/state", 'FREE')
            time.sleep(INTERVAL_SEC)
    except KeyboardInterrupt:
        mqtt.disconnect()

if __name__ == '__main__':
    main()
