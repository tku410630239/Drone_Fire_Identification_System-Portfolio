import cv2
import time
import threading
from drone_controller_2 import DroneController
from vision_2 import VisionProcessor
import datetime

class FireFightingDrone:
    def __init__(self):
        self.drone_controller = DroneController()
        self.vision_processor = VisionProcessor()
        self.is_running = False
        self.frame = None
        self.lock = threading.Lock()
        self.operation_stage = 1  # 初始階段 用於顯示資訊
        self.start_time = None
        self.max_height = 0
        self.min_height = float('inf')
        self.log_file = f"drone_log.txt"

    def initialize(self):
        """初始化所有組件"""
        print("初始化無人機系統...")
        self.drone_controller.initialize()
        self.vision_processor.initialize()
        self.vision_processor.set_frame_size(1080, 720)
        if not self.drone_controller.connect():
            print("無法連接到無人機，程序退出")
            return False
        print("初始化完成")
        self.start_time = datetime.datetime.now()
        return True

    def run(self):
        """運行主程序循環"""
        self.is_running = True
        video_thread = threading.Thread(target=self._video_loop)
        video_thread.start()

        try:
            while self.is_running and not self.drone_controller.emergency_stop.is_set():
                self._process_user_input()
                self._update_drone_state()
                self._update_height_records()
                time.sleep(0.1)  # 避免CPU過度使用
        except KeyboardInterrupt:
            print("程序被用戶中斷")
        finally:
            self.cleanup()
            self._write_log()

    def _video_loop(self):
        """視頻處理循環"""
        while self.is_running and not self.drone_controller.emergency_stop.is_set():
            frame = self.drone_controller.get_frame()
            if frame is not None:
                with self.lock:
                    self.frame = frame.copy()
            time.sleep(0.03)  # 約30 FPS

    def _process_user_input(self):
        """處理用戶輸入"""
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            self.is_running = False
        elif key == ord('t'):
            self._toggle_takeoff_land()
            if self.drone_controller.is_flying and self.operation_stage == 1:
                self.operation_stage = 2
        elif key == ord('v'):
            self.drone_controller.toggle_vision()
            if self.drone_controller.is_vision_enabled and self.operation_stage == 1:
                self.operation_stage = 2
        elif key == ord('m'):
            self.drone_controller.toggle_mode()
            if self.drone_controller.auto_mode and self.operation_stage == 2:
                self.operation_stage = 3
        elif key == ord('x'):
            self.drone_controller.emergency_land()
        elif key == ord('w'):
            self.drone_controller.adjust_position(2,4,2,0)
            time.sleep(0.5)
        elif key == ord('a'):
            self.drone_controller.adjust_position(0,2,2,0)
            time.sleep(0.5)
        elif key == ord('s'):
            self.drone_controller.adjust_position(2,0,2,0)
            time.sleep(0.5)
        elif key == ord('d'):
            self.drone_controller.adjust_position(4,2,2,0)
            time.sleep(0.5)
        elif key == ord('q'):
            self.drone_controller.adjust_position(2,2,4,0)
            time.sleep(0.5)
        elif key == ord('e'):
            self.drone_controller.adjust_position(2,2,0,0)
            time.sleep(0.5)
        elif key == ord('r'):
            if not self.drone_controller.auto_mode:
                self.drone_controller.return_to_start()

    def _toggle_takeoff_land(self):
        """切換起飛/降落狀態"""
        if not self.drone_controller.is_flying:
            self.drone_controller.takeoff()
        else:
            self.drone_controller.land()

    def _update_drone_state(self):
        try:
            with self.lock:
                if self.frame is None:
                    print("警告：沒有可用的幀")
                    return

                frame = self.frame.copy()

            flame_size = None # 用於紀錄目標火焰大小

            if self.drone_controller.is_vision_enabled:
                frame, detections = self.vision_processor.process_frame(frame)

                frame = self.vision_processor.draw_detections(frame, detections)

                # 計算火焰大小

                if detections:
                    # 假設最大的檢測框是主要目標
                    largest_detection = max(detections, key=lambda d: (d[2] - d[0]) * (d[3] - d[1]))
                    flame_size = (largest_detection[2] - largest_detection[0]) * (
                                largest_detection[3] - largest_detection[1])

                if self.drone_controller.auto_mode and self.drone_controller.is_flying:
                    self._handle_auto_mode(detections)

            drone_info = self._get_drone_info()
            drone_info['flame_size'] = flame_size  # 添加火焰大小信息
            frame = self.vision_processor.display_info(frame, drone_info, self.operation_stage)

            cv2.imshow("Fire Fighting Drone", frame)
        except Exception as e:
            print(f"更新無人機狀態時發生錯誤: {str(e)}")
            import traceback
            traceback.print_exc()

    def _handle_auto_mode(self, detections):
        """處理自動飛行模式"""
        if detections:
            target_flame = max(detections, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))
            continue_auto = self.drone_controller.move_to_flame(target_flame,
                                                                self.vision_processor.frame_width,
                                                                self.vision_processor.frame_height)
            if not continue_auto:
                print("自動模式結束，已成功抵達目標面前")

        else:
            self.drone_controller.adjust_position(0, 0, 0, 0)  # 保持懸停

    def _get_drone_info(self):
        """獲取無人機信息"""
        return {
            'battery': self.drone_controller.get_battery(),
            'is_flying': self.drone_controller.is_flying,
            'is_vision_enabled': self.drone_controller.is_vision_enabled,
            'auto_mode': self.drone_controller.auto_mode,
            'position': self.drone_controller.position,
        }

    def cleanup(self):
        print("正在清理資源...")
        self.is_running = False
        if self.drone_controller.is_flying:
            print("正在降落無人機...")
            self.drone_controller.land()
        print("正在斷開無人機連接...")
        self.drone_controller.disconnect()
        print("正在關閉所有窗口...")
        cv2.destroyAllWindows()
        print("清理完成")

    def _update_height_records(self):
        current_height = self.drone_controller.get_height() / 100  # 轉換為公尺
        self.max_height = max(self.max_height, current_height)
        self.min_height = min(self.min_height, current_height)

    def _write_log(self):
        end_time = datetime.datetime.now()
        with open(self.log_file, 'w') as f:
            f.write(f"1\n")
            f.write(f"{self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Taipei\n")
            f.write(f"{self.max_height:.2f}\n")
            f.write(f"{self.min_height:.2f}\n")
            f.write(f"1\n")
        print(f"飛行日誌已保存至 {self.log_file}")

if __name__ == "__main__":
    fire_fighting_drone = FireFightingDrone()
    if fire_fighting_drone.initialize():
        fire_fighting_drone.run()
    else:
        print("初始化失敗，程序退出")