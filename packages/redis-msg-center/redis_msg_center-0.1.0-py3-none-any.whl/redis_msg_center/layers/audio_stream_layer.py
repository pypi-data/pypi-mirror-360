from loguru import logger
import sounddevice as sd
import numpy as np
import base64
import threading
import time
import queue
from typing import Optional, Callable


class AudioStreamLayer:
    def __init__(self, comm_center):
        self.comm_center = comm_center
        self.channels = 1
        self.rate = 16000
        self.chunk_size = 1024
        self.dtype = np.int16
        self.blocksize = self.chunk_size
        
        # Audio streams
        self.input_stream = None
        self.output_stream = None
        
        # Audio queues for buffering
        self.input_queue = queue.Queue()
        self.output_queues = {}  # Dict of robot_id -> queue
        
        # Stream control
        self.streaming = False
            
    def clean_redis_stream_buffer(self, robot_id: str):
        """Clean Redis stream buffer for a specific robot before audio play starts"""
        stream_name = f"robot:{robot_id}:audio"
        try:
            # Trim the Redis stream to remove old entries
            self.comm_center.redis_binary.xtrim(stream_name, maxlen=0)
            print(f"Cleaned Redis stream buffer for {stream_name}")
        except Exception as e:
            print(f"Failed to clean Redis stream buffer for {stream_name}: {e}")
            
    def start_audio_stream(self):
        """Start audio streaming from microphone"""
        if self.streaming:
            # print("Audio stream already running")
            return
            
        self.streaming = True
        
        def audio_callback(indata, frames, time_info, status):
            """Callback for audio input"""
            if status:
                print(f"Audio input status: {status}")
            # import ipdb; ipdb.set_trace()
            # # Convert to int16 and add to queue
            audio_data = (indata * 32767).astype(np.int16)  # Convert float32 to int16
            # print(audio_data)
            self.input_queue.put(audio_data.copy())
        
        try:
            from rlm.utils.sound import find_default_device
            default_device = find_default_device("UGREEN")
            # Start input stream
            self.input_stream = sd.InputStream(
                callback=audio_callback,
                channels=self.channels,
                samplerate=self.rate,
                device=default_device,
                blocksize=self.blocksize,
                dtype=np.float32  # sounddevice uses float32 internally
            )
            
            self.input_stream.start()
            
            # Start worker thread to process audio data
            threading.Thread(target=self._audio_sender_worker, daemon=True).start()
            
            # print(f"Audio streaming started: {self.rate}Hz, {self.channels} channel(s)")
            # import ipdb; ipdb.set_trace()
            
        except Exception as e:
            # print(f"Failed to start audio stream: {e}")
            self.streaming = False
            
    def _audio_sender_worker(self):
        """Worker thread to send audio data to Redis"""
        chunk_count = 0
        
        self.clean_redis_stream_buffer(self.comm_center.robot_id)
        self.input_queue.queue.clear()  # Clear any existing data in the queue
        
        while 1:
            if not (self.streaming and self.comm_center.running):
                time.sleep(0.1)
                continue
            try:
                # why can not enter here?
                # import ipdb; ipdb.set_trace()
                # Get audio data from queue (blocking with timeout)
                audio_data = self.input_queue.get(timeout=0.1)
                
                # Encode audio data
                audio_bytes = audio_data.tobytes()
                encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                
                # Send via Redis Streams
                stream_name = f"robot:{self.comm_center.robot_id}:audio"
                audio_chunk = {
                    'chunk_id': chunk_count,
                    'timestamp': time.time(),
                    'data': encoded_audio,
                    'sample_rate': self.rate,
                    'channels': self.channels,
                    'dtype': str(self.dtype),
                    'frames': len(audio_data)
                }
                
                self.comm_center.redis_binary.xadd(stream_name, audio_chunk, maxlen=200)
                # Trim the Redis stream to a fixed size to prevent memory overflow
                # self.comm_center.redis_binary.xtrim(stream_name, maxlen=200)
                chunk_count += 1
                # print(f"Sent audio chunk {chunk_count} to Redis stream {stream_name}")
                
                
            except queue.Empty:
                # print("No audio data available, waiting...")
                continue
            except Exception as e:
                # print(f"Audio sender error: {e}")
                time.sleep(0.01)
                
    def stop_audio_stream(self):
        """Stop audio streaming"""
        self.streaming = False
        
        if self.input_stream:
            self.input_stream.stop()
            self.input_stream.close()
            self.input_stream = None
            
        if self.output_stream:
            self.output_stream.stop()
            self.output_stream.close()
            self.output_stream = None
            
        # Clear queues
        while not self.input_queue.empty():
            try:
                self.input_queue.get_nowait()
            except queue.Empty:
                break
                
        for robot_queue in self.output_queues.values():
            while not robot_queue.empty():
                try:
                    robot_queue.get_nowait()
                except queue.Empty:
                    break
                    
        # print("Audio streaming stopped")
        
    def receive_audio_stream(self, robot_id: str, play_audio: bool = True, 
                           callback: Optional[Callable] = None):
        """Receive and optionally play audio stream"""
        
        if robot_id in self.output_queues:
            print(f"Already receiving audio from {robot_id}")
            return
            
        # Create queue for this robot
        self.output_queues[robot_id] = queue.Queue(maxsize=50)  # Buffer up to 50 chunks
        
        if play_audio:
            self._start_audio_output()
            
        def receiver_worker():
            stream_name = f"robot:{robot_id}:audio"
            last_id = '0'
            
            while self.comm_center.running:
                # try:
                    messages = self.comm_center.redis_binary.xread(
                        {stream_name: last_id}, count=1, block=100
                    )
                    
                    # logger.debug(f"Received audio messages from {stream_name}: {messages}")
                    
                    for stream, msgs in messages:
                        for msg_id, fields in msgs:
                            last_id = msg_id
                            
                            # Decode audio data
                            audio_bytes = base64.b64decode(fields[b'data'])
                            # print(f"{msg_id=}")
                            # print(f"{fields=}")
                            # Convert back to numpy array
                            # dtype = np.dtype(fields[b'dtype'].decode())
                            dtype = np.int16  # Assuming int16 for audio data
                            frames = int(fields[b'frames'])
                            audio_data = np.frombuffer(audio_bytes, dtype=dtype)
                            
                            # Reshape if needed
                            if self.channels > 1:
                                audio_data = audio_data.reshape(-1, self.channels)
                                
                            print(frames)
                            # Add to output queue if playing
                            if play_audio and robot_id in self.output_queues:
                                try:
                                    self.output_queues[robot_id].put_nowait({
                                        'data': audio_data,
                                        'timestamp': float(fields[b'timestamp']),
                                        'robot_id': robot_id
                                    })
                                except queue.Full:
                                    # Queue is full, remove oldest item
                                    try:
                                        self.output_queues[robot_id].get_nowait()
                                        self.output_queues[robot_id].put_nowait({
                                            'data': audio_data,
                                            'timestamp': float(fields[b'timestamp']),
                                            'robot_id': robot_id
                                        })
                                    except queue.Empty:
                                        pass
                                        
                            # Call custom callback if provided
                            if callback:
                                callback(audio_data, {
                                    'robot_id': robot_id,
                                    'timestamp': float(fields[b'timestamp']),
                                    'sample_rate': int(fields[b'sample_rate']),
                                    'channels': int(fields[b'channels'])
                                })
                                
                # except Exception as e:
                #     print(f"Audio receive error: {e}")
                #     time.sleep(0.01)
                    
            # Cleanup
            if robot_id in self.output_queues:
                del self.output_queues[robot_id]
                
        threading.Thread(target=receiver_worker, daemon=True).start()
        
    def _start_audio_output(self):
        """Start audio output stream if not already running"""
        if self.output_stream is not None:
            return
            
        def output_callback(outdata, frames, time_info, status):
            """Callback for audio output"""
            if status:
                print(f"Audio output status: {status}")
                
            # Initialize output with silence
            outdata.fill(0)
            
            # Mix audio from all active robot streams
            mixed_audio = np.zeros(frames, dtype=np.float32)
            active_streams = 0
            
            for robot_id, robot_queue in self.output_queues.items():
                try:
                    # Get audio chunk from queue
                    audio_chunk = robot_queue.get_nowait()
                    audio_data = audio_chunk['data']
                    
                    # Convert to float32 and normalize
                    if audio_data.dtype == np.int16:
                        audio_float = audio_data.astype(np.float32) / 32767.0
                    else:
                        audio_float = audio_data.astype(np.float32)
                        
                    # Ensure correct length
                    if len(audio_float) == frames:
                        mixed_audio += audio_float
                        active_streams += 1
                    elif len(audio_float) < frames:
                        mixed_audio[:len(audio_float)] += audio_float
                        active_streams += 1
                        
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Audio mixing error for {robot_id}: {e}")
                    
            # Normalize mixed audio to prevent clipping
            if active_streams > 0:
                mixed_audio = mixed_audio / max(1, active_streams * 0.7)  # Reduce volume to prevent clipping
                
            # Copy to output buffer
            if self.channels == 1:
                outdata[:, 0] = mixed_audio[:len(outdata)]
            else:
                for ch in range(self.channels):
                    outdata[:, ch] = mixed_audio[:len(outdata)]
                    
        try:
            self.output_stream = sd.OutputStream(
                callback=output_callback,
                channels=self.channels,
                samplerate=self.rate,
                blocksize=self.blocksize,
                dtype=np.float32
            )
            
            self.output_stream.start()
            print("Audio output stream started")
            
        except Exception as e:
            print(f"Failed to start audio output: {e}")
            self.output_stream = None
            
    def stop_receiving_audio(self, robot_id: str):
        """Stop receiving audio from specific robot"""
        if robot_id in self.output_queues:
            del self.output_queues[robot_id]
            print(f"Stopped receiving audio from {robot_id}")
            
        # Stop output stream if no more robots
        if not self.output_queues and self.output_stream:
            self.output_stream.stop()
            self.output_stream.close()
            self.output_stream = None
            print("Audio output stream stopped")
            
    def list_audio_devices(self):
        """List available audio devices"""
        print("Available audio devices:")
        print(sd.query_devices())
        
    def set_audio_device(self, input_device=None, output_device=None):
        """Set specific audio devices"""
        if input_device is not None:
            sd.default.device[0] = input_device
            
        if output_device is not None:
            sd.default.device[1] = output_device
            
        print(f"Audio devices set - Input: {sd.default.device[0]}, Output: {sd.default.device[1]}")
        
    def get_audio_info(self):
        """Get current audio configuration info"""
        return {
            'sample_rate': self.rate,
            'channels': self.channels,
            'chunk_size': self.chunk_size,
            'dtype': str(self.dtype),
            'streaming': self.streaming,
            'input_queue_size': self.input_queue.qsize(),
            'output_queues': {robot_id: q.qsize() for robot_id, q in self.output_queues.items()},
            'default_devices': sd.default.device
        }