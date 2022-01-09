import tensorflow as tf

'''
to run only interpreter uncomment the line below
'''
# import tflite_runtime.interpreter as tflite
import config
import numpy as np
import cv2

input_mean = 127.5
input_std = 127.5


def load_labels(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]


def detect(frame):
    interpreter = tf.lite.Interpreter(model_path=config.modelFile)
    '''
    to run only interpreter uncomment the line below
    '''
    # interpreter = tflite.Interpreter(model_path=config.modelFile)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # check the type of the input tensor
    floating_model = input_details[0]['dtype'] == np.float32

    # NxHxWxC, H:1, W:2
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    img = cv2.resize(frame, (width, height))
    (ih, iw, ch) = frame.shape

    # add N dim
    input_data = np.expand_dims(img, axis=0)

    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    interpreter.set_tensor(input_details[0]['index'], input_data)

    interpreter.invoke()

    roi_coordinates = interpreter.get_tensor(output_details[0]['index'])[0]
    class_names = interpreter.get_tensor(output_details[1]['index'])[0]
    probability = interpreter.get_tensor(output_details[2]['index'])[0]
    coordinates = []
    labels = load_labels(config.labelPath)
    object_name = ""
    for i in range(len(probability)):
        if probability[i] > 0.9 and probability[i] < 1.0:
            Xa = roi_coordinates[i][3] * iw
            Ya = roi_coordinates[i][2] * ih
            Xb = roi_coordinates[i][1] * iw
            Yb = roi_coordinates[i][0] * ih
            yC = (Yb + Ya) / 2 - Yb / 2
            xC = (Xb + Xa) / 2
            coordinates.append(xC)
            coordinates.append(yC)
            cv2.rectangle(frame, (int(Xa), int(Ya)), (int(Xb), int(Yb)), (255, 00, 0), 2)
            object_name = labels[int(class_names[i])]
            cv2.putText(frame, object_name, (int(Xb), int(Yb)), cv2.FONT_HERSHEY_SIMPLEX, (1), (0, 0, 255), 2)

        return (frame, object_name, coordinates)
