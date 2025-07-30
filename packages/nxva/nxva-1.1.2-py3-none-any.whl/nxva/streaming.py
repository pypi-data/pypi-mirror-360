import os
import cv2
cv2.setNumThreads(0)
import time
import yaml
import platform
import threading
import numpy as np       
        
def is_jetson():
    """Check if the code is running on an NVIDIA Jetson platform."""
    compat_file_path = "/proc/device-tree/compatible"
    if os.path.isfile(compat_file_path):
        with open(compat_file_path, "r") as file:
            compat_str = file.read()
            return "nvidia" in compat_str and "tegra" in compat_str
    return False


class MultiStreaming(object):
    """
    A class to handle multi-camera streaming with automatic reconnection, frame resizing and gstreamer support.
    """
    def __init__(self, 
                 config=None, 
                 reconnect_interval=30,
                 verbose=False):
        """
        Initialize the MultiStreaming object with the given configuration settings.
        
        Args:
            config (str or dict): Configuration settings for the cameras, 
                which can be provided as a path to a YAML file or directly as a dictionary. 
                The configuration should include the following sections:
                
                'parameter': Dictionary containing:
                    - 'WIDTH' (int): Width of the frame.
                    - 'HEIGHT' (int): Height of the frame.
                    - 'GSTREAMER' (bool): Whether to use GStreamer for streaming.
                    - 'CODEC' (str, optional): Codec to use, default is 'h264'.
                
                'cameras': List of dictionaries, each containing:
                    - 'ip' (str): IP address of the camera.
                    - 'user' (str, optional): Username for the camera.
                    - 'pw' (str, optional): Password for the camera.
                
                Example configuration:
                ```
                parameter:
                    WIDTH: 1920
                    HEIGHT: 1080
                    GSTREAMER: True
                    CODEC: h264
                cameras:
                    - ip: '192.168.1.100'
                      user: 'admin'
                      pw: 'password'
                ```

            reconnect_interval (int): Interval in seconds to attempt reconnection to a camera.
            verbose (bool): Enable verbose output to help with debugging.
        """
        self.reconnect_interval = reconnect_interval
        self.verbose = verbose
        
        if config:
            self._load_and_validate_config(config)
            self._generate_rtsp_strings()
        else:
            raise ValueError('Configuration must be provided, either as a dictionary or a YAML file path.')
        
        self.running = True
        self.mutex = threading.Lock()
        self.caps = [cv2.VideoCapture() for _ in range(self.num)]
        self.caps_info = [None for _ in range(self.num)]
        self.frames = [np.zeros((self.h, self.w, 3), dtype=np.uint8) for i in range(self.num)]
        self.status = [False] * self.num
        self.rtsp_reconnect = [None] * self.num

    def _load_and_validate_config(self, config):
        if isinstance(config, str):
            assert config.endswith(('.yaml', '.yml'))
            with open(config, 'r') as f:
                self.setting = yaml.safe_load(f)
        elif isinstance(config, dict):
            self.setting = config
        else:
            raise TypeError('Config must be provided as a yaml file or dictionary.')
        
        self.num = len(self.setting['cameras'])
        for i in range(self.num):
            rtsp = self.setting['cameras'][i].get('rtsp', None)
            if not rtsp:
                self.setting['cameras'][i]['rtsp'] = [
                    {'ip': self.setting['cameras'][i]['ip'],
                     'user': self.setting['cameras'][i].get('user', None),
                     'pw': self.setting['cameras'][i].get('pw', None)}
                ]
        
        # Ensure 'parameter' section exists and set default values if necessary
        param_defaults = {'WIDTH': 1920, 'HEIGHT': 1080, 'GSTREAMER': False, 'CODEC': 'h264'}
        self.setting.setdefault('parameter', {})
        for key, default in param_defaults.items():
            self.setting['parameter'].setdefault(key, default)

        # Ensure 'cameras' section exists and is a list
        if 'cameras' not in self.setting or not isinstance(self.setting['cameras'], list):
            raise ValueError("The 'cameras' section must be a list and cannot be empty.")

        # Extract values to simplify further usage
        self.w = self.setting['parameter']['WIDTH']
        self.h = self.setting['parameter']['HEIGHT']
        self.gst_enable = self.setting['parameter']['GSTREAMER']
        self.codec = self.setting['parameter']['CODEC']

    def _generate_rtsp_strings(self):
        # Gstreamer pipeline
        if self.gst_enable:
            cpu_arch = platform.machine()
            if cpu_arch == 'x86_64':
                gst_pipeline = [
                    f'queue max-size-buffers=0 max-size-bytes={1024*1024} leaky=downstream',  # 1MB buffer to keep GOP not be truncated
                    f'rtp{self.codec}depay', 
                    f'{self.codec}parse', 
                    f'avdec_{self.codec}', 
                    'videoconvert n-threads=1', 
                    'appsink drop=true sync=false'
                ]
                # gst_pipeline = [
                #     f'queue max-size-buffers=0 max-size-bytes={1024*1024} leaky=downstream',
                #     f'rtp{self.codec}depay', 
                #     f'{self.codec}parse', 
                #     f'nv{self.codec}dec',
                #     'nvvideoconvert'  # it is important to use nvvideoconvert after nv{codec}dec for performance
                #     'queue max-size-buffers=1 leaky=downstream',
                #     'videoconvert n-threads=1',  # it is important to add convert after nvvideoconvert for performance
                #     'video/x-raw, format=RGBA',
                #     'appsink caps="video/x-raw,format=BGR drop=true sync=false'
                # ]
            elif cpu_arch == 'aarch64' and is_jetson():
                gst_pipeline = [
                    f'queue max-size-buffers=0 max-size-bytes={1024*1024} leaky=downstream',
                    f'rtp{self.codec}depay', 
                    f'{self.codec}parse', 
                    'nvv4l2decoder',  #  drop-frame has some problem, disable-dpb=true need the stream with no B-frames
                    'nvvidconv', 
                    'queue max-size-buffers=1 leaky=downstream',
                    'video/x-raw,format=RGBA',          # explicitly set RGBA format for system memory
                    'videoconvert n-threads=1',         
                    'video/x-raw,format=BGR',           # cap filter, ensure the output is in BGR format
                    'appsink drop=true sync=false'
                ]
                # gst_pipeline = [
                #     f'rtp{self.codec}depay', f'{self.codec}parse', 'nvv4l2decoder', 
                #     'nvvidconv', 'appsink drop=true sync=false'
                # ]
            else:
                gst_pipeline = []
                print('Not allow to use Gstreamer under the current platform! (Only support x86_64 and Jetson)')
        
        # Collect RTSP strings
        self.rtsp_strings = [[] for _ in range(self.num)]

        for i in range(len(self.setting['cameras'])):
            camera = self.setting['cameras'][i]
            for rtsp in camera['rtsp']:
                ip = rtsp['ip']
                user = rtsp['user']
                pw = rtsp['pw']
                if self.gst_enable and gst_pipeline:
                    # Gstreamer pipeline
                    rtspsrc_base  = f'rtspsrc location=rtsp://{ip}'
                    if user and pw:
                        rtspsrc_base += f' user-id={user} user-pw={pw}'

                    # https://forums.developer.nvidia.com/t/deepstream-losing-relevance-because-of-outdated-dependecies/203426/7?utm_source=chatgpt.com 
                    rtspsrc_params = [
                        'short-header=true',
                        'is-live=true',
                        'protocols=tcp',
                        # 'latency=200',
                        # 'drop-on-latency=true',
                        # 'timeout=10',
                        # 'tcp-timeout=5',
                        # 'retry=3',
                        # 'do-retransmission=false'
                    ]
                    rtspsrc = rtspsrc_base + ' ' + ' '.join(rtspsrc_params)
                    
                    # Gstreamer pipeline put in front of the default rtsp
                    if len(self.rtsp_strings[i]) > 1:
                        index = len(self.rtsp_strings[i])//2
                        self.rtsp_strings[i].insert(index, ' ! '.join([rtspsrc] + gst_pipeline))
                    else:
                        self.rtsp_strings[i].append(' ! '.join([rtspsrc] + gst_pipeline))

                # if Gstreamer is not used, use the default rtsp
                if user and pw:
                    self.rtsp_strings[i].append(f'rtsp://{user}:{pw}@{ip}')
                else:
                    self.rtsp_strings[i].append(f'rtsp://{ip}')
        
    def __len__(self):
        return self.num
    
    def init_cameras(self, i):
        """Initialize all cameras based on the configuration settings."""
        for rtsp in self.rtsp_strings[i]:
            self.caps[i] = self._open_camera(rtsp, self.gst_enable)
            self.caps_info[i] = self._get_info(self.caps[i])
            
            if self.caps[i].isOpened():
                self.status[i] = True
                self.rtsp_reconnect[i] = rtsp
                if self.verbose:
                    print(f'camera {i}:', self.caps_info[i], flush=True)
                break
            else:
                self.status[i] = False
                if self.verbose:
                    print(f'camera {i}: failed to open initially', flush=True)

    def stop(self):
        """Stop all camera threads."""
        self.running = False

    def release(self):
        """Stop all camera threads and release resources."""
        self.running = False
        time.sleep(0.1)
        for cap in self.caps:
            if cap.isOpened():
                cap.release()
        # Wait for threads to finish
        for thread in self.threads:
            thread.join()
        
    def run(self):
        """Start the camera streaming threads."""
        self.threads = []
        for i in range(self.num):
            t = threading.Thread(
                target=self._run_one,
                args=(i, ),
                daemon=True
                )
            t.start()
            self.threads.append(t)
        
    def get_frames(self, status=False):
        """
        Retrieve the latest frames from all cameras. 
        Optionally include status.
        """
        with self.mutex:
            frames = self.frames.copy()
            if status:
                return frames, self.status.copy()
            return frames
            
    def _run_one(self, i):
        """Handle the streaming of one individual camera."""
        self.init_cameras(i)
        cap = self.caps[i]
        resize = (self.caps_info[i]['w'], self.caps_info[i]['h']) != (self.w, self.h)
        reconnect_time = time.time() - self.reconnect_interval
        
        try:
            while self.running:
                # successfully read frame
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        if self.verbose and not self.status[i]:
                                print(f'camera {i} reconnects successfully', flush=True)
                        if resize:
                            frame = cv2.resize(frame, (self.w, self.h))
                        with self.mutex:
                            self.frames[i] = frame
                            self.status[i] = True
                        time.sleep(0.02)
                        continue
                
                # camera is not open or failed to read frame
                with self.mutex:
                    self.frames[i] = np.zeros((self.h, self.w, 3), dtype=np.uint8)
                    self.status[i] = False
                    
                if time.time() - reconnect_time > self.reconnect_interval:
                    reconnect_time = time.time()
                    if self.verbose:
                        print(f'camera {i} is not open, try reconnecting', flush=True)
                    if cap.isOpened():
                        cap.release()
                    if self.rtsp_reconnect[i]:
                        self.caps[i] = self._open_camera(self.rtsp_reconnect[i], self.gst_enable)
                        if self.caps[i].isOpened() == False:
                            self.rtsp_reconnect[i] = None
                    else:
                        for rtsp in self.rtsp_strings[i]:
                            self.caps[i] = self._open_camera(rtsp, self.gst_enable)
                            if self.caps[i].isOpened():
                                self.rtsp_reconnect[i] = rtsp
                                break
                    self.caps_info[i] = self._get_info(self.caps[i])
                    cap = self.caps[i]
                    resize = (self.caps_info[i]['w'], self.caps_info[i]['h']) != (self.w, self.h)    
                
                time.sleep(0.02)
        finally:
            if cap.isOpened():
                cap.release()
    
    @staticmethod
    def _open_camera(rtsp, gst):
        """Open a camera using the given RTSP stream and settings for GStreamer."""
        def _open(cap):
            cap.open(rtsp, cv2.CAP_GSTREAMER) if gst else cap.open(rtsp)
                
        cap = cv2.VideoCapture()
        t = threading.Thread(
            target=_open, 
            args=(cap,), 
            daemon=True
            )
        t.start()
        t.join(15)
        
        return cap
    
    @staticmethod
    def _get_info(cap):
        """Return camera properties such as width, height, FPS, and codec."""
        try:
            if cap.isOpened():
                w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                fps = cap.get(cv2.CAP_PROP_FPS)
                fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
                codec_format = ''.join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
                return {
                    'w': int(w),
                    'h': int(h),
                    'fps': int(fps),
                    'codec': codec_format
                }
        except Exception as e:
            print(f"Error getting camera properties: {e}", flush=True)

        return {
            'w': 0,
            'h': 0,
            'fps': 0,
            'codec': ''
        }