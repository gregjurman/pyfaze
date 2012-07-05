import eeml
from pyfaze import AnafazeController as AFC

from time import sleep

import eeml_config

a = AFC('/dev/ttyUSB0', 9600)

# parameters
API_KEY = eeml_config.API_KEY
API_URL = 56611

cosm = eeml.Cosm(API_URL, API_KEY)

print "Starting loop"

while True:
    try:
        in_val = a.ambient_sensor_readings / 10.0
        print "Current Value (Indoor):", in_val

        out_val = a.process_variable[0] / 10.0
        print "Current Value (Outdoor):", out_val

        cosm.update([
            eeml.Data("indoor", in_val, unit=eeml.Fahrenheit()),
            eeml.Data("outdoor", out_val, unit=eeml.Fahrenheit()),
            ])

        cosm.put()

        print "    Cosm updated:"
        print "        Indoor: ", in_val
        print "       Outdoor: ", out_val
        sleep(300) # sleep for 5 minutes

    except AttributeError as ae:
        print "Whoops, failed to get an attribute"
