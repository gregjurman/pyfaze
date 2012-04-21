import eeml
from pyfaze import AnafazeController as AFC

from time import sleep

import eeml_config

a = AFC('/dev/ttyUSB0', 9600)

# parameters
API_KEY = eeml_config.API_KEY
API_URL = 56611

pac = eeml.Pachube(API_URL, API_KEY)

while True:
    pac.update([eeml.Data("ambient", a.ambient_sensor_readings / 10.0, unit=eeml.Fahrenheit())])
    pac.put()
    sleep(300)
