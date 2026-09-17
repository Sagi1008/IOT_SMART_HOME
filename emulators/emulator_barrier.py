import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json, time
from agent import MqttClient
from init import COMM_ROOT

DEV = 'barrier-1'

def main():
    mqtt = MqttClient('emu-barrier')
    state = 'CLOSED'
    def on_msg(c,u,m):
        nonlocal state
        if m.topic == f"{COMM_ROOT}devices/{DEV}/in":
            try:
                j = json.loads(m.payload.decode('utf-8','ignore'))
                if j.get('state') in ('OPEN','CLOSED'):
                    state = j['state']
            except: pass
            mqtt.publish(f"{COMM_ROOT}sensors/{DEV}/state", state)

    mqtt.connect()
    mqtt.client.on_message = on_msg
    mqtt.subscribe(f"{COMM_ROOT}devices/{DEV}/in")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mqtt.disconnect()

if __name__ == '__main__':
    main()
