import cv2
import numpy as np
from ultralytics import YOLO

class VisionProcessor:
    def __init__(self):
        self.yolo_model = None
        self.frame_width = 1080
        self.frame_height = 720
        self.model_path = 'FireDetectionTest.pt'  # YOLO 模型路徑

        # 顏色輔助辨識用
        self.lower_flame = np.array([0, 220, 160])  # 火焰顏色的 HSV 下界
        self.upper_flame = np.array([20, 255, 255])  # 火焰顏色的 HSV 上界

    def set_frame_size(self, width, height):
        self.frame_width = width
        self.frame_height = height

    def initialize(self):
        """初始化 YOLO 模型"""
        try:
            self.yolo_model = YOLO(self.model_path)
            print("YOLO 模型已初始化")
            # 測試模型
            dummy_frame = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
            self.yolo_model(dummy_frame)
            print("YOLO 模型測試成功")
        except Exception as e:
            print(f"初始化 YOLO 模型時發生錯誤: {str(e)}")
            raise

    def process_frame(self, frame):
        """處理單個視頻幀"""
        try:
            if frame is None:
                return None, []

            frame = cv2.resize(frame, (self.frame_width, self.frame_height))

            # YOLO 檢測
            results = self.yolo_model(frame)
            yolo_detections = self._extract_detections(results)

            # 顏色檢測
            color_detections = self.detect_flame_color(frame)

            # 合併檢測結果
            all_detections = yolo_detections + color_detections

            return frame, all_detections

        except Exception as e:
            print(f"處理幀時發生錯誤: {str(e)}")
            return frame, []

    def _extract_detections(self, results):
        """從 YOLO 結果中提取檢測結果"""
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                if self.yolo_model.names[cls] == 'fire':
                    x1, y1, x2, y2 = box.xyxy[0]
                    detections.append([int(x1), int(y1), int(x2), int(y2)])
        return detections

    def detect_flame_color(self, frame):
        """使用顏色檢測火焰"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_flame, self.upper_flame)

        # 進行形態學操作以減少噪聲
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.dilate(mask, kernel, iterations=2)

        # 找到輪廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        color_detections = []
        for contour in contours:
            if 80000 > cv2.contourArea(contour) > 100:  # 過濾非正常大小區域
                x, y, w, h = cv2.boundingRect(contour)
                color_detections.append([x, y, x + w, y + h])

        return color_detections

    def draw_detections(self, frame, detections):
        """在幀上繪製檢測結果"""
        for x1, y1, x2, y2 in detections:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        return frame

    def display_info(self, frame, drone_info, operation_stage):
        """在幀上顯示無人機信息"""
        cv2.putText(frame, f"battery: {drone_info['battery']}%", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"flying: {'Yes' if drone_info['is_flying'] else 'No'}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"vision: {'On' if drone_info['is_vision_enabled'] else 'Off'}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"auto_mode: {'Auto' if drone_info['auto_mode'] else 'Manual'}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"position: {drone_info['position']}", (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 目標火焰大小信息
        if 'flame_size' in drone_info and drone_info['flame_size'] is not None:
            cv2.putText(frame, f"flame_size: {drone_info['flame_size']:.2f}", (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)
        else:
            cv2.putText(frame, "flame_size: no", (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 顯示操作指示信息
        height, width = frame.shape[:2]
        if operation_stage == 1:
            cv2.putText(frame, "Press 'v' to open detector", (width // 2 - 150, height - 60), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0, 255, 255), 2)
            cv2.putText(frame, "Press 't' to takeoff", (width // 2 - 150, height - 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0, 255, 255), 2)
        elif operation_stage == 2:
            cv2.putText(frame, "Press 'm' Auto_mode on", (width // 2 - 250, height - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        elif operation_stage == 3:
            cv2.putText(frame, "Press 'r' to return", (width // 2 - 150, height - 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0, 255, 255), 2)
        return frame