import time
import threading
import numpy as np
from djitellopy import Tello

class DroneController:
    def __init__(self):
        # 初始化無人機控制相關的屬性
        self.tello = None
        self.is_connected = False
        self.is_flying = False
        self.is_vision_enabled = False
        self.auto_mode = False
        self.emergency_stop = threading.Event()
        self.position = Position()
        self.initial_position = Position()

        # 定義固定的移動速度選項
        self.SPEED_OPTIONS = [-20, -10, 0, 10, 20]

        # 其他控制相關的屬性
        self.command_interval = 0.5
        self.last_command_time = 0
        self.command_lock = threading.Lock()

        # 電池檢查相關
        self.battery = None
        self.last_battery_check = 0
        self.battery_check_interval = 60  # 每60秒檢查一次電池

        # 保持命令相關
        self.keepalive_interval = 2  # 每3秒發送一次保持命令
        self.keepalive_thread = None
        self.stop_keepalive = threading.Event()

    def initialize(self):
        """初始化無人機連接"""
        self.tello = Tello()

    def connect(self):
        """連接到無人機"""
        try:
            self.tello.connect()
            self.tello.streamon()
            self.is_connected = True
            print("成功連接到Tello")
            self.start_keepalive_thread()
            if self.is_connected:
                self.battery = self.tello.get_battery()
                self.last_battery_check = time.time()
            return True
        except Exception as e:
            print(f"連接Tello時發生錯誤: {str(e)}")
            return False

    def disconnect(self):
        """斷開與無人機的連接"""
        self.stop_keepalive_thread()
        if self.tello:
            try:
                if self.is_flying:
                    self.land()
                self.tello.end()
                print("已安全斷開與Tello的連接")
            except Exception as e:
                print(f"斷開連接時發生錯誤: {str(e)}")
            finally:
                self.tello = None
                self.is_flying = False

    def takeoff(self):
        """控制無人機起飛"""
        if not self.is_flying and self.tello:
            self.tello.takeoff()
            self.is_flying = True
            self.last_command_time = time.time()
            self.initial_position = Position()  # 記錄起飛位置為初始位置
            print("無人機起飛，初始位置設置為", self.initial_position)

    def land(self):
        """控制無人機降落"""
        if self.is_flying and self.tello:
            self.tello.land()
            self.is_flying = False
            self.last_command_time = time.time()

    def emergency_land(self):
        """執行緊急降落程序"""
        print("執行緊急降落")
        self.emergency_stop.set()
        if self.tello:
            try:
                self.tello.emergency()
            except Exception as e:
                print(f"緊急降落時發生錯誤: {str(e)}")
        self.is_flying = False
        print("緊急降落完成")

    def move_to_flame(self, flame, frame_width, frame_height):
        """
        移動無人機到火焰位置，使用固定的速度選項
        :param flame: 火焰信息 [x1, y1, x2, y2]
        :param frame_width: 幀寬度
        :param frame_height: 幀高度
        :return: 是否繼續自動模式
        """
        flame_center_x = (flame[0] + flame[2]) // 2
        flame_center_y = (flame[1] + flame[3]) // 2
        flame_size = (flame[2] - flame[0]) * (flame[3] - flame[1])

        target_x = frame_width // 2
        target_y = frame_height // 2
        target_size = frame_width * frame_height * 0.18

        # 確定移動方向和速度
        lr_index = self._get_movement_index(flame_center_x, target_x, frame_width // 8, frame_width // 4)
        ud_index = self._get_movement_index(flame_center_y, target_y, frame_height // 8, frame_height // 4)
        fb_index = self._get_movement_index(flame_size, target_size, target_size // 4, target_size // 2)

        # 調整上下移動的邏輯
        # ud_index = 4 - ud_index  # 反轉上下移動的索引

        # 檢查是否所有速度都為0
        if lr_index == 2 and fb_index == 2 and ud_index == 2:
            print("無需移動或已到達目標，退出自動模式")
            self.auto_mode = False
            return False

        self.adjust_position(lr_index, fb_index, ud_index, 0)

        self.print_movement_info(flame_center_x, flame_center_y, flame_size, target_x, target_y, target_size, lr_index,
                                 fb_index, ud_index)

        return True

    def return_to_start(self):
        """
        控制無人機返回起始位置
        """
        print("開始返回起始位置")
        while self.position != self.initial_position:
            dx = self.initial_position.x - self.position.x
            dy = self.initial_position.y - self.position.y
            dz = self.initial_position.z - self.position.z

            lr_index = self._get_return_index(dx)
            fb_index = self._get_return_index(dy)
            ud_index = self._get_return_index(dz)

            self.adjust_position(lr_index, fb_index, ud_index, 0)
            time.sleep(0.5)  # 短暫暫停以允許位置更新

        print("已返回起始位置")

    def _get_return_index(self, diff):
        """
        根據與目標位置的差異確定返回索引
        """
        if abs(diff) < 5:
            return 2  # 不移動
        elif abs(diff) < 20:
            return 1 if diff > 0 else 3  # 小幅度移動
        else:
            return 0 if diff > 0 else 4  # 大幅度移動

    def adjust_position(self, left_right, forward_backward, up_down, yaw):
        """
        調整無人機位置，使用固定的速度選項
        :param left_right: 左右移動的速度索引 (0-4 對應 -20, -10, 0, 10, 20)
        :param forward_backward: 前後移動的速度索引
        :param up_down: 上下移動的速度索引
        :param yaw: 旋轉速度
        """
        if left_right != 2 or forward_backward != 2 or up_down != 2 or yaw != 0:
            with self.command_lock:
                current_time = time.time()
                if current_time - self.last_command_time < self.command_interval:
                    time.sleep(self.command_interval - (current_time - self.last_command_time))

                if self.tello and not self.emergency_stop.is_set():
                    lr_speed = self.SPEED_OPTIONS[left_right]
                    fb_speed = self.SPEED_OPTIONS[forward_backward]
                    ud_speed = self.SPEED_OPTIONS[up_down]

                    try:
                        self.tello.send_rc_control(lr_speed, fb_speed, ud_speed, yaw)
                        self.last_command_time = time.time()
                        print(f"發送指令: 左右={lr_speed}, 前後={fb_speed}, 上下={ud_speed}")

                        # 更新位置
                        self.update_position(lr_speed, fb_speed, ud_speed)

                    except Exception as e:
                        print(f"調整位置時發生錯誤: {str(e)}")
                        self.emergency_stop.set()

    def update_position(self, lr_speed, fb_speed, ud_speed):
        """
        根據速度更新無人機的位置
        """
        dx = lr_speed
        dy = fb_speed
        dz = ud_speed
        self.position.update(dx, dy, dz)
        print(f"更新後的位置: {self.position}")

    def print_movement_info(self, flame_center_x, flame_center_y, flame_size, target_x, target_y, target_size, lr_index,
                            fb_index, ud_index):
        """
        打印詳細的移動信息，用於調試
        """
        print(f"火焰中心: ({flame_center_x}, {flame_center_y}), 大小: {flame_size}")
        print(f"目標位置: ({target_x}, {target_y}), 目標大小: {target_size}")
        print(f"移動指數: 左右={lr_index}, 前後={fb_index}, 上下={ud_index}")
        print(f"實際速度: 左右={self.SPEED_OPTIONS[lr_index]}, 前後={self.SPEED_OPTIONS[fb_index]}, 上下={self.SPEED_OPTIONS[ud_index]}")
        print(f"當前位置: {self.position}")

    def get_position(self):
        """
        獲取當前無人機位置
        """
        return str(self.position)

    def _get_movement_index(self, current, target, small_threshold, large_threshold):
        """
        根據當前位置和目標位置確定移動索引
        :return: 0-4 之間的索引，對應 SPEED_OPTIONS
        """
        diff = current - target
        if abs(diff) <= small_threshold:
            return 2  # 不移動
        elif abs(diff) <= large_threshold:
            return 1 if diff > 0 else 3  # 小幅度移動
        else:
            return 0 if diff > 0 else 4  # 大幅度移動

    def get_frame(self):
        """獲取當前視頻幀"""
        if self.tello.stream_on:
            return self.tello.get_frame_read().frame
        return None

    def get_battery(self):
        """獲取電池電量"""
        current_time = time.time()
        if current_time - self.last_battery_check >= self.battery_check_interval:
            self.battery = self.tello.get_battery()
            self.last_battery_check = current_time
        return self.battery

    def toggle_vision(self):
        """切換視覺處理開關"""
        self.is_vision_enabled = not self.is_vision_enabled
        print(f"影像辨識 {'啟用' if self.is_vision_enabled else '停用'}")

    def toggle_mode(self):
        """切換自動/手動模式"""
        self.auto_mode = not self.auto_mode
        print(f"模式已切換。新模式: {'自動' if self.auto_mode else '手動'}")

    # Keepalive 相關方法
    def start_keepalive_thread(self):
        """啟動保持命令線程"""
        self.stop_keepalive.clear()
        self.keepalive_thread = threading.Thread(target=self._keepalive_loop)
        self.keepalive_thread.start()

    def stop_keepalive_thread(self):
        """停止保持命令線程"""
        if self.keepalive_thread:
            self.stop_keepalive.set()
            self.keepalive_thread.join()

    def _keepalive_loop(self):
        """保持命令循環"""
        while not self.stop_keepalive.is_set():
            current_time = time.time()
            if self.is_flying and current_time - self.last_command_time > self.keepalive_interval:
                self.send_keepalive_command()
            time.sleep(0.5)  # 每0.5秒檢查一次

    def send_keepalive_command(self):
        """發送保持命令"""
        with self.command_lock:
            if self.tello and not self.emergency_stop.is_set() and self.is_flying:
                try:
                    self.tello.send_rc_control(0, 0, 0, 0)
                    self.last_command_time = time.time()
                    print("發送保持命令")
                except Exception as e:
                    print(f"發送保持命令時發生錯誤: {str(e)}")

    def get_height(self):
        """獲取無人機當前高度"""
        if self.tello:
            try:
                return self.tello.get_height()  # 返回值單位為公分
            except Exception as e:
                print(f"獲取高度時發生錯誤: {str(e)}")
        return 0  # 如果無法獲取高度，返回0


class Position:
    """表示無人機位置的類"""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0

    def update(self, dx, dy, dz):
        """更新位置"""
        self.x += dx
        self.y += dy
        self.z += dz

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"