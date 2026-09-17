from agent import MqttClient
from init import COMM_ROOT, MAX_SPOTS, BARRIER_AUTO_CLOSE_S
import data_acq as da
import json, time, threading, random

TOPIC_SENS = f"{COMM_ROOT}sensors/#"
TOPIC_CTRL = f"{COMM_ROOT}control/#"
TOPIC_ALRM = f"{COMM_ROOT}alarm"

state = {
    'occupied': 0,
    'occupied_spots': set(),
    'barrier': 'CLOSED',
    'barrier_last_open_ts': 0
}

def publish_alarm(mqtt, level, msg):
    da.add_alert(level, msg)
    mqtt.publish(TOPIC_ALRM, json.dumps({'level': level, 'message': msg}))

def handle_sensor(mqtt, topic, payload):
    # sensors/spot-<n>/state, sensors/entry/button, sensors/exit/button, sensors/barrier-1/state
    name = topic.split(f"{COMM_ROOT}sensors/")[-1]
    da.add_data(name, payload)

    if name.startswith('spot-') and name.endswith('/state'):
        v = payload.upper()
        spot_id = name.split('/')[0] if '/' in name else None
        if v == 'OCCUPIED':
            if spot_id and spot_id not in state['occupied_spots']:
                state['occupied_spots'].add(spot_id)
                state['occupied'] += 1
        elif v == 'FREE':
            if spot_id and spot_id in state['occupied_spots']:
                state['occupied_spots'].remove(spot_id)
                if state['occupied'] > 0:
                    state['occupied'] -= 1
        if state['occupied'] >= MAX_SPOTS:
            publish_alarm(mqtt, 'ALARM', f'Parking Full ({state['occupied']}/{MAX_SPOTS})')
        return

    if name == 'entry/button':
        if state['occupied'] < MAX_SPOTS:
            mqtt.publish(f"{COMM_ROOT}devices/barrier-1/in", json.dumps({'state': 'OPEN'}))
        else:
            publish_alarm(mqtt, 'WARN', 'Entry pressed but parking is full')
        return

    
    if name == 'barrier-1/state':
        state['barrier'] = payload.upper()
        if state['barrier'] == 'OPEN':
            state['barrier_last_open_ts'] = time.time()
        return

def handle_control(mqtt, topic, payload):
    try:
        j = json.loads(payload)
    except:
        j = {'state': str(payload)}
    dev = topic.split(f"{COMM_ROOT}control/")[-1].split('/')[0]
    mqtt.publish(f"{COMM_ROOT}devices/{dev}/in", json.dumps(j))

def auto_exit_loop(mqtt, interval=10):
    # Every 'interval' seconds, simulate an exit:
    # - If there are occupied spots: free one randomly and open barrier
    # - Else: publish 'Parking empty' info
    while True:
        if state['occupied_spots']:
            pick = random.choice(list(state['occupied_spots']))
            mqtt.publish(f"{COMM_ROOT}sensors/{pick}/state", 'FREE')
            mqtt.publish(f"{COMM_ROOT}devices/barrier-1/in", json.dumps({'state': 'OPEN'}))
        else:
            publish_alarm(mqtt, 'INFO', 'Auto-exit: parking empty')
        time.sleep(interval)

def auto_close_loop(mqtt):
    while True:
        if state['barrier'] == 'OPEN' and (time.time() - state['barrier_last_open_ts']) > BARRIER_AUTO_CLOSE_S:
            mqtt.publish(f"{COMM_ROOT}devices/barrier-1/in", json.dumps({'state': 'CLOSED'}))
        time.sleep(1)

def main():
    da.init_db()
    mqtt = MqttClient('parking-manager')

    def on_msg(c,u,m):
        t = m.topic
        p = m.payload.decode('utf-8','ignore')
        if t.startswith(f"{COMM_ROOT}sensors/"):
            handle_sensor(mqtt, t, p)
        elif t.startswith(f"{COMM_ROOT}control/"):
            handle_control(mqtt, t, p)

    mqtt.connect()
    mqtt.client.on_message = on_msg
    mqtt.subscribe(TOPIC_SENS)
    mqtt.subscribe(TOPIC_CTRL)

    threading.Thread(target=auto_close_loop, args=(mqtt,), daemon=True).start()
    threading.Thread(target=auto_exit_loop, args=(mqtt,10), daemon=True).start()

    try:
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        mqtt.disconnect()

if __name__ == '__main__':
    main()
