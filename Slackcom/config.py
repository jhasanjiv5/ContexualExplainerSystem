
from pathlib import Path
home = str(Path.home())

frozenInferenceGraph = r'pre-trained-set/frozen_inference_graph.pb'
trainNodeDescription = r'pre-trained-set/output.pbtxt'

rawImagePath = r'images/61-402layout.png'

stopWordsPath = 'stop-words.txt'

windowSize = (8, 8)

imageResolution = (720, 1080)
faceClassifierAddress = home + \
    r'/downloads/opencv-3.4/data/haarcascades/haarcascade_frontalface_default.xml'
'''
to run on raspberry pi uncomment the line below 'saved opencv-3.4.0 folder inside the local folder'
'''
#faceClassifierAddress= r'opencv-3.4.0/data/haarcascades/haarcascade_frontalface_default.xml'
captureDuration = 43200
sleepDuration = 0

outputPath = r'output/'

defaultDistance = 50
changeThreshold =50
changeAreaMin =50
changeAreaMax =300


modelFile = r'tflite_models/detect.tflite'
labelPath = r'tflite_models/person-labelmap.txt'

inputImageSize = (640, 480)
blurrSize = (31, 31)

roomBrightnessThreshold=50

furnitureCoordinates = {
    "table": {"x": 250, "y": 130, "w": 180, "h": 108},
    "whiteBoard": {"x": 320, "y": 350, "w": 150, "h": 150},
    "glassBoard":{"x": 50, "y": 150, "w": 110, "h": 90}
    
}

occupancy = {
    0: "unknown",
    1: "Warm",
    2: "Cold",
    3: "Free"
}

blue = 'b'
green = 'g'
red = 'r'
cyan = 'c'
magenta = 'm'
yellow = 'y'
black = 'k'
white = 'w'

googleDriveUploadAllowed = 0

testMode = 0