#!/usr/bin/env python
import paho.mqtt.client as mqtt
import json

with open('options.json') as fp:
    options = json.load(fp)

echo_topics = options['echo_topics']
fix_values = options['fix_values']

state_values = {}
dirty = {}


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    for topic in echo_topics:
        client.subscribe(topic['command'])
        client.subscribe(topic['state'])


def on_message(client, userdata, msg):
    for topic in echo_topics:
        if msg.topic == topic['command']:
            new_vals = json.loads(msg.payload)
            status_topic = topic['state']
            if status_topic not in state_values:
                state_values[status_topic] = {}

            for fix_val in fix_values:
                if fix_val['key_in'] in new_vals.keys():
                    val = fix_val['val']
                    try:
                        val = json.loads(val.replace("'", '"'))
                    except ValueError as e:
                        if val.isdigit():
                            val = float(val)
                    new_vals[fix_val['key_out']] = val

            state_values[status_topic].update(new_vals)
            dirty[status_topic] = 1

            log("Update: " + str(msg.topic) + " " + str(msg.payload))
            return

    if dirty[msg.topic] and msg.topic in state_values:
        data = json.dumps(state_values[msg.topic])
        client.publish(msg.topic, data)
        dirty[msg.topic] = 0
        log("Publish: " + str(msg.topic) + " " + str(data))


def log(msg):
    if options.get('log_level') == "debug":
        print(msg)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(options['mqtt_user'], options['mqtt_pass'])
client.connect(options['mqtt_server'], options['mqtt_server_port'], 60)
client.loop_forever()