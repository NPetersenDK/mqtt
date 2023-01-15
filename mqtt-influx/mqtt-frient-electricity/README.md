# MQTT-Influx Frient
Getting Frient Electricity Meter Interface into Influx nice and easy with the help of Python.
Please only use as inspirational, modify if needed.

# How?
- Search/Replace: "NameOnDevice" with the name you have given it in fx zigbee2mqtt
- Power_false_timeout: Can be set to the timeout you want before pushing data to the LONGTERM bucket.
- Run

## Requirements:
- Python3.x
  - Modules in the requirements.txt
- A InfluxDB 2.x server
    - Two InfluxDB buckets with write access.
- A Frient Electricity Meter: https://frient.com/products/electricity-meter-interface/