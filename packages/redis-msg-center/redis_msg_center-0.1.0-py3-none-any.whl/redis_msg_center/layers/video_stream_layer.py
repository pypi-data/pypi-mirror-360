import threading
import time
from typing import Dict, Any, Callable, Optional
import cv2
import numpy as np
import base64

class VideoStreamLayer:
    def __init__(self, comm_center):
        self.comm_center = comm_center
        self.video_quality = 80  # JPEG quality
        self.max_fps = 30
        self.frame_buffer_size = 100
        
    def start_video_stream(self, camera_id: int = 0):
        """Start video streaming from camera"""
        def stream_worker():
            cap = cv2.VideoCapture(camera_id)
            cap.set(cv2.CAP_PROP_FPS, self.max_fps)
            
            frame_count = 0
            last_time = time.time()
            
            while self.comm_center.running:
                ret, frame = cap.read()
                if not ret:
                    continue
                    
                # Control frame rate
                current_time = time.time()
                if current_time - last_time < 1.0 / self.max_fps:
                    continue
                last_time = current_time
                
                # Compress frame
                compressed_frame = self._compress_frame(frame)
                
                # Send via Redis Streams
                stream_name = f"robot:{self.comm_center.robot_id}:video"
                frame_data = {
                    'frame_id': frame_count,
                    'timestamp': current_time,
                    'data': compressed_frame,
                    'width': frame.shape[1],
                    'height': frame.shape[0]
                }
                
                self.comm_center.redis_binary.xadd(stream_name, frame_data, maxlen=self.frame_buffer_size)
                frame_count += 1
                
            cap.release()
            
        threading.Thread(target=stream_worker, daemon=True).start()
        
    def _compress_frame(self, frame):
        """Compress frame to reduce bandwidth"""
        # Resize if too large
        height, width = frame.shape[:2]
        if width > 640:
            scale = 640.0 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height))
            
        # JPEG compression
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.video_quality]
        _, buffer = cv2.imencode('.jpg', frame, encode_param)
        return base64.b64encode(buffer).decode('utf-8')
        
    def receive_video_stream(self, robot_id: str, callback: Callable):
        """Receive video stream from another robot"""
        def receiver_worker():
            stream_name = f"robot:{robot_id}:video"
            last_id = '0'
            
            while self.comm_center.running:
                try:
                    messages = self.comm_center.redis_binary.xread(
                        {stream_name: last_id}, count=1, block=100
                    )
                    
                    for stream, msgs in messages:
                        for msg_id, fields in msgs:
                            last_id = msg_id
                            
                            # Decode frame
                            frame_data = base64.b64decode(fields[b'data'])
                            frame = cv2.imdecode(
                                np.frombuffer(frame_data, np.uint8), 
                                cv2.IMREAD_COLOR
                            )
                            
                            # Call callback with frame
                            callback(frame, {
                                'frame_id': int(fields[b'frame_id']),
                                'timestamp': float(fields[b'timestamp']),
                                'robot_id': robot_id
                            })
                            
                except Exception as e:
                    print(f"Video receive error: {e}")
                    time.sleep(0.1)
                    
        threading.Thread(target=receiver_worker, daemon=True).start()

