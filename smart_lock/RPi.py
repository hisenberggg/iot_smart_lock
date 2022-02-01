from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
#SETUP CODE
relay_pin = [26]
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.OUT)
GPIO.output(relay_pin, 0)
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))
#SUCCESSFUL FACIAL RECOGNITION
GPIO.output(relay_pin, 1) #SENDS SIGNAL TO RPi TO UNLOCK DOOR
#UNSUCCESSFUL FACIAL RECOGNITION
GPIO.output(relay_pin, 0) #SENDS SIGNAL TO RPi TO KEEP THE DOOR LOCKED ONLY