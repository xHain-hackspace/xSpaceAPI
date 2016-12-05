# coding=utf-8

import os
import sys
import json
import time
import redis
import ConfigParser

from flask             import Flask
from flask             import jsonify

server = Flask(__name__)

def readConfig():
    myConfig = ConfigParser.ConfigParser()
    update   = False

    if os.path.isfile("config.ini"):
        myConfig.read("config.ini")
    else:
        print "Config file not found"
    if not myConfig.has_section('WEBSERVER'):
        print "Adding WEBSERVER part"
        update = True
        myConfig.add_section("WEBSERVER")

    if not myConfig.has_option("WEBSERVER", "Port"):
        print "No webserver port"
        update = True
        myConfig.set("WEBSERVER", "Port", "1234")

    if not myConfig.has_section('REDIS'):
        print "Adding Redis part"
        update = True
        myConfig.add_section("REDIS")

    if not myConfig.has_option("REDIS", "ServerAddress"):
        print "No Server Address"
        update = True
        myConfig.set("REDIS", "ServerAddress", "<ServerAddress>")

    if not myConfig.has_option("REDIS", "ServerPort"):
        print "No Server Port"
        update = True
        myConfig.set("REDIS", "ServerPort", "6379")

    if not myConfig.has_option("REDIS", "Password"):
        print "No Server Port"
        update = True
        myConfig.set("REDIS", "Password", "<passwd>")

    if update:
        with open("config.ini", 'w') as f:
            myConfig.write(f)
            print "Please edit the config file"
            sys.exit()

    return myConfig

def getDefaultObject():
    with open('endpoint.json', 'r') as myfile:
        data = json.load(myfile)
    return data

def prepareRedisEntries():
    myRedis.setex("xHain/door/openstate",              100, True )
    myRedis.setex("xHain/lab/sensor/humidity",         100, 42   )
    myRedis.setex("xHain/lab/sensor/temperature",      100, 33.23)
    myRedis.setex("xHain/lab/sensor/co2",              100, 12345)
    myRedis.setex("xHain/outside/sensor/humidity",     100, 23   )
    myRedis.setex("xHain/outside/sensor/temperature",  100, 13.23)
    myRedis.setex("xHain/member/count",                100, 23   )
    myRedis.setex("xHain/server/spaceapi/callcounter", 100, 0    )

@server.route('/check', methods=['GET'])
def check():
    data = {}
    data['Serverstatus'] = True
    data['Callcounter']  = myRedis.get("xHain/server/spaceapi/callcounter")
    return jsonify(data)

@server.route('/', methods=['GET'])
def getSpaceAPI():
    mySpaceObject = getDefaultObject()
    counter = int(myRedis.get("xHain/server/spaceapi/callcounter"))
    counter += 1
    myRedis.setex("xHain/server/spaceapi/callcounter", 100, counter)
    mySpaceObject['dynamic_generator']['counter']              = counter
    mySpaceObject['dynamic_generator']['generated_utc_time']   = time.time()
    mySpaceObject['state']['open']                             = myRedis.get("xHain/door/openstate")
    mySpaceObject['sensors']['humidity']          [1]['value'] = myRedis.get("xHain/lab/sensor/humidity")
    mySpaceObject['sensors']['temperature']       [1]['value'] = myRedis.get("xHain/lab/sensor/temperature")
    mySpaceObject['sensors']['co2']               [0]['value'] = myRedis.get("xHain/lab/sensor/co2")
    mySpaceObject['sensors']['humidity']          [0]['value'] = myRedis.get("xHain/outside/sensor/humidity")
    mySpaceObject['sensors']['temperature']       [0]['value'] = myRedis.get("xHain/outside/sensor/temperature")
    mySpaceObject['sensors']['total_member_count'][0]['value'] = myRedis.get("xHain/member/count")
    return jsonify(mySpaceObject)

myConfig = readConfig()
myRedis  = redis.StrictRedis(host     = myConfig.get("REDIS", "ServerAddress"),
                             port     = myConfig.get("REDIS", "ServerPort"),
                             password = myConfig.get("REDIS", "Password"),
                             db       = 0)
prepareRedisEntries() # Dummy entries, remove as soon as infrastructure is in place
server.run(debug=False, port=myConfig.get("WEBSERVER", "Port"))
