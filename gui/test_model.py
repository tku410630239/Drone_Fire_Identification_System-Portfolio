import math
import cv2
import time
import logging
import numpy as np
from ultralytics import YOLO

# 初始化 YOLOv8 模型
model = YOLO("FireDetectionTest.pt")
classNames = ['fire', 'smoke']

# 打開影片文件
cap = cv2.VideoCapture("video.mp4")

# 初始化日志紀錄器
logging.basicConfig(filename='fire_detection_every_second.log', level=logging.INFO, format='%(asctime)s %(message)s')

class Fire:
    def __init__(self, box):
        self.box = box
        self.center = ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2)
        self.first_detected = time.time()
        self.last_detected = self.first_detected

fires = {}
total_fires_detected = 0
fire_center_threshold = 200
fire_persistence_threshold = 5
last_log_time = 0

def get_box_color(area):
    if area < 1000:
        return (0, 255, 0)
    elif area < 5000:
        return (255, 0, 0)
    else:
        return (0, 0, 255)

def is_same_fire(center1, center2):
    return math.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) < fire_center_threshold

def update_fire_tracking(fires, current_time):
    expired_fires = [fire_id for fire_id, fire in fires.items() if current_time - fire.last_detected > fire_persistence_threshold]
    for fire_id in expired_fires:
        del fires[fire_id]

def calculate_average_center(fires):
    if not fires:
        return None
    total_x, total_y = 0, 0
    for fire in fires.values():
        center_x, center_y = fire.center
        total_x += center_x
        total_y += center_y
    return (total_x // len(fires), total_y // len(fires))

def display_data(window_name, total_fires, current_fire_count, max_fire_box, avg_confidence):
    info_image = np.zeros((300, 600, 3), dtype=np.uint8)
    cv2.putText(info_image, f"Total fires detected: {total_fires}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    cv2.putText(info_image, f"Current fire count: {current_fire_count}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    if max_fire_box:
        cv2.putText(info_image, f"Max fire box: ({max_fire_box[0]}, {max_fire_box[1]}) to ({max_fire_box[2]}, {max_fire_box[3]})", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    cv2.putText(info_image, f"Avg confidence: {avg_confidence:.2f}", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    cv2.imshow(window_name, info_image)

def display_center_position(window_name, avg_center, frame_size):
    if avg_center:
        center_img = np.zeros((200, 200, 3), dtype=np.uint8)
        scaled_x = int((avg_center[0] / frame_size[1]) * 200)
        scaled_y = int((avg_center[1] / frame_size[0]) * 200)
        cv2.circle(center_img, (scaled_x, scaled_y), 5, (0, 255, 0), -1)
        cv2.putText(center_img, f"Center: {avg_center}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.imshow(window_name, center_img)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, stream=True)
    current_time = time.time()
    current_confidences = []

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            area = (x2 - x1) * (y2 - y1)
            center = ((x1 + x2) // 2, (y1 + y2) // 2)
            new_fire = True
            conf = box.conf
            current_confidences.append(conf)

            for fire_id, fire in fires.items():
                if is_same_fire(center, fire.center):
                    fire.last_detected = current_time
                    fire.box = (x1, y1, x2, y2)
                    fire.center = center
                    new_fire = False
                    break

            if new_fire:
                fire_id = len(fires) + 1
                fires[fire_id] = Fire((x1, y1, x2, y2))
                total_fires_detected += 1

            color = get_box_color(area)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    update_fire_tracking(fires, current_time)

    fire_count = len(fires)
    max_fire_box = max(fires.values(), key=lambda f: (f.box[2] - f.box[0]) * (f.box[3] - f.box[1]), default=None).box if fires else None
    avg_center = calculate_average_center(fires)
    avg_confidence = np.mean(current_confidences) if current_confidences else 0

    if current_time - last_log_time >= 1:
        logging.info(f"Total fires detected: {total_fires_detected}, Current fire count: {fire_count}, Max fire box: {max_fire_box}, Avg confidence: {avg_confidence:.2f}, Center position: {avg_center}")
        last_log_time = current_time

    display_data("Fire Data", total_fires_detected, fire_count, max_fire_box, avg_confidence)
    display_center_position("Fire Center Position", avg_center, frame.shape[:2])

    cv2.imshow("Fire Detection(press q to exit)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
