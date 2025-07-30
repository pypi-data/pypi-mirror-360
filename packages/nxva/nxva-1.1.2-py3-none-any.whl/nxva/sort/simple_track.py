import numpy as np
import time

from .utils.KMmatcher import KMmatcher

from .utils.association import diou_batch
from .utils.tools import get_speed_direction

class SimpleTracker():
    def __init__(self, 
                 iou_threshold, 
                 max_age,
                 pos_lambda=(0.5, 0.5),
                 direction_type='vector',
                 dir_history_num=10
                 ):
        '''
        Args:
            w: 
                int, width of the image, ex: 1920
            h: 
                int, height of the image, ex: 1080
            iou_threshold: 
                float, threshold for matching between two bounding boxes
            max_age: 
                int, maximum number of frames to tolerate disappear
            line_pts: 
                list of 2 points for cross_line ->  [[0,0],[1,1]] 
            inside_pts: 
                list of a points                ->  [0,0]
        '''
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.pos_lambda = pos_lambda
        self.direction_type = direction_type
        self.dir_history_num = dir_history_num

        self.track_list = []
        self.unique_id = 0

    # get current track_list
    def get_track_ids(self):
        lst = []
        for track in self.track_list:
            lst.append(track['uid'])
            
        return lst 
    
    def get_appear_results(self):
        trk_lst = {}
        for track in self.track_list:
            trk_lst[track['uid']] = {'appear':track['appear'], 'disappear':track['disappear']}
        return trk_lst

    def get_update_results(self):
        # if didn't update, return None
        if len(self.update_lst['new_ids']) == 0 and len(self.update_lst['disappeared_ids']) == 0:
            return None
        else:
            return self.update_lst

    def run(self, result):
        """
            args:
                result: n x 6        [0-3=boxes, 4=confidence, 5=class]
            return:
                track_results: n x 1 [0=uid]
                cross_results: n x 2 [0=pos, 1=cross], cross = 0: no event, +-1: cross line
        """
        # initial update value
        track_results = np.ones(len(result)) * (-1)
        speed_results = np.zeros(len(result))
        direction_results = np.zeros((len(result), 2)) if self.direction_type == 'vector' else np.zeros(len(result))


        self.update_lst = {'new_ids': [], 'disappeared_ids': []}

        if isinstance(result, np.ndarray) and result.shape[0]:
            """
            Match track list
            """ 
            if len(self.track_list) > 0:
                track_bboxs = np.stack([track['bbox'] for track in self.track_list])
                dious_c = diou_batch(track_bboxs, result[:, :4])
                dious_c[np.where(dious_c < self.iou_threshold)] = -100
                
                # match
                if dious_c.shape[0] <= dious_c.shape[1]:
                    matcher = KMmatcher(dious_c)
                    matcher.solve()
                    match = matcher.xy
                else:
                    matcher = KMmatcher(dious_c.T)
                    matcher.solve()
                    match = matcher.yx
                    
            # check in track list
            for t in range(len(self.track_list)):
                m = match[t]
                if (m == -1) or (dious_c[t, m] == -100):
                    self.track_list[t]['disappear'] += 1
                    self.track_list[t]['appear'] = 0
                else:
                    # remove the index of result which is match to track list
                    last_time = self.track_list[t]['time']
                    cur_time = time.time()
                    pre_n_box = self.track_list[t]['history_bbox'][0]

                    speed, direction = get_speed_direction(last_time, 
                                                           cur_time,
                                                           pre_box=self.track_list[t]['history_bbox'][-1],
                                                           pre_n_box=pre_n_box,
                                                           cur_box=result[m, :4],
                                                           pos_lambda=self.pos_lambda,
                                                           direction_type=self.direction_type)
                    
                    # # 取得pre_direction
                    # if self.track_list[t]['direction'] is not None:
                    #     last_direction = self.track_list[t]['direction']
                    
                    self.track_list[t]['bbox'] = result[m, :4]  # inherit
                    self.track_list[t]['history_bbox'].append(result[m, :4])
                    if len(self.track_list[t]['history_bbox']) > self.dir_history_num:
                        self.track_list[t]['history_bbox'] = self.track_list[t]['history_bbox'][-self.dir_history_num:]
                    self.track_list[t]['appear'] += 1
                    self.track_list[t]['disappear'] = 0
                    self.track_list[t]['time'] = cur_time
                    self.track_list[t]['speed'] = speed
                    self.track_list[t]['direction'] = direction # cur_direction


                    track_results[m] = self.track_list[t]['uid']
                    speed_results[m] = self.track_list[t]['speed']
                    direction_results[m] = self.track_list[t]['direction']

                    
            # adjust track list
            update_track_list = []
            for track in self.track_list:
                if track['disappear'] >= self.max_age:
                    self.update_lst['disappeared_ids'].append(track['uid'])
                else:
                    update_track_list.append(track)
            self.track_list = update_track_list

            not_match_idx = [idx for idx, value in enumerate(track_results) if value == -1]
            # not_match_idx = np.argwhere(track_results == -1).flatten().tolist()
            for r in not_match_idx:
                self.track_list.append({'bbox': result[r, :4],
                                        'uid': self.unique_id,
                                        'appear': 1,
                                        'disappear': 0,
                                        'time': time.time(),
                                        'speed': 0,
                                        'direction': None,
                                        'history_bbox':[result[r, :4]]
                                        })
                self.update_lst['new_ids'].append(self.unique_id)
                track_results[r] = self.unique_id
                self.unique_id += 1
            

        else:
            for t in range(len(self.track_list)):
                self.track_list[t]['disappear'] += 1
                self.track_list[t]['appear'] = 0

            # adjust track list
            update_track_list = []
            for track in self.track_list:
                if track['disappear'] >= self.max_age:
                    self.update_lst['disappeared_ids'].append(track['uid'])
                else:
                    update_track_list.append(track)
            self.track_list = update_track_list
        

        return track_results, speed_results, direction_results
    
