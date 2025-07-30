import cv2
import json
from pathlib import Path
import numpy as np

class ZoneManager:
    def __init__(self, zone_file="danger_zones.json", zone_mode=1):
        self.zone_file = zone_file
        self.zone_mode = zone_mode
        self.area = []
        self.mouse_area = []
        self.saved_zones = []
        self.zone_creation_mode = False
        self.zone_setup_complete = False
        
        self.initialize_zones()
    
    def initialize_zones(self):
        print(f"🎯 Zone Mode: {self.zone_mode}")
        
        if self.zone_mode == 1:
            print("Mode 1: Sử dụng zone từ file danger_zones.json")
            self.load_zones()
            if not self.area:
                print("Không load được zone từ file, sử dụng zone mặc định")
                self.area = [(760, 200), (140, 211), (110, 400), (834, 427)]
            self.zone_setup_complete = True
            print(f"Zone đã được thiết lập: {self.area}")
            
        elif self.zone_mode == 2:
            print("🖱️ Mode 2: Vẽ zone bằng chuột")
            self.zone_creation_mode = True
            self.zone_setup_complete = False

    def save_zones(self):
        if not self.area:
            print("Không có zone nào để lưu")
            return   
        zones_to_save = {
            "default_zone": self.area,
            "custom_zones": self.saved_zones,
        }
        
        try:
            with open(self.zone_file, 'w') as f:
                json.dump(zones_to_save, f, indent=4)
            print(f"Đã lưu zones vào {self.zone_file}")
        except Exception as e:
            print(f"Lỗi khi lưu zones: {e}")
    
    def load_zones(self):
        if not Path(self.zone_file).exists():
            print(f"File zone {self.zone_file} không tồn tại")
            return False
        
        try:
            with open(self.zone_file, 'r') as f:
                data = json.load(f)
                if "default_zone" in data and data["default_zone"]:
                    self.area = data["default_zone"]
                    print(f"✅ Đã tải zone từ file: {len(self.area)} điểm")
                self.saved_zones = data.get("custom_zones", [])
                return True
        except Exception as e:
            print(f"Lỗi khi tải zones: {e}")
            return False
    
    def add_zone(self, zone):
        self.saved_zones.append(zone)
        self.save_zones()
    
    def add_point(self, x, y):
        if self.zone_creation_mode:
            self.mouse_area.append((x, y))
            print(f"📍 Điểm {len(self.mouse_area)}: ({x}, {y})")
            return True
        return False
    
    def complete_zone_creation(self):
        if len(self.mouse_area) >= 3:
            self.area = self.mouse_area.copy()
            self.add_zone(self.mouse_area)
            print(f"Đã tạo zone với {len(self.mouse_area)} điểm: {self.mouse_area}")
            self.mouse_area = []
            self.zone_creation_mode = False
            self.zone_setup_complete = True
            print("Zone đã được thiết lập! Bây giờ có thể bắt đầu detection.")
            return True
        else:
            print("Cần ít nhất 3 điểm để tạo zone")
            return False
    
    def clear_points(self):
        if self.zone_creation_mode:
            self.mouse_area = []
            print("🗑️ Đã xóa các điểm đã chọn")
    
    def is_point_in_zone(self, point):
        if not self.area or len(self.area) < 3:
            return False
        return cv2.pointPolygonTest(np.array(self.area), point, False) >= 0
    
    def toggle_creation_mode(self):
        if self.zone_mode == 2:
            self.zone_creation_mode = not self.zone_creation_mode
            if self.zone_creation_mode:
                print("🖱️ Chế độ tạo zone được kích hoạt")
            else:
                print("🖱️ Chế độ tạo zone được tắt")