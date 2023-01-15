# Created by NPetersenDK - please use as inspiration.
# Change "NameOnDevice" to the name(s) you have given it

# This script uses two buckets, you can remove one of them if you want. 
# That is to have realtime data in a "SPAM" bucket that has a retention policy. 
# And a bucket for long term with a timeout thats being set in the "Power_false_timeout" parameter.

# Requirements - see the below imported, and of course a Frient Electricity Meter and a MQTT + InfluxDB server

import paho.mqtt.client as mqtt
import json
import requests
import datetime


from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
bucket = "Python-MQTT-Frient-SPAM"
longtermbucket = "Python-MQTT-Frient-LONGTERM"
client = InfluxDBClient(url="YOURIPHERE:8086", token="YOURTOKENHERE", org="YOURORGHERE")
write_api = client.write_api(write_options=SYNCHRONOUS)


lastvalues = {
	"NameOnDevice": "At runtime",
}

Power_false = "At runtime"
Power_false_timeout = 3

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("zigbee2mqtt/NameOnDevice")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	global lastvalues
	global Power_false

	try:
		output = json.loads(msg.payload)
	except:
		print("nok ikke json")

	if msg.topic.startswith("zigbee2mqtt/NameOnDevice"):
		now = datetime.datetime.now()

		namesplit = msg.topic.split("/")[1]

		try:
			energy = float(output["energy"])
			power = float(output["power"])

			try:

				if lastvalues[namesplit] == "At runtime":
					print("First run")
					lastvalues[namesplit] = now
					print(power)
					print(energy)

					print("Writing power to spam bucket")
					p = Point("Powermeter").tag("Device", msg.topic).field("Wattage", power)
					write_api.write(bucket=bucket, record=p)

					print("Writing to normal bucket")
					p = Point("Powermeter").tag("Device", msg.topic).field("Wattage", power)
					write_api.write(bucket=longtermbucket, record=p)

					print("Writing energy usage to Influx")
					p = Point("Powermeter").tag("Device", msg.topic).field("Energy", energy)
					write_api.write(bucket=longtermbucket, record=p)

				else:
					print("Sending to all data bucket")
					p = Point("Powermeter").tag("Device", msg.topic).field("Wattage", power)
					write_api.write(bucket=bucket, record=p)

					if now > lastvalues[namesplit] + datetime.timedelta(minutes = Power_false_timeout):
						lastvalues[namesplit] = now
						print("More than the timeout time has passed, pushing data.")

						print("Writing power to Influx")
						p = Point("Powermeter").tag("Device", msg.topic).field("Wattage", power)
						write_api.write(bucket=bucket, record=p)

						print("Writing energy usage to Influx")
						p = Point("Powermeter").tag("Device", msg.topic).field("Energy", energy)
						write_api.write(bucket=bucket, record=p)

					#else:
					#	print("time not up")

			except Exception as e:
				print(e)
				print("Error sending to Influx")

		except:
			print("oof")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("127.0.0.1", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
