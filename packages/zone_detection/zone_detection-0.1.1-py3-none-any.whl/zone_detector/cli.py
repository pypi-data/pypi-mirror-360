
import argparse
from .detection_streamer import YOLODetectionStreamer
import time

def main():
    parser = argparse.ArgumentParser(description="YOLO ROI Detector")
    parser.add_argument("--video", default="22.mp4", help="Video file path")
    parser.add_argument("--model", default="yolo11n.pt", help="YOLO model path")
    parser.add_argument("--rtsp", default="rtsp://localhost:8554/live", help="RTSP URL")
    parser.add_argument("--warning-time", type=float, default=10.0, help="Warning time in seconds")
    parser.add_argument("--no-streaming", action="store_true", help="Disable RTSP streaming")
    parser.add_argument("--detection-interval", type=float, default=0.5, help="Detection interval")
    parser.add_argument("--zone-mode", type=int, choices=[1, 2], default=1, help="Zone mode")
    
    args = parser.parse_args()
    
    # Tạo streamer
    streamer = YOLODetectionStreamer(
        video_path=args.video,
        model_path=args.model,
        rtsp_url=args.rtsp,
        warning_time=args.warning_time,
        enable_streaming=not args.no_streaming,
        detection_interval=args.detection_interval,
        zone_mode=args.zone_mode
    )
    
    try:
        print(f"🎥 Input source: {args.video}")
        print(f"🎯 Zone Mode: {args.zone_mode}")
        
        if not args.no_streaming:
            print(f"📡 RTSP URL: {args.rtsp}")
        
        # Bắt đầu xử lý
        capture_thread, stream_thread = streamer.start_streaming()
        
        if capture_thread is None:
            print("❌ Failed to start detection")
            return
        
        # Đợi các thread hoàn thành
        while capture_thread.is_alive() or (stream_thread and stream_thread.is_alive()):
            time.sleep(0.5)
            if streamer.video_finished:
                print("🎬 Video playback completed!")
                break
        
        # Đợi thread kết thúc
        capture_thread.join(timeout=5)
        if stream_thread:
            stream_thread.join(timeout=5)
        
        print("✅ All threads completed!")
        
    except KeyboardInterrupt:
        print("\n⚡ Interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        streamer.stop_streaming()
        print("✅ Program ended successfully!")

if __name__ == "__main__":
    main()