import cv2
import datetime
import os
from ultralytics import YOLO
import pyttsx3
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

# from communication import led_on, led_off

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Loading pretrained YOLO model (will be downloaded on first run)
model = YOLO("model/yolov8n.pt", "v8")

# Load the Keras model for bird classification
bird_model = load_model("birdsmodel.h5")

# Set dimensions of video frames
frame_width = 1280
frame_height = 720

# Video source is MP4 file stored locally
cap = cv2.VideoCapture(0)

# Only save an image on frame 0
frame_count = 0

if not cap.isOpened():
    print("Cannot open video stream")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("No video frame available")
        break
    
    # Resize the frame
    frame = cv2.resize(frame, (frame_width, frame_height))

    # Do prediction on image, with confidence greater than 80%
    detect_params = model.predict(source=[frame], conf=0.8, save=False)

    DP = detect_params[0].numpy()

    if len(DP) != 0:
        for i in range(len(detect_params[0])):

            boxes = detect_params[0].boxes
            box = boxes[i]
            clsID = box.cls.numpy()[0]
            conf = box.conf.numpy()[0]
            bb = box.xyxy.numpy()[0]
            c = box.cls
            # Name of object detected (e.g. 'bird')
            class_name = model.names[int(c)]

        # If the class name contains the word 'bird', do something with the frame
        if 'bird' in class_name.lower():

            if frame_count == 0:
                current_time = datetime.datetime.now()
                filename = os.path.join("images", current_time.strftime("bird_%Y-%m-%d_%H-%M-%S-%f.jpg"))
                success = cv2.imwrite(filename, frame)

            if frame_count == 10:
                frame_count = 0
            else:
                frame_count += 1

            # Extract the detected bird region and preprocess it for the bird model
            bird_region = frame[int(bb[1]):int(bb[3]), int(bb[0]):int(bb[2])]
            bird_region = cv2.resize(bird_region, (224, 224))  # Assuming the model expects 224x224 input size
            bird_region = bird_region.astype("float") / 255.0
            bird_region = img_to_array(bird_region)
            bird_region = np.expand_dims(bird_region, axis=0)

            # Classify the bird using the bird model
            bird_pred = bird_model.predict(bird_region)
            print(bird_pred)
            bird_class = np.argmax(bird_pred, axis=1)[0]
            bird_conf = bird_pred[0][bird_class]


            print(f"Confidenence = {bird_conf}")

            if bird_conf > 0.95 :
                # Assuming you have a list of bird species names corresponding to the model's output classes
                bird_names = ["swan", "parrot", "sparow"]  # Modify with your actual class names
                bird_name = bird_names[bird_class]

                # Draw green rectangle around the object
                cv2.rectangle(
                    frame,
                    (int(bb[0]), int(bb[1])),
                    (int(bb[2]), int(bb[3])),
                    (0, 255, 0),
                    3,
                )
                # Add some text labelling to the rectangle
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(
                    frame,
                    bird_name + " " + str(round(bird_conf, 3)) + "%",
                    (int(bb[0]), int(bb[1]) - 10),
                    font,
                    1,
                    (255, 255, 255),
                    2,
                )

                # led_on()

                engine.say(f"{bird_name} has been detected")

                # Wait for speech to finish
                engine.runAndWait()

            else:
                # led_off()
                pass

    # Display the frame onscreen
    cv2.imshow("Object Detection", frame)

    # End program when q is pressed
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

