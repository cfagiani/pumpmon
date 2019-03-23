Ultrasonic Sump Pump Monitor
============================

This project uses an ultrasonic range finder to detect the distance between the sensor the the water level in a sump 
pump. Readings are stored in a SQLite database and can be retrieved either via a Rest API or viewed with a simple
time series graph.


Requirements:
flask - (unless running headless)


Invocation:
sudo nohup python3 pumpmon.py & 
