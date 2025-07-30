
from redis_msg_center.core import (
    RobotCommCenter,
    MessageType,
)



######### WS machine #########
robot_comm = RobotCommCenter(robot_id="robot_ws")
# robot_comm = RobotCommCenter(robot_id="robot_ws", redis_host="10.11.12.56")
robot_comm.audio_layer.start_audio_stream()
robot_comm.start()

# # Start video and audio streaming
# robot_comm.video_layer.start_video_stream(camera_id=0)

# robot_comm.audio_layer.input_queue
# robot_comm.audio_layer.streaming
# robot_comm.audio_layer.comm_center.running



######### local machine #########
# Initialize robot communication center
robot_comm = RobotCommCenter(robot_id="robot_local")

# Register message handlers
def handle_command(message_data):
    print(f"Received command: {message_data}")
    command = message_data['data']['command']
    print(f"Received command: {command}")

robot_comm.register_message_handler(MessageType.COMMAND, handle_command)

# Start the communication center
robot_comm.start()




########### test code ############

# Send commands to other robots
robot_comm.message_layer.send_command("robot_ws", "move_forward", {"distance": 1346236})
robot_comm.message_layer.send_command("robot_local", "move_forward", {"distance": 324523})



# # Receive video from another robot
# def on_video_frame(frame, metadata):
#     cv2.imshow(f"Robot {metadata['robot_id']}", frame)
#     cv2.waitKey(1)

# robot_comm.video_layer.receive_video_stream("robot_ws", on_video_frame)



# Receive audio from another robot
def on_audio_chunk(audio_data, metadata):
    # print(f"Received audio chunk from {metadata['robot_id']}")
    # Here you can process the audio data, e.g., play it or analyze it
    # For demonstration, we just print the metadata
    print(f"Audio metadata: {metadata}")

robot_comm.audio_layer.receive_audio_stream("robot_ws", on_audio_chunk)


# # Broadcast status
# robot_comm.message_layer.broadcast_status({
#     "battery": 85,
#     "position": {"x": 10, "y": 20},
#     "mode": "autonomous"
# })


# import cv2
# import numpy as np

# # Initialize robot communication center
# robot_comm = RobotCommCenter(robot_id="robot_001")

# # Register stream handlers
# def handle_video_stream(frame, metadata):
#     """Handle incoming video frames"""
#     print(f"Received video frame {metadata['frame_id']} from {metadata['robot_id']}")
    
#     # Display the frame
#     cv2.imshow(f"Robot {metadata['robot_id']} Video", frame)
#     cv2.waitKey(1)
    
#     # You can also process the frame here
#     # - Object detection
#     # - Face recognition
#     # - Motion tracking
#     # etc.

# def handle_audio_stream(audio_data, metadata):
#     """Handle incoming audio chunks"""
#     print(f"Received audio chunk {metadata['chunk_id']} from {metadata['robot_id']}")
    
#     # You can process audio here
#     # - Speech recognition
#     # - Audio analysis
#     # - Play audio
#     # etc.

# def handle_sensor_stream(sensor_data, metadata):
#     """Handle incoming sensor data"""
#     print(f"Received {metadata['sensor_type']} data from {metadata['robot_id']}: {sensor_data}")
    
#     # Process sensor data
#     # - Environmental monitoring
#     # - Robot state tracking
#     # - Safety checks
#     # etc.

# # Register handlers for specific robots
# robot_comm.register_stream_handler('video', 'robot_002', handle_video_stream)
# robot_comm.register_stream_handler('audio', 'robot_002', handle_audio_stream)
# robot_comm.register_stream_handler('sensor', 'robot_002', handle_sensor_stream, 'temperature')
# robot_comm.register_stream_handler('sensor', 'robot_003', handle_sensor_stream, 'lidar')

# # Start the communication center
# robot_comm.start()
while True:
    # Your robot logic here
    # print("Robot is running...")
    time.sleep(1)

# # Your robot's main loop
# try:
        
# except KeyboardInterrupt:
#     print("Shutting down...")
#     robot_comm.stop()