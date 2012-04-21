from pyfaze import AnafazeController as AFC
a = AFC('/dev/ttyUSB0', 9600)

print a.ambient_sensor_readings
