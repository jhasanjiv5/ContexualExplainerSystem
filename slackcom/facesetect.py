import cv2

frontal_face_Cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
profile_face_Cascade = cv2.CascadeClassifier("haarcascade_profileface.xml")


def detect_faces(image):
    # img = cv2.imread(image)
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    front_faces = frontal_face_Cascade.detectMultiScale(
        gray_img,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(1, 1),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    profile_faces = profile_face_Cascade.detectMultiScale(
        gray_img,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(1, 1),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    for faces in [front_faces, profile_faces]:
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)


    return len(front_faces)+len(profile_faces),image




