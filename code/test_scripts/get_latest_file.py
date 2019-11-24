import glob
import os

import camera

list_of_files = glob.glob("/home/pi/motion/camera1" + '/*-snapshot.jpg')
latest_file = max(list_of_files, key=os.path.getctime)
print(latest_file)
