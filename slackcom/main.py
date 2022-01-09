import pamclient

import threading

# def capture_thread_func():
#     import cv2
#     frame = capture.videoStream()
#     detect_image, object_name, _ = tfdetect.detect(frame)
#     cv2.imwrite('detected-frame/detected-frame.jpg', detect_image)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bot_thread = threading.Thread(target=pamclient.connectbot)
    #capture_thread = threading.Thread(target=capture_thread_func)
    bot_thread.start()
    # capture_thread.start()







