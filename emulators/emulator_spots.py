import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time, random
from agent import MqttClient
from init import COMM_ROOT, MAX_SPOTS

SPOTS = [f'spot-{i}' for i in range(1, MAX_SPOTS+1)]

def main():
    mqtt = MqttClient('emu-spots')
    mqtt.connect()
    occ = 0
    try:
        while True:
            spot = random.choice(SPOTS)
            make_occ = random.choice([True, False])
            if make_occ and occ < MAX_SPOTS:
                mqtt.publish(f"{COMM_ROOT}sensors/{spot}/state", 'OCCUPIED'); occ += 1
            elif not make_occ and occ > 0:
                mqtt.publish(f"{COMM_ROOT}sensors/{spot}/state", 'FREE'); occ -= 1
            mqtt.publish(f"{COMM_ROOT}sensors/lot/occupied", str(occ))
            time.sleep(2)
    except KeyboardInterrupt:
        mqtt.disconnect()

if __name__ == '__main__':
    main()
