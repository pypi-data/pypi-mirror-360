import sys
import redis
import json
import threading
import time
from typing import Dict, Any, Callable, Optional
import cv2
import numpy as np
import base64
from loguru import logger

# set logger level
logger.remove()
logger.add(sys.stderr, level="INFO")

from .layers.audio_stream_layer import AudioStreamLayer
from .layers.video_stream_layer import VideoStreamLayer
from .layers.msg_layer import MessageType, MessageLayer

class RobotCommCenter:
    def __init__(self, redis_host='localhost', redis_port=6379, robot_id=None):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.redis_binary = redis.Redis(host=redis_host, port=redis_port, decode_responses=False)
        self.robot_id = robot_id or f"robot_{int(time.time())}"
        self.pubsub = self.redis_client.pubsub()
        self.running = False
        self.message_handlers = {}
        self.stream_handlers = {}
        self.stream_processors = {}  # Add this to store stream processors
        # Initialize layers
        self.message_layer = MessageLayer(self)
        self.video_layer = VideoStreamLayer(self)
        self.audio_layer = AudioStreamLayer(self)
        
    def start(self):
        """Start the communication center"""
        self.running = True
        self._setup_subscriptions()
        # Start background threads
        threading.Thread(target=self._message_listener, daemon=True).start()
        threading.Thread(target=self._stream_processor, daemon=True).start()
        threading.Thread(target=self._heartbeat, daemon=True).start()
        logger.info(f"Robot communication center started for {self.robot_id}")
        
    def stop(self):
        """Stop the communication center"""
        self.running = False
        self.pubsub.close()

    def _stream_processor(self):
        """Process incoming streams (video, audio, sensor data)"""
        while self.running:
            try:
                # Get all active streams for this robot
                stream_pattern = f"robot:*:video"
                video_streams = self._get_active_streams(stream_pattern)
                
                stream_pattern = f"robot:*:audio" 
                audio_streams = self._get_active_streams(stream_pattern)
                
                stream_pattern = f"robot:*:sensors:*:stream"
                sensor_streams = self._get_active_streams(stream_pattern)
                
                # Process all streams
                all_streams = {}
                all_streams.update({s: '0' for s in video_streams})
                all_streams.update({s: '0' for s in audio_streams}) 
                all_streams.update({s: '0' for s in sensor_streams})
                
                if all_streams:
                    # Read from multiple streams with timeout
                    try:
                        messages = self.redis_binary.xread(
                            all_streams, 
                            count=1, 
                            block=100  # 100ms timeout
                        )
                        
                        for stream_name, msgs in messages:
                            self._handle_stream_message(stream_name.decode(), msgs)
                            
                    except redis.ResponseError as e:
                        if "NOGROUP" not in str(e):
                            print(f"Stream processing error: {e}")
                            
                else:
                    # No active streams, sleep briefly
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"Stream processor error: {e}")
                time.sleep(1)
                
    def _get_active_streams(self, pattern):
        """Get list of active streams matching pattern"""
        try:
            streams = []
            keys = self.redis_client.keys(pattern)
            
            for key in keys:
                # Check if stream has recent activity (last 30 seconds)
                try:
                    info = self.redis_client.xinfo_stream(key)
                    last_entry = info.get('last-generated-id', '0-0')
                    
                    if last_entry != '0-0':
                        # Extract timestamp from stream ID
                        timestamp_ms = int(last_entry.split('-')[0])
                        current_time_ms = int(time.time() * 1000)
                        
                        # Only include streams with recent activity
                        if current_time_ms - timestamp_ms < 30000:  # 30 seconds
                            streams.append(key)
                            
                except redis.ResponseError:
                    # Stream might be empty or doesn't exist
                    continue
                    
            return streams
            
        except Exception as e:
            print(f"Error getting active streams: {e}")
            return []
            
    def _handle_stream_message(self, stream_name, messages):
        """Handle individual stream messages"""
        try:
            # Parse stream name to determine type and robot
            parts = stream_name.split(':')
            if len(parts) < 3:
                return
                
            robot_id = parts[1]
            stream_type = parts[2]
            
            for msg_id, fields in messages:
                # Update last processed ID for this stream
                if stream_name not in self.stream_processors:
                    self.stream_processors[stream_name] = {'last_id': '0'}
                    
                self.stream_processors[stream_name]['last_id'] = msg_id.decode()
                
                # Route to appropriate handler
                if stream_type == 'video':
                    self._handle_video_stream(robot_id, msg_id, fields)
                elif stream_type == 'audio':
                    self._handle_audio_stream(robot_id, msg_id, fields)
                elif stream_type == 'sensors':
                    sensor_type = parts[3] if len(parts) > 3 else 'unknown'
                    self._handle_sensor_stream(robot_id, sensor_type, msg_id, fields)
                    
        except Exception as e:
            print(f"Error handling stream message: {e}")
            
    def _handle_video_stream(self, robot_id, msg_id, fields):
        """Handle incoming video stream data"""
        try:
            # Check if we have a registered handler for this robot's video
            handler_key = f"video:{robot_id}"
            if handler_key in self.stream_handlers:
                
                # Decode video frame
                frame_data = base64.b64decode(fields[b'data'])
                frame = cv2.imdecode(
                    np.frombuffer(frame_data, np.uint8), 
                    cv2.IMREAD_COLOR
                )
                
                metadata = {
                    'robot_id': robot_id,
                    'frame_id': int(fields[b'frame_id']),
                    'timestamp': float(fields[b'timestamp']),
                    'width': int(fields[b'width']),
                    'height': int(fields[b'height']),
                    'msg_id': msg_id.decode()
                }
                
                # Call registered handler
                self.stream_handlers[handler_key](frame, metadata)
                
        except Exception as e:
            print(f"Error handling video stream: {e}")
            
    def _handle_audio_stream(self, robot_id, msg_id, fields):
        """Handle incoming audio stream data"""
        try:
            handler_key = f"audio:{robot_id}"
            if handler_key in self.stream_handlers:
                
                # Decode audio data
                audio_data = base64.b64decode(fields[b'data'])
                
                metadata = {
                    'robot_id': robot_id,
                    'chunk_id': int(fields[b'chunk_id']),
                    'timestamp': float(fields[b'timestamp']),
                    'sample_rate': int(fields[b'sample_rate']),
                    'channels': int(fields[b'channels']),
                    'msg_id': msg_id.decode()
                }
                
                # Call registered handler
                self.stream_handlers[handler_key](audio_data, metadata)
                
        except Exception as e:
            print(f"Error handling audio stream: {e}")
            
    def _handle_sensor_stream(self, robot_id, sensor_type, msg_id, fields):
        """Handle incoming sensor stream data"""
        try:
            handler_key = f"sensor:{robot_id}:{sensor_type}"
            if handler_key in self.stream_handlers:
                
                # Parse sensor data
                sensor_data = json.loads(fields[b'data'].decode())
                
                metadata = {
                    'robot_id': robot_id,
                    'sensor_type': sensor_type,
                    'timestamp': float(fields[b'timestamp']),
                    'msg_id': msg_id.decode()
                }
                
                # Call registered handler
                self.stream_handlers[handler_key](sensor_data, metadata)
                
        except Exception as e:
            print(f"Error handling sensor stream: {e}")
            
    def register_stream_handler(self, stream_type: str, robot_id: str, handler: Callable, sensor_type: str = None):
        """Register handler for stream data"""
        if stream_type == 'video':
            key = f"video:{robot_id}"
        elif stream_type == 'audio':
            key = f"audio:{robot_id}"
        elif stream_type == 'sensor' and sensor_type:
            key = f"sensor:{robot_id}:{sensor_type}"
        else:
            raise ValueError("Invalid stream type or missing sensor_type")
            
        self.stream_handlers[key] = handler
        print(f"Registered stream handler for {key}")
        
    def unregister_stream_handler(self, stream_type: str, robot_id: str, sensor_type: str = None):
        """Unregister stream handler"""
        if stream_type == 'video':
            key = f"video:{robot_id}"
        elif stream_type == 'audio':
            key = f"audio:{robot_id}"
        elif stream_type == 'sensor' and sensor_type:
            key = f"sensor:{robot_id}:{sensor_type}"
        else:
            return
            
        if key in self.stream_handlers:
            del self.stream_handlers[key]
            print(f"Unregistered stream handler for {key}")
            
    def _setup_subscriptions(self):
        """Setup Redis subscriptions"""
        # Subscribe to robot-specific commands
        self.pubsub.subscribe(f"robot:{self.robot_id}:commands")
        
        # Subscribe to broadcast messages
        self.pubsub.subscribe("robot:broadcast:status")
        self.pubsub.subscribe("robot:broadcast:emergency")
        
    def _message_listener(self):
        """Listen for incoming messages"""
        for message in self.pubsub.listen():
            if not self.running:
                break
            # import ipdb; ipdb.set_trace()
            logger.debug(f"Received message: {message}")
                
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    logger.debug(f"Handling message: {data}")
                    self._handle_message(data)
                except Exception as e:
                    print(f"Message handling error: {e}")
                    
    def _handle_message(self, message_data):
        """Handle incoming message"""
        msg_type = message_data.get('message_type')
        logger.debug(f"Handling message type: {msg_type}")
        if msg_type in self.message_handlers:
            self.message_handlers[msg_type](message_data)
            
    def register_message_handler(self, message_type: MessageType, handler: Callable):
        """Register handler for specific message type"""
        self.message_handlers[message_type.value] = handler
        
    def _heartbeat(self):
        """Send periodic heartbeat"""
        while self.running:
            # import ipdb; ipdb.set_trace()
            heartbeat_data = {
                'robot_id': self.robot_id,
                'timestamp': time.time(),
                'status': 'active'
            }
            
            self.redis_client.hset(
                f"robot:{self.robot_id}:heartbeat", 
                'data', 
                json.dumps(heartbeat_data)
            )
            self.redis_client.expire(f"robot:{self.robot_id}:heartbeat", 30)
            
            time.sleep(10)
            
    def get_active_robots(self):
        """Get list of active robots"""
        pattern = "robot:*:heartbeat"
        keys = self.redis_client.keys(pattern)
        
        active_robots = []
        for key in keys:
            data = self.redis_client.hget(key, 'data')
            if data:
                robot_info = json.loads(data)
                active_robots.append(robot_info)
                
        return active_robots
