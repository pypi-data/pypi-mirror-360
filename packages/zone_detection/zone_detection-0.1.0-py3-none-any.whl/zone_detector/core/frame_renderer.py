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

class FrameRenderer: 
    def __init__(self, width=1020, height=500):
        self.width = width
        self.height = height
    
    def draw_zone_creation_interface(self, frame, zone_manager):
        for i, point in enumerate(zone_manager.mouse_area):
            cv2.circle(frame, point, 8, (0, 255, 0), -1)
            cv2.putText(frame, str(i+1), (point[0]+15, point[1]-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        if len(zone_manager.mouse_area) > 1:
            for i in range(len(zone_manager.mouse_area)):
                if i < len(zone_manager.mouse_area) - 1:
                    cv2.line(frame, zone_manager.mouse_area[i], 
                           zone_manager.mouse_area[i+1], (255, 0, 255), 2)
            if len(zone_manager.mouse_area) >= 3:
                cv2.line(frame, zone_manager.mouse_area[-1], 
                        zone_manager.mouse_area[0], (255, 0, 255), 2) 
        return frame
    
    def draw_annotations(self, frame, zone_manager, tracker, current_people_in_zone, 
                        current_time, frame_count, start_time):
        try:
            # trong chế độ tạo zone
            if zone_manager.zone_creation_mode:
                return self.draw_zone_creation_interface(frame, zone_manager)
            
            if zone_manager.area and len(zone_manager.area) >= 3:
                cv2.polylines(frame, [np.array(zone_manager.area)], True, (0, 0, 255), 2)
            
            for i, point in enumerate(zone_manager.mouse_area):
                cv2.circle(frame, point, 5, (0, 255, 0), -1)
                cv2.putText(frame, str(i+1), (point[0]+10, point[1]+5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            if zone_manager.zone_setup_complete:
                self._draw_detections(frame, tracker, current_time)
                self._draw_info_panel(frame, current_people_in_zone, tracker, 
                                    frame_count, start_time)
            else:
                cvzone.putTextRect(frame, 'Waiting for zone setup...', 
                                 (10, 60), 1, 2, colorR=(255, 255, 0))
            
            return frame
            
        except Exception as e:
            print(f"⚠️ Annotation error: {e}")
            return frame
    
    def _draw_detections(self, frame, tracker, current_time):
        for track_id, detection in tracker.current_detections.items():
            x1, y1, x2, y2 = detection['box']
            time_in_zone = tracker.get_time_in_zone(track_id, current_time)
            
            if detection['in_zone']:
                color = (0, 0, 255) if time_in_zone >= tracker.warning_time else (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                info_text = f'ID: {track_id}'
                cvzone.putTextRect(frame, info_text, (x1, y1 - 10), 1, 1)
    
    def _draw_info_panel(self, frame, current_people_in_zone, tracker, frame_count, start_time):
        cv2.putText(frame, f'People in Zone: {len(current_people_in_zone)}', 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        # Cảnh báo
        if tracker.warned_people:
            warning_text = f"DANGER: {len(tracker.warned_people)} person(s) exceeded {tracker.warning_time}s"
            (text_width, text_height), _ = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame, (10, 100), (20 + text_width, 130), (0, 0, 0), -1 )
            cv2.putText(frame, warning_text, (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.rectangle(frame, (5, 105), (15, 125), (0, 0, 255), -1)
            cv2.putText(frame, "!", (8, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
        
        
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time if elapsed_time > 0 else 0
        cvzone.putTextRect(frame, f'FPS: {fps:.1f}', (10, 70), 1, 1)