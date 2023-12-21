import cv2
import mediapipe as mp
import math
import serial
# הגדרת הפורט ומהירות השידור
ser = serial.Serial('COM3', 9600)
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils
finger_coord = [(8, 6), (12, 10), (16, 14), (20, 18)]
thumb_coord = (4, 2)

while True:
    success, image = cap.read()
    if not success:
        break

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_image)
    multi_landmarks = results.multi_hand_landmarks

    if multi_landmarks:
        all_hand_points = []
        for hand_landmarks in multi_landmarks:
            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            hand_points = []
            for idx, lm in enumerate(hand_landmarks.landmark):
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                hand_points.append((cx, cy))
                cv2.circle(image, (cx, cy), 2, (208, 224, 64), 2)
            all_hand_points.append(hand_points)

        total_up_count = 0
        for hand_points in all_hand_points:
            up_count = 0
            for coordinate in finger_coord:
                if hand_points[coordinate[0]][1] < hand_points[coordinate[1]][1]:
                    up_count += 1

            if hand_points[thumb_coord[0]][0] > hand_points[thumb_coord[1]][0]:
                up_count += 1

            total_up_count += up_count
            
            
            # מרחק בין האגודל לאחות האצבעות
            distance = math.dist(hand_points[thumb_coord[0]], hand_points[finger_coord[0][0]])
            # חישוב אחוזים לפי המרחק
            percentage = (distance / image.shape[1]) * 100  # כדי להתאים לגודל התמונה
            
            if  0<= total_up_count <= 5:
                ser.write(str(total_up_count).encode())
                 
        cv2.putText(image, str(total_up_count), (20, 50), cv2.FONT_HERSHEY_PLAIN, 4, (200, 255, 0), 4)

        bar_length = int(percentage * 4)  # אורך הבר כל פרוסנט = 4 פיקסלים
        cv2.rectangle(image, (20, 420 - bar_length), (30, 420), (0, 255, 0), -1)


        cv2.putText(image, f'{percentage:.2f}%', (20, 460), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)


    cv2.imshow("Counting number of fingers", image)
    if cv2.waitKey(1) & 0xFF == 27:  # לחיצה על ESC
        break

cap.release()
cv2.destroyAllWindows()
