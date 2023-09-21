""" Libraries """
#Libraries for Face Recognition
import face_recognition

#libraries from EmotionRec
from keras.preprocessing.image import img_to_array
import imutils
from keras.models import load_model

#Libraries from both
import cv2
import numpy as np

#Other Libraries
import conversation

global label
global complete
global test
global n
global oldName

test = "none"
oldName = "none"
n = 0

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

""" FaceRec """
# Load a sample picture and learn how to recognize it.
selin_image = face_recognition.load_image_file("images/selin.jpg")
selin_face_encoding = face_recognition.face_encodings(selin_image)[0]

# Load a second sample picture and learn how to recognize it.
altug_image = face_recognition.load_image_file("images/altug.jpg")
altug_face_encoding = face_recognition.face_encodings(altug_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    selin_face_encoding,
    altug_face_encoding
    ]
known_face_names = [
    "Selin",
    "Altug"
    ]

""" EmotionRec """
# parameters for loading data and images
detection_model_path = 'haarcascade_files/haarcascade_frontalface_default.xml'
emotion_model_path = 'models/_mini_XCEPTION.102-0.66.hdf5'

# hyper-parameters for bounding boxes shape
# loading models
face_detection = cv2.CascadeClassifier(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)
EMOTIONS = ["angry" ,"disgust","scared", "happy", "sad", "surprised", "neutral"]

    # Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    test = "none"
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detection.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)

            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)
            
            if len(faces) > 0:
                faces = sorted(faces, reverse=True,
                key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
                (fX, fY, fW, fH) = faces
                # Extract the ROI of the face from the grayscale image, resize it to a fixed 28x28 pixels, and then prepare
                # the ROI for classification via the CNN
                roi = gray[fY:fY + fH, fX:fX + fW]
                roi = cv2.resize(roi, (64, 64))
                roi = roi.astype("float") / 255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)

                preds = emotion_classifier.predict(roi)[0]
                emotion_probability = np.max(preds)
                label = EMOTIONS[preds.argmax()]
                complete = name, label
                complete = ', '.join(complete)
                n = 1
                
            
            

    process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name,(left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    
    # Display the resulting image
    cv2.imshow('Video', frame)

    #Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if n == 1:
        if oldName == name:
            continue
        else:
            test = complete
            test = test.split(", ")
            oldName = name
            conversation.conversationStart(test[0], test[1])
            continue
    
"""    
# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()"""