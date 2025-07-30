import pyaudio
import redis
import json
import asyncio
import threading
import time
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import cv2
import numpy as np
import base64
from loguru import logger



class MessageType(Enum):
    COMMAND = "command"
    STATUS = "status"
    VIDEO_FRAME = "video_frame"
    AUDIO_CHUNK = "audio_chunk"
    SENSOR_DATA = "sensor_data"
    ERROR = "error"

@dataclass
class RobotMessage:
    robot_id: str
    message_type: MessageType
    timestamp: float
    data: Dict[str, Any]
    priority: int = 1
    
    def to_dict(self):
        """Convert to dictionary with JSON-serializable values"""
        result = asdict(self)
        # Convert enum to string value
        result['message_type'] = self.message_type.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create RobotMessage from dictionary"""
        # Convert string back to enum
        data['message_type'] = MessageType(data['message_type'])
        return cls(**data)
    
    def to_json(self):
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str):
        """Create RobotMessage from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    
class MessageLayer:
    def __init__(self, comm_center):
        self.comm_center = comm_center
        
    def send_command(self, target_robot: str, command: str, params: Dict = None):
        """Send command to specific robot"""
        message = RobotMessage(
            robot_id=self.comm_center.robot_id,
            message_type=MessageType.COMMAND,
            timestamp=time.time(),
            data={
                'command': command,
                'params': params or {},
                'target': target_robot
            },
            priority=3
        )
        tmp=message.to_json()
        channel = f"robot:{target_robot}:commands"
        logger.debug(f"Sending command to {target_robot}: {tmp}")
        self.comm_center.redis_client.publish(channel, tmp)
        
    def broadcast_status(self, status_data: Dict):
        """Broadcast robot status to all"""
        message = RobotMessage(
            robot_id=self.comm_center.robot_id,
            message_type=MessageType.STATUS,
            timestamp=time.time(),
            data=status_data,
            priority=1
        )
        
        tmp=message.to_json()
        channel = "robot:broadcast:status"
        logger.debug(f"Broadcasting status: {tmp}")
        self.comm_center.redis_client.publish(channel, tmp)
        
    def send_sensor_data(self, sensor_type: str, data: Dict):
        """Send sensor data"""
        key = f"robot:{self.comm_center.robot_id}:sensors:{sensor_type}"
        
        message = {
            'timestamp': time.time(),
            'robot_id': self.comm_center.robot_id,
            'data': data
        }
        
        # Store latest sensor data
        self.comm_center.redis_client.hset(key, 'latest', json.dumps(message))
        
        # Add to time series (Redis Streams)
        self.comm_center.redis_client.xadd(f"{key}:stream", message)
