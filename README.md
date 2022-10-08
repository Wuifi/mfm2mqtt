# mfm2mqtt
A tiny middleware to forward the data from mains frequency measurement board to mqtt
This Python scripts grabs content of the mfm-board and publishes the data to an MQTT-Broker.
the mfm-board hardware is described in detail in the
"[mains-frequency-measure](https://gitlab.com/Wuifi/mains-frequency-measure/)"  repo. 

**Why MQTT?**
MQTT was chosen, because it is (from my point of view) the most flexible solution to process the data further on.
In my use case, there is a telegraf instance running, that forwards all MQTT data to InfluxDB, thus no additional Interface from "field level" to the monitoring instance. A nice benefit is the possibility to integrate the MQTT stream into Node-Red or any other automation system such as OpenHAB etc.

## Setup

** CAUTION**
From IT_Security Point-of-View, the whole script might be a nightmare!
Feel free to enhance and contribute!

### Verify access to serial connection
run the script in folder `python3 /debug/mfm_serial_test.py' for a first vaildation of the connectivity to your mfm-board

### Set environment variables with the relevant details (e.g. via docker-compose)  
*** noch nicht implementiert!***
* For Interface to mfm-ATMega328p Board
  * `MFM_SERIAL_PORT`=/dev/ttyS0`
  * `NOMINAL_FREQUENCY`=50
  * `SCRAPE_INTERVAL`=0.1 # os.environ.get('SCRAPE_INTERVAL')
* For MQTT Broker:
  * `MQTT_TOPIC` = `"MFM"`
  * `MQTT_HOST` =`"127.0.0.1"`
  * `MQTT_USERNAME`=`<your_username>`  < Runs currently without authentification!
  * `MQTT_PASSWORD`=`<your_password>`  < Runs currently without authentification!

### Internal variables, that can be easily added to the environment variables as well:  
  * `MQTT_PORT`=`1883`
  * `MQTT_CLIENT_ID`=`""`
  * `MQTT_KEEPALIVE`=`60`
  * `MQTT_WILL`=`None`
  * `MQTT_TLS`=`None`
  * `SCRAPE_INTERVAL`

### create docker container
build the container from a terminal:
`sudo docker build -t mfm2mqtt:latest .`

`sudo docker run mfm2mqtt --name mfm2mqtt mfm2mqtt/app`

building the container with docker-compose
`docker-compose up`

 * Run `python3 app.py`


## Description of the runtime sequence
- get data
- convert to json
- create mqtt message
- publish message

## Missing features:
- exception handling  **not yet implemented**
  - connection errors
    - route to mfm-board
    - route to MQTT Broker
  - data inconsistency
  - etc. etc.
- interface to docker logging console

## Problems to be solved:
- Docker container environment ==> 
-  how to make sure that the latest lib is used?
- container stops with "exit code 1" after almost any issue ==> the solution shall be robust against any external connectivity problems such as a restart of another instance of loss of communication
- runtime monitoring shall provide (detailed) information on the issue causing the container to break.

## use cases for data consumption
### Grafana

By logging the data with this script it's easily possible to create a nice
Grafana Dashboard to display some of the interesting data.

### NODE-RED
**... to be developped**


## Note

This is just a quick-and-dirty script to grab to content
