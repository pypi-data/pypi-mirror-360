import numpy as np
import time
from PIL import Image, ImageDraw, ImageFont


def _cosine_distance(a, b, data_is_normalized=False):
    """Compute pair-wise cosine distance between points in `a` and `b`.
    Parameters
    ----------
    a : array_like
        An NxM matrix of N samples of dimensionality M.
    b : array_like
        An LxM matrix of L samples of dimensionality M.
    data_is_normalized : Optional[bool]
        If True, assumes rows in a and b are unit length vectors.
        Otherwise, a and b are explicitly normalized to lenght 1.
    Returns
    -------
    ndarray
        Returns a matrix of size len(a), len(b) such that eleement (i, j)
        contains the squared distance between `a[i]` and `b[j]`.
    """
    if not data_is_normalized:
        a = np.asarray(a) / np.linalg.norm(a, axis=1, keepdims=True)
        b = np.asarray(b) / np.linalg.norm(b, axis=1, keepdims=True)
        
    return 1. - np.dot(a, b.T)

def cosine_distance_to_image_center(bbox, image_size):
    """
    Calculates the absolute cosine distance subtracted by 1, from an up vector located at the image center to
    the specified bbox.

    Inputs:
        bbox - bounding box of type (x pos, y pos, s area, r aspect ratio), shape (1, 4)
        image_size - tuple (width, height)

    Returns:
        Absolute value of cosine distance subtracted by 1 (higher values means further away from up vector located
        at image center)
    """
    up_vector = np.asarray([[0., 1., 0., 0.]])
    image_center_pos = np.asarray([[image_size[0] / 2., image_size[1] / 2., 0., 0.]])
    
    return np.abs(_cosine_distance(up_vector, bbox - image_center_pos).flatten() - 1)[0]

def speed_direction(bbox1, bbox2):
    cx1, cy1 = (bbox1[0]+bbox1[2]) / 2.0, (bbox1[1]+bbox1[3])/2.0
    cx2, cy2 = (bbox2[0]+bbox2[2]) / 2.0, (bbox2[1]+bbox2[3])/2.0
    speed = np.array([cy2-cy1, cx2-cx1])
    norm = np.sqrt((cy2-cy1)**2 + (cx2-cx1)**2) + 1e-6
    
    return speed / norm

def convert_bbox_to_z(bbox):
    """
    Takes a bounding box in the form [x1,y1,x2,y2] and returns z in the form
      [x,y,s,r] where x,y is the centre of the box and s is the scale/area and r is
      the aspect ratio
    """
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = bbox[0] + w/2.
    y = bbox[1] + h/2.
    s = w * h  # scale is just area
    r = w / float(h+1e-6)
    
    return np.array([x, y, s, r]).reshape((4, 1))

def convert_x_to_bbox(x, score=None):
    """
    Takes a bounding box in the centre form [x,y,s,r] and returns it in the form
      [x1,y1,x2,y2] where x1,y1 is the top left and x2,y2 is the bottom right
    """
    w = np.sqrt(x[2] * x[3])
    h = x[2] / w
    if(score == None):
      return np.array([x[0]-w/2., x[1]-h/2., x[0]+w/2., x[1]+h/2.]).reshape((1, 4))
    else:
      return np.array([x[0]-w/2., x[1]-h/2., x[0]+w/2., x[1]+h/2., score]).reshape((1, 5))

#紀錄track的狀態----超過min_hits才變confirm！（避免錯誤偵測也追蹤）
class TrackState:

    initial = 1
    Confirmed = 2
    Deleted = 3

