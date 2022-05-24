import configparser
import os
import sys


sys.path.append(os.path.abspath('..'))
#sys.path.append(os.path.abspath('../..'))
#from tools.ockjwt import OckRandom
from ntools.net import *

if (__name__ == '__main__'):
    config = configparser.ConfigParser()
    configFileName = "config/ock.cfg"
    if os.path.isfile(configFileName):
        print("Config file found")
    else:
        print("Config file is missing!")
        sys.exit("\nConfig file not found")

    config.read(configFileName)

    if len(sys.argv) <= 2:
        print("Usage: python3 ock-manager.py system action")


    setup = "okta"
    if len(sys.argv) > 1:
        setup = sys.argv[1]

    url = config[setup]["server"]
    print(str(ping(url)))

    #dirName = OckRandom.randomString(8)
    #print(dirName)

