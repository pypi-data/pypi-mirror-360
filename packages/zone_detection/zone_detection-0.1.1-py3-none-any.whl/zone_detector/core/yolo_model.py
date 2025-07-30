import torch
from ultralytics import YOLO
import numpy as np
import sys

class YOLOModel: 
    def __init__(self, model_path="yolo11n.pt"):
        self.model_path = model_path
        self.model = None
        self.names = {}
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        self.load_model()
        self.warmup_model()
    
    def load_model(self):
        try:
            print(f"Đang tải YOLO model: {self.model_path}")
            self.model = YOLO(self.model_path)
            self.names = self.model.names
            self.model.to(self.device)
        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            sys.exit(1)
    
    def warmup_model(self):
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        _ = self.model(dummy_frame, verbose=False)
        print("✅ Model ready")
    
    def detect_and_track(self, frame):

        try:
            results = self.model.track(frame, persist=True, verbose=False, imgsz=640)
            return results
        except Exception as e:
            print(f"⚠️ Detection error: {e}")
            return None