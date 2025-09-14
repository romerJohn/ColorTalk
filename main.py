import cv2
import numpy as np
import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # speed
engine.setProperty('volume', 1)  # volume

selected_color = None
selected_color_name = None

def speak(text):
    engine.stop()   # clear old speech queue
    engine.say(text)
    engine.runAndWait()

def get_color_name(bgr_color):
    # Convert BGR to HSV
    c = np.uint8([[bgr_color]])
    hsvC = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)
    h, s, v = hsvC[0][0]

    # Simple ranges for basic colors (can be refined)
    if h < 10 or h >= 170:
        return "Red"
    elif 10 <= h < 25:
        return "Orange"
    elif 25 <= h < 35:
        return "Yellow"
    elif 35 <= h < 85:
        return "Green"
    elif 85 <= h < 125:
        return "Blue"
    elif 125 <= h < 170:
        return "Purple"
    else:
        return "Unknown"

def pick_color(event, x, y, flags, param):
    global selected_color, selected_color_name, frame
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_color = frame[y, x].tolist()  # BGR color at click
        selected_color_name = get_color_name(selected_color)
        print(f"Selected color (BGR): {selected_color}, Color: {selected_color_name}")
        speak(selected_color_name)  # always speak on click

def get_limits(color):
    c = np.uint8([[color]])
    hsvC = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)
    h = hsvC[0][0][0]
    lowerLimit = (h - 10, 100, 100)
    upperLimit = (h + 10, 255, 255)
    return np.array(lowerLimit, np.uint8), np.array(upperLimit, np.uint8)

cap = cv2.VideoCapture(0)
cv2.namedWindow("ColorTalk")
cv2.setMouseCallback("ColorTalk", pick_color)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if selected_color is not None:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower, upper = get_limits(selected_color)
        mask = cv2.inRange(hsv, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if cv2.contourArea(cnt) > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                if selected_color_name:
                    cv2.putText(frame, selected_color_name, (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("ColorTalk", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    if cv2.getWindowProperty("ColorTalk", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
