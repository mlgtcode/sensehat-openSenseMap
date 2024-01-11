#!/usr/bin/env python3

from sense_hat import SenseHat
import subprocess, datetime, json, toml, requests

conf = toml.load("default.toml")
kkey = conf['sensekeys']
aapi = conf['senseauth']

def wifi_signal():
    process = subprocess.Popen("iwconfig wlan0", stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    for line in output.split(b'\n'):
        if b"Signal level" in line:
            wifi_dbm = int(line.split(b'=')[2].split(b' ')[0])
            return wifi_dbm

sense = SenseHat()
sense.clear()

pressure = round(sense.get_pressure(),2)
temp1 = round(sense.get_temperature_from_pressure(),2)
temp2 = round(sense.get_temperature_from_humidity(),2)
humidity = round(sense.get_humidity(),2)
wifi = wifi_signal()
ts = datetime.datetime.utcnow().isoformat("T")+"Z"

response = requests.post("https://api.opensensemap.org/boxes/"+aapi['senseboxid']+"/data",
                json={
                    kkey['temp1']: [temp1, ts],
                    kkey['humidity']: [humidity, ts],
                    kkey['pressure']: [pressure, ts],
                    kkey['temp2']: [temp2, ts],
                    kkey['wifi']: [wifi, ts],
                },
                headers={
                    "content-type": "application/json",
                    "Authorization": aapi['apikey'],
                },
                timeout=20
            )

if aapi['debug'] is True:
    print("Sensebox API retuned following response:")
    print (response.json())

print("----- Sensor data (%s) -----" %ts)
print("Pressure: %s Millibars" % pressure)
print("Humidity: %s" % humidity)
print("Temperature from pressure sesnor: %s" % temp1)
print("Temperature from humidity sesnor: %s" % temp2)
print("WiFi: %s dBm" % wifi)
