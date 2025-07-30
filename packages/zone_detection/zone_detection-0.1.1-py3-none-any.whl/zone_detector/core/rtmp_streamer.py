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

class RTMPStreamer:
    
    def __init__(self, rtsp_url, width=1020, height=500, fps=30):
        self.rtsp_url = rtsp_url
        self.width = width
        self.height = height
        self.fps = fps
        self.ffmpeg_process = None
        self.frame_queue = queue.Queue(maxsize=5)
        self.running = False
    
    def start_ffmpeg_process(self):
        print(f"📡 Starting RTSP stream to: {self.rtsp_url}")
        
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', f'{self.width}x{self.height}',
            '-r', str(self.fps),
            '-i', '-',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'fast ',
            '-tune', 'zerolatency',
            '-crf', '23',
            '-g', str(int(self.fps * 2)),
            '-f', 'rtsp',
            '-rtsp_transport', 'tcp',
            self.rtsp_url
        ]
        
        try:
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd, stdin=subprocess.PIPE,
                stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )
            print("✅ FFmpeg streaming process started")
            return True
        except Exception as e:
            print(f"❌ Could not start FFmpeg process: {e}")
            return False
    
    def add_frame(self, frame):
        try:
            self.frame_queue.put(frame, timeout=0.01)
        except queue.Full:
            try:
                self.frame_queue.get_nowait()
                self.frame_queue.put(frame, timeout=0.01)
            except queue.Empty:
                pass
    
    def stream_loop(self, video_finished_callback):
        consecutive_errors = 0
        max_errors = 20
        
        while self.running:
            try:
                frame = self.frame_queue.get(timeout=1.0)
                
                if self.ffmpeg_process and self.ffmpeg_process.stdin:
                    self.ffmpeg_process.stdin.write(frame.tobytes())
                    self.ffmpeg_process.stdin.flush()
                
                consecutive_errors = 0
                
            except queue.Empty:
                if video_finished_callback():
                    print("📹 Video ended, stopping stream...")
                    break
                continue
            except BrokenPipeError:
                print("⚠️ FFmpeg pipe broken")
                break
            except Exception as e:
                consecutive_errors += 1
                print(f"⚠️ Streaming error ({consecutive_errors}/{max_errors}): {e}")
                
                if consecutive_errors >= max_errors:
                    print("❌ Too many streaming errors, stopping")
                    break
                
                time.sleep(0.1)
    
    def stop_streaming(self):
        self.running = False
        try:
            if self.ffmpeg_process:
                self.ffmpeg_process.stdin.close()
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=5)
                print("✅ FFmpeg process terminated")
        except subprocess.TimeoutExpired:
            if self.ffmpeg_process:
                self.ffmpeg_process.kill()
                print("🔨 FFmpeg process killed")
        except Exception as e:
            print(f"⚠️ Error closing FFmpeg: {e}")