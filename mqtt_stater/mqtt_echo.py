#!/usr/bin/env python
import paho.mqtt.client as mqtt
import json

with open('options.json') as fp:
    options = json.load(fp)

echo_topics = options['echo_topics']

dirty = {}


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    for topic in echo_topics:
        client.subscribe(topic['command'])
        client.subscribe(topic['state'])


def on_message(client, userdata, msg):
    for topic in echo_topics:
        new_vals = json.loads(msg.payload)
        if msg.topic == topic['command'] and topic['key_in'] in new_vals.keys():
            val = topic['val']
            try:
                val = json.loads(val.replace("'", '"'))
            except ValueError as e:
                if val.isdigit():
                    val = float(val)
            dirty[topic['state']] = {
                'state_count': 0,
                'state_fire': topic['state_fire'],
                'val': val
            }
            log("Update: " + str(msg.topic) + " " + str(msg.payload))
            return
        elif msg.topic == topic['state'] and msg.topic in dirty:
            dirty[msg.topic]['state_count'] += 1
            if dirty[msg.topic]['state_count'] == dirty[msg.topic]['state_fire']:
                state_vals = json.loads(msg.payload)
                entry = dirty.pop(msg.topic)
                state_vals.update(entry['val'])
                data = json.dumps(state_vals)
                log("Publish: " + str(msg.topic) + " " + str(data))
                client.publish(msg.topic, data)


def log(msg):
    if options.get('log_level') == "debug":
        print(msg)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(options['mqtt_user'], options['mqtt_pass'])
client.connect(options['mqtt_server'], options['mqtt_server_port'], 60)
client.loop_forever()
