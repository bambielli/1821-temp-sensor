import os
from datetime import datetime

def get_sensor_name():
    for i in os.listdir('/sys/bus/w1/devices'):
        if i != 'w1_bus_master1':
            sensor = i
    return sensor

def read(sensor):
    location = f"/sys/bus/w1/devices/{sensor}/w1_slave"
    tfile = open(location)
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    celsius = temperature / 1000
    farenheit = (celsius * 1.8) + 32
    time = datetime.now().isoformat()
    return celsius, farenheit, time

def loop(sensor):
    while True:
        temp_vals = read(sensor)
        if temp_vals != None:
            celsius, farenheit, time = temp_vals
            print(f"time : {time}")
            print(f"Current temp : {celsius} C")
            print(f"Current temp : {farenheit} F")

def kill():
    quit()

if __name__ == "__main__":
    try:
        sensor = get_sensor_name()
        loop(sensor)
    except KeyboardInterrupt:
        kill()