class KalmanBoxTracker(object):
    """
    This class represents the internal state of individual tracked objects observed as bbox.
    """
    count = 0
    def __init__(self, bbox, max_age, min_hits, cls, delta_t=3, orig=False, use_feature = False, image_size=(0, 0), id = 0, dir_history_num=10): 
        self.image_size = image_size
        # box ---> [0:4] = bbox, [4]:confs [5]:classes [6:] positions [7:] features
        """
        Initialises a tracker using initial bounding box.

        """
        # define constant velocity model
        if not orig:
          from .kalmanfilter import KalmanFilterNew as KalmanFilter
          self.kf = KalmanFilter(dim_x=7, dim_z=4)
        # else:
        #   from filterpy.kalman import KalmanFilter
        #   self.kf = KalmanFilter(dim_x=7, dim_z=4)        
        '''
        testing
        '''
        
        self.kf.F = np.array([
            [1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1]])
        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0]])

        """
            Motion and observation uncertainty are chosen relative to the current
            state estimate. These weights control the amount of uncertainty in
            the model. This is a bit hacky.
        """
        self._std_weight_position = 10.
        self._std_weight_size = 1. / 20
        self._std_weight_velocity = 20.

        state_space_bbox = convert_bbox_to_z(bbox)

        dist = cosine_distance_to_image_center(state_space_bbox, self.image_size)
        std = [
            2 * self._std_weight_position * dist + 1,  # the center point x
            2 * self._std_weight_position * dist + 1,  # the center point y
            2 * self._std_weight_size * state_space_bbox[2][0],  # the scale (area)
            1 * state_space_bbox[3][0],  # the ratio of width/height
            10 * self._std_weight_velocity * dist + 1,
            10 * self._std_weight_velocity * dist + 1,
            10 * self._std_weight_velocity * dist + 1]
        self.kf.P = np.diag(np.square(std).flatten())

        self.kf.x[:4] = state_space_bbox
        '''
        testing
        '''
        
        # self.kf.R[2:, 2:] *= 10.
        # self.kf.P[4:, 4:] *= 1000.  # give high uncertainty to the unobservable initial velocities
        # self.kf.P *= 10.
        # self.kf.Q[-1, -1] *= 0.01
        # self.kf.Q[4:, 4:] *= 0.01

        # self.kf.x[:4] = convert_bbox_to_z(bbox[:4])
        self.time_since_update = 0
        # self.id = KalmanBoxTracker.count
        # KalmanBoxTracker.count += 1
        self.id = id
        
        self.history = []
        self.hits = 0
        self.hit_streak = 0
        self.age = 0
        self.conf = bbox[4]
        if use_feature:
            self.feature = bbox[7:]#特徵
        self.tmp_index = bbox[6] #for mapping det id
        self.last_pos = None #上一期的pos
        
        self.cls = cls
        self._n_hits = min_hits #最少hit幾次就confirm
        self._max_age = max_age #confirm track多久後沒出現就delete
        self.state = TrackState.initial #紀錄track當前狀態
        self.use_feature = use_feature #使用外觀特徵or_not
        self.count_flag = False #記錄是否被累加過，針對人流、車流、進來的總人數or出去的總人數做控管
        """
        NOTE: [-1,-1,-1,-1,-1] is a compromising placeholder for non-observation status, the same for the return of 
        function k_previous_obs. It is ugly and I do not like it. But to support generate observation array in a 
        fast and unified way, which you would see below k_observations = np.array([k_previous_obs(...]]), let's bear it for now.
        """
        self.last_observation = np.array([-1, -1, -1, -1, -1])  # placeholder
        self.observations = dict()
        self.history_observations = []
        self.velocity = None
        self.delta_t = delta_t
        self.dir_history_num = dir_history_num

        self.time = time.time()
        self.speed = 0
        self.direction = None


    def update(self, bbox, cls):
        # [0:4] = bbox, [4]:confs [5]:classes [6:] input_index [7:] features
        """
        Updates the state vector with observed bbox.
        """
        
        if bbox is not None:
            self.conf = bbox[4]
            self.cls = cls
            if self.use_feature:
                self.feature = bbox[7:]
            if self.last_observation.sum() >= 0:  # no previous observation
                previous_box = None
                for i in range(self.delta_t):
                    dt = self.delta_t - i
                    if self.age - dt in self.observations:
                        previous_box = self.observations[self.age-dt]
                        break
                if previous_box is None:
                    previous_box = self.last_observation
                """
                  Estimate the track speed direction with observations \Delta t steps away
                """
                self.velocity = speed_direction(previous_box, bbox)
            
            
            """
            Update covariance matrices
            """
            dist = cosine_distance_to_image_center(bbox[:4].reshape(1, -1), self.image_size)
            std = [
                2. * self._std_weight_position * dist + 1,
                2. * self._std_weight_position * dist + 1,
                self._std_weight_size * self.kf.x[2][0],
                1 * self.kf.x[3][0]]
            std = [(2 - self.conf) * x for x in std]
            self.kf.R = np.diag(np.square(std).flatten())
            
            
            
            """
              Insert new observations. This is a ugly way to maintain both self.observations
              and self.history_observations. Bear it for the moment.
            """
            self.last_observation = bbox[:5]
            self.observations[self.age] = bbox[:5]
            self.history_observations.append(bbox[:5])
            if len(self.history_observations) > self.dir_history_num:
                self.history_observations = self.history_observations[-self.dir_history_num-1:] # is a ugly way for same with simple track!!

            self.time_since_update = 0
            self.hits += 1
            if self.state == TrackState.initial and self.hits >= self._n_hits:
                self.state = TrackState.Confirmed
            self.history = []
            self.hit_streak += 1
            self.kf.update(convert_bbox_to_z(bbox[:5]))

        else:
            self.kf.update(bbox)

    def predict(self):
        """
        Advances the state vector and returns the predicted bounding box estimate.
        """
        if((self.kf.x[6]+self.kf.x[2]) <= 0):
            self.kf.x[6] *= 0.0
        '''
        test
        '''
        # Update process noise
        dist = cosine_distance_to_image_center(self.kf.x, self.image_size)
        std_pos = [
            self._std_weight_position * dist + 1,
            self._std_weight_position * dist + 1,
            self._std_weight_size * self.kf.x[2][0],
            1 * self.kf.x[3][0]]
        std_vel = [
            self._std_weight_velocity * dist + 1,
            self._std_weight_velocity * dist + 1,
            self._std_weight_velocity * dist + 1]
        self.kf.Q = np.diag(np.square(np.r_[std_pos, std_vel]).flatten())
        '''
        test
        '''
        self.kf.predict()
        self.age += 1
        if(self.time_since_update > 0):
            self.hit_streak = 0
        self.time_since_update += 1
        self.history.append(convert_x_to_bbox(self.kf.x))
        return self.history[-1]


    def get_state(self):
        """
        Returns the current bounding box estimate.
        """
        return convert_x_to_bbox(self.kf.x)
    
    def mark_missed(self):
        """Mark this track as missed (no association at the current time step).
        """
        if self.state == TrackState.initial:
            self.state = TrackState.Deleted
        elif self.time_since_update > self._max_age:
            self.state = TrackState.Deleted

    def is_initial(self):
        """Returns True if this track is tentative (unconfirmed).
        """
        return self.state == TrackState.initial

    def is_confirmed(self):
        """Returns True if this track is confirmed."""
        return self.state == TrackState.Confirmed

    def is_deleted(self):
        """Returns True if this track is dead and should be deleted."""
        return self.state == TrackState.Deleted    