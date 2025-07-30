import cv2
import json
from pathlib import Path
import numpy as np
import torch
from ultralytics import YOLO
import cvzone
from datetime import datetime
import os
import time
import subprocess
import threading
import queue
import sys


class PersonTracker:
    def __init__(self, warning_time=10.0):
        self.warning_time = warning_time
        self.people_zone_time = {}
        self.warned_people = set()
        self.current_detections = {}
    
    def update_tracking(self, results, zone_manager, current_time):
        current_people_in_zone = set()
        
        if not zone_manager.zone_setup_complete:
            return current_people_in_zone
        
        # Xóa detections cũ
        self.current_detections.clear()
        
        if results and results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.int().cpu().tolist()
            class_ids = results[0].boxes.cls.int().cpu().tolist()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            confidences = results[0].boxes.conf.cpu().tolist()
            
            for box, class_id, track_id, conf in zip(boxes, class_ids, track_ids, confidences):
                if results[0].names[class_id] == 'person' and conf >= 0.3:
                    x1, y1, x2, y2 = box
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    
                    in_zone = zone_manager.is_point_in_zone((cx, cy))

                    self.current_detections[track_id] = {
                        'box': (x1, y1, x2, y2),
                        'center': (cx, cy),
                        'confidence': conf,
                        'in_zone': in_zone,
                        'last_update': current_time
                    }
                    
                    if in_zone:
                        current_people_in_zone.add(track_id)
                        self._update_zone_time(track_id, current_time)

        self._cleanup_zone_tracking(current_people_in_zone)
        
        return current_people_in_zone
    
    def _update_zone_time(self, track_id, current_time):
        if track_id not in self.people_zone_time:
            self.people_zone_time[track_id] = current_time
        
        time_in_zone = current_time - self.people_zone_time[track_id]
        
        if time_in_zone >= self.warning_time and track_id not in self.warned_people:
            warning_msg = f"⚠️ WARNING: Person {track_id} in danger zone for {time_in_zone:.1f}s!"
            print(warning_msg)
            self.warned_people.add(track_id)
    
    def _cleanup_zone_tracking(self, current_people_in_zone):
        people_to_remove = []
        for track_id in list(self.people_zone_time.keys()):
            if track_id not in current_people_in_zone:
                people_to_remove.append(track_id)
        
        for track_id in people_to_remove:
            del self.people_zone_time[track_id]
            if track_id in self.warned_people:
                self.warned_people.remove(track_id)
    
    def get_time_in_zone(self, track_id, current_time):
        if track_id in self.people_zone_time:
            return current_time - self.people_zone_time[track_id]
        return 0
    
    def reset_tracking(self):
        self.people_zone_time.clear()
        self.warned_people.clear()
        self.current_detections.clear()
        print("🔄 Đã reset tracking")