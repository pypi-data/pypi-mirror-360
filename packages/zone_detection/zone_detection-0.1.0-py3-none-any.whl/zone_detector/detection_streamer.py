import cv2
from ultralytics import YOLO
from datetime import datetime
import os
import time
import subprocess
import threading
from .core.zone_manager import ZoneManager
from .core.yolo_model import YOLOModel
from .core.person_tracker import PersonTracker
from .core.frame_renderer import FrameRenderer
from .core.rtmp_streamer import RTMPStreamer

class YOLODetectionStreamer: 
    def __init__(self, 
                 video_path='',
                 model_path="yolo11s.pt",
                 rtsp_url="rtsp://localhost:8554/live",
                 warning_time=10.0,
                 enable_streaming=True,
                 detection_interval=0.5,
                 zone_mode=1):
        
        print("🚀 Bắt đầu detect....")
        
        self.video_path = video_path
        self.enable_streaming = enable_streaming
        self.detection_interval = detection_interval
        
        # Khởi tạo các component
        self.zone_manager = ZoneManager(zone_mode=zone_mode)
        self.yolo_model = YOLOModel(model_path)
        self.tracker = PersonTracker(warning_time)
        self.renderer = FrameRenderer()
        
        if enable_streaming:
            self.streamer = RTMPStreamer(rtsp_url)
        else:
            self.streamer = None
        
        # Video properties
        self.width = 1020
        self.height = 500
        self.fps = 30
        self.current_frame = None
        
        # Timing và state
        self.last_detection_time = 0
        self.running = False
        self.video_finished = False
        self.frame_count = 0
        self.start_time = time.time()
    
    def setup_mouse_callback(self):
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                self.zone_manager.add_point(x, y)
            elif event == cv2.EVENT_RBUTTONDOWN:
                self.zone_manager.complete_zone_creation()

        cv2.namedWindow('YOLO Detection')
        cv2.setMouseCallback('YOLO Detection', mouse_callback)
    
    def check_prerequisites(self):
        if isinstance(self.video_path, str) and self.video_path != '0':
            if not os.path.exists(self.video_path):
                return False
        
        
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            cap.release()
            return False
        
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return False
        print("Video source is working")
        
        # Kiểm tra FFmpeg
        if self.enable_streaming:
            try:
                result = subprocess.run(['ffmpeg', '-version'], 
                                    capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("✅ FFmpeg is available")
                    return True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                return False
        return True
    
    def process_detection(self, frame):
        current_time = time.time() - self.start_time
        current_people_in_zone = set()
        
        if not self.zone_manager.zone_setup_complete:
            return current_people_in_zone, False
        
        # Kiểm tra có cần detect không
        should_detect = current_time - self.last_detection_time >= self.detection_interval
        
        if should_detect:
            results = self.yolo_model.detect_and_track(frame)
            self.last_detection_time = current_time
            
            if results:
                current_people_in_zone = self.tracker.update_tracking(
                    results, self.zone_manager, current_time)
        else:
            # Giữ nguyên tracking hiện tại
            for track_id, detection in self.tracker.current_detections.items():
                if detection['in_zone']:
                    current_people_in_zone.add(track_id)
                    
                    if track_id in self.tracker.people_zone_time:
                        time_in_zone = current_time - self.tracker.people_zone_time[track_id]
                        if (time_in_zone >= self.tracker.warning_time and 
                            track_id not in self.tracker.warned_people):
                            warning_msg = f"⚠️ WARNING: Person {track_id} in danger zone for {time_in_zone:.1f}s!"
                            print(warning_msg)
                            self.tracker.warned_people.add(track_id)
        
        return current_people_in_zone, should_detect
    
    def capture_and_process(self):
        print("🎥 Starting video capture...")
        self.setup_mouse_callback()
        cap = cv2.VideoCapture(self.video_path)
        

        original_fps = cap.get(cv2.CAP_PROP_FPS)
        self.fps = original_fps if original_fps > 0 else 30
        print(f"✅ Video original FPS: {self.fps}")
        
        # Cài đặt video properties
        frame_delay = 1.0 / self.fps if self.fps > 0 else 1.0/30
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        consecutive_failures = 0
        max_failures = 10
        
        while self.running:
            loop_start_time = time.time()
            
            ret, frame = cap.read()
            if not ret:
                consecutive_failures += 1
                if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                    self.video_finished = True
                    self.running = False
                    break
                
                if consecutive_failures >= max_failures:
                    break
                    time.sleep(0.1)
                    continue
            
            self.current_frame = frame.copy()
            consecutive_failures = 0
            self.frame_count += 1

            frame_resized = cv2.resize(frame, (self.width, self.height))

            current_people_in_zone, was_detected = self.process_detection(frame_resized)

            annotated_frame = self.renderer.draw_annotations(
                frame_resized, self.zone_manager, self.tracker,
                current_people_in_zone, time.time() - self.start_time,
                self.frame_count, self.start_time
            )

            if self.streamer and self.zone_manager.zone_setup_complete:
                self.streamer.add_frame(annotated_frame)

            cv2.imshow("YOLO Detection", annotated_frame)

            if not self.handle_key_press():
                break

            self.control_frame_rate(loop_start_time, frame_delay)
        
        cap.release()
        cv2.destroyAllWindows()
        print("📷 Video capture stopped")
    
    def handle_key_press(self):
       
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord("q"):  # Thoát chương trình
            self.running = False
            return False
        elif key == ord("r"):  # Reset tracking
            self.tracker.reset_tracking()
        elif key == ord("d"):  # Force detection
            self.last_detection_time = 0
        elif key == ord("n"):  # Hoàn thành tạo zone
            self.zone_manager.complete_zone_creation()
        elif key == ord("c"):  # Xóa các điểm đã chọn
            self.zone_manager.clear_points()
        elif key == ord("s"):  # Bắt đầu detection
            if not self.zone_manager.zone_setup_complete and self.zone_manager.area:
                self.zone_manager.zone_setup_complete = True
                self.zone_manager.zone_creation_mode = False
                print("🎯 Bắt đầu detection!")
            else:
                print("ℹ️ Detection đã đang chạy")
        elif key == ord("z"):  # Toggle zone creation mode
            self.zone_manager.toggle_creation_mode()
        
        return True

    def control_frame_rate(self, loop_start_time, frame_delay):
        loop_end_time = time.time()
        processing_time = loop_end_time - loop_start_time
        sleep_time = frame_delay - processing_time
        
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    def start_streaming(self):
        if not self.check_prerequisites():
            return None, None
        
        self.running = True
        self.start_time = time.time()
        
        capture_thread = threading.Thread(target=self.capture_and_process, daemon=True)
        capture_thread.start()
        
        stream_thread = None
        if self.enable_streaming:
            time.sleep(1)  
            stream_thread = threading.Thread(target=self.streamer.stream_loop, args=(self.video_finished,))
            stream_thread.start()
            print("📡 RTSP streaming started")
        else:
            print("📺 Streaming disabled - only local detection")
        
        return capture_thread, stream_thread
    
    def stop_streaming(self):

        print("\n🛑 Stopping detection and streaming...")
        self.running = False
        self.zone_manager.save_zones()
        
        if self.streamer:
            self.streamer.stop_streaming()

        cv2.destroyAllWindows()
