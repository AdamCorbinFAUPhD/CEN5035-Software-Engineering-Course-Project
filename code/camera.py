import subprocess
from time import sleep
from threading import Thread
import logging

url = 'http://127.0.0.1:8080/0'

photo_cmd = '/action/snapshot'

start_video_cmd = '/config/set?emulate_motion=on'

stop_video_cmd = '/config/set?emulate_motion=off'

VIDEO_TIME = 20

NUM_PHOTOS = 1

module_logger = logging.getLogger('AlarmSystem.camera')

# The target_dir is the path where the photos will be stored. To change this you need to edit the
# target_dir in  /etc/motion/motion.conf
target_dir = "/home/pi/motion/camera1"


def take_photo():
    """
    Take a single photo from the camera.
    """
    full_url = url + photo_cmd
    command = ['curl', '-s', full_url]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    # out, err = process.communicate()
    module_logger.info("Photo taken")


def take_alarm_photos():
    """
    Takes the number of specified alarm photos. Starts the alarm photos thread.
    """
    t = Thread(target=_alarm_photos_thread, args=())
    t.start()


def _alarm_photos_thread():
    """
    Takes the number of specified photos when an alarm is triggered. Waits 1 second between photos.
    """
    for i in range(0, NUM_PHOTOS):
        take_photo()
        sleep(1)


def take_video():
    """
    Take a video. Starts the video thread.
    """
    t = Thread(target=_video_thread, args=())
    t.start()


def _video_thread():
    """
    Calls the emulate_motion config change, waits for the length of the video, then turns emulate_motion off
    """
    full_url = url + start_video_cmd
    command = ['curl', '-s', full_url]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    # out, err = process.communicate()
    module_logger.info("Video started")
    sleep(VIDEO_TIME)
    full_url = url + stop_video_cmd
    command = ['curl', '-s', full_url]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    # out, err = process.communicate()
    module_logger.info("Video completed")
