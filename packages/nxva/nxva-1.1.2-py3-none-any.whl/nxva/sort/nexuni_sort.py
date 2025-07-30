import numpy as np
import time

from .track import KalmanBoxTracker
from .reid_multibackend import ReIDDetectMultiBackend
from .utils.tools import nn_cosine_distance, xyxy2xywh, k_previous_obs, get_speed_direction
from .utils.association import iou_batch, giou_batch, ciou_batch, diou_batch, ct_dist, associate, linear_assignment
import torch

ASSO_FUNCS = {  "iou": iou_batch, # IoU計算方式選擇(in association.py)
    "giou": giou_batch,
    "ciou": ciou_batch,
    "diou": diou_batch,
    "ct_dist": ct_dist}

class NexuniSort(): #參照OCSort的架構, 融合StrongSort的特徵計算(不用特徵的話=只用IoU重疊來匹配)
    def __init__(self,
            settings):
        self.trackers = [] #儲存track
        self.device = settings['device']
        self.max_age = settings['max_age']
        self.min_hits = settings['min_hits']
        self.asso_func = ASSO_FUNCS[settings['asso_func']]
        self.delta_t = settings['delta_t']
        self.inertia = settings['inertia']
        self.iou_threshold = settings['iou_threshold']
        self.det_thresh = settings['det_thresh']#用以分辨高(>det_thresh)、中(0.1、det_thresh之間)、低分框(<0.1)
        self.pos_lambda = settings['pos_lambda']
        self.direction_type = settings['direction_type']
        self.count = 0
        self.dir_history_num = settings['dir_history_num']

        self.use_byte = settings['use_byte']                
        if self.use_byte:
            self.det_thresh_byte = settings['iou_threshold'] #低分框的threshold

        self.use_feature = settings['use_feature'] #是否要看特徵，否則純看IoU
        if self.use_feature: # strong_sort 的特徵
            self.samples = {} #用來存unique ID的特徵向量
            self.max_budget = settings['max_budget'] #每一個id可以儲存的特徵數量
            self.model = ReIDDetectMultiBackend(weights=settings['reid_weights'], device=self.device, fp16=settings['fp16'], pretrained=True) #ReID模型（特徵模型）
            img = torch.zeros((1, 3, 1920, 1080))
            features_len = len(self.model(img)[0])
            self.no_features = np.zeros((0, features_len))
            self.lamda = settings['lamda'] #cost appear_cost的權重
            self.appear_threshold = settings['appear_threshold'] # 特徵threshold
    
    def distance(self, features, targets): #計算"特徵"的距離(參考strong sort), 也可以使用歐式距離（但我沒寫), 以及我改寫原code的餘弦距離（改成愈大愈好，為了跟IoU分數加總）
        """Compute distance between features and targets.
        Parameters
        ----------
        features : ndarray
            An NxM matrix of N features of dimensionality M.
        targets : List[int]
            A list of targets to match the given `features` against.
        Returns
        -------
        ndarray
            Returns a cost matrix of shape len(targets), len(features), where
            element (i, j) contains the closest squared distance between
            `targets[i]` and `features[j]`.
        """
        # 結論：計算每一個當前bbox對應之前track的特徵距離計算（保留最大者的值)
        cost_matrix = np.zeros((len(targets), len(features)))
        for i, target in enumerate(targets):
            cost_matrix[i, :] = nn_cosine_distance(self.samples[target], features)
        #我需要 len(features), len(targets) #features=當前bbox, target=track_bbox, 故轉至
        #需要轉至 變成當前bbox對上track(因為我IoU匹配也是bbox對track)
        return cost_matrix.T 
        
    #更新每個ID的特徵 (strongsort)，並只考慮conf >= 0.7者，避免分數太低的特徵搗亂(遮擋)
    def partial_fit(self, features, targets, conf): 
        for i, (feature, target) in enumerate(zip(features, targets)):

            self.samples.setdefault(target, []).append(feature)
            if conf[i] < 0.7: #只保留高分框的特徵, 低分框會有雜質
                continue 
            if self.max_budget is not None: #避免存太多特徵量, 單一object最多只有max_budget個特徵儲存）
                self.samples[target] = self.samples[target][-self.max_budget:]
    
    def _get_features(self, bbox_xywh, ori_img): #抽取bbox特徵
        im_crops = []
        for box in bbox_xywh:
            x1, y1, x2, y2 = self._xywh_to_xyxy(box)
            im = ori_img[y1:y2, x1:x2]
            im_crops.append(im)

        if im_crops:
            features = self.model(im_crops)
        else:
            features = self.no_features.copy()
            
        return features
    
    def get_update_results(self):
        # if didn't update, return None
        if len(self.update_lst['new_ids']) == 0 and len(self.update_lst['disappeared_ids']) == 0:
            return None
        else:
            return self.update_lst
        
    def _xywh_to_xyxy(self, bbox_xywh):
        x, y, w, h = bbox_xywh
        x1 = max(int(x - w / 2), 0)
        x2 = min(int(x + w / 2), self.width - 1)
        y1 = max(int(y - h / 2), 0)
        y2 = min(int(y + h / 2), self.height - 1)
        
        return x1, y1, x2, y2
    
    def run(self, dets, ori_img): #KalmanFilter更新狀態位置
        """
        Params:
            dets - a numpy array of detections in the format [[x1,y1,x2,y2,score],[x1,y1,x2,y2,score],...]
        Requires: 
            this method must be called once for each frame even with empty detections (use np.empty((0, 5)) for frames without detections).
        Returns:
            the a similar array, where the last column is the object ID.
        """
        # init results
        # track_results = [-1 for i in range(len(dets))]
        track_results = np.ones(len(dets)) * (-1)
        speed_results = np.zeros(len(dets))
        direction_results = np.zeros((len(dets), 2)) if self.direction_type == 'vector' else np.zeros(len(dets))

        self.update_lst = {'new_ids': [], 'disappeared_ids': []}

        #先處理track的東西，避免沒有det到東西，track沒更新後就回傳，因此先處理track,再看有沒有det，來進行下一步
        # get predicted locations from existing trackers. trks用來儲存tracking

        # to_del = [] #若有刪除狀態的track, pop it    
        pred_results = [] #儲存pred_box
        trks = np.zeros((len(self.trackers), 6))
        #填滿trks
        for t, trk in enumerate(trks):
            #確認track狀態為confirmed才繼續
            pos = self.trackers[t].predict()[0] #拿上一幀的框先預測變成track, 以便後面匹配
            trk_id = self.trackers[t].id 
            trk[:] = [pos[0], pos[1], pos[2], pos[3], 0, trk_id+1] #多放id在後面

            pred_results.append([pos[0], pos[1], pos[2], pos[3]])
        trks = np.ma.compress_rows(np.ma.masked_invalid(trks))

        # 沒det，track需要更新空的，並且確認是否miss掉
        # if not(isinstance(dets, np.ndarray) and dets.shape[0]):
        if dets is None:
            if trks is not None:
                delete_list = []
                for m, trk in enumerate(trks):
                    self.trackers[m].update(None, None)
                    self.trackers[m].mark_missed() #檢查是否遺失太久， >= max_age -> deleted
                    if trk.is_deleted():
                        delete_list.append(m)
                        self.update_lst['disappeared_ids'].append(trk.id)
                for i in reversed(delete_list):
                    self.trackers.pop(i)

            if len(self.update_lst['disappeared_ids']) == 0:
                self.update_lst = None

            tracking_results = {
                'track_results': track_results,
                'speed_results': speed_results,
                'direction_results': direction_results,
                'feature_results': None
            }

            return tracking_results

        xyxys = dets[:, 0:4]
        confs = dets[:, 4]
        classes = dets[:, 5]
        #檢測bbox相對線之位置, 新增一個index-id（order to map the track
        index_lst = []
        for i in range(len(xyxys)):
            index_lst.append(i)

        # 抽取目前bbox特徵(新增的--從strongsort copy過來，並stack起來)
        self.height, self.width = ori_img.shape[:2]
        xywhs = xyxy2xywh(xyxys)
        if self.use_feature: #若有考慮特徵, 則先擷取特徵, 並stack起來
            feature = self._get_features(xywhs, ori_img)
            if isinstance(feature, torch.Tensor):
                features = feature.cpu().detach().numpy()
            elif isinstance(feature, np.ndarray):
                features = feature

            # [0:4] = bbox, [4]:confs [5]:classes [6:]det_results_index [7:] features
            output_results = np.column_stack((xyxys, confs, classes, index_lst, features))
        else:
            output_results = np.column_stack((xyxys, confs, classes, index_lst))
        
        # 將detection分成三等分（高、中、低）
        inds_low = confs > 0.1
        inds_middle = confs < self.det_thresh
        inds_second = np.logical_and(inds_low, inds_middle)  # self.det_thresh > score > 0.1, for second matching
        
        #高分框
        inds_high = confs >= self.det_thresh
        dets_high = output_results[inds_high]  #高分框(若有use_byte則是det_thresh, 否則是conf_thres)
        #中分框
        if self.use_byte: #若有use_byte:考慮中分框，先存起來以最後initial方便
            dets_second = output_results[inds_second]  # detections for second matching  
            unmatched_dets_second = []
            for i in range(len(dets_second)):
                unmatched_dets_second.append(i)
        
        b_features = [] # b_features暫存feature_list
        velocities = np.array(
            [trk.velocity if trk.velocity is not None else np.array((0, 0)) for trk in self.trackers])
        last_boxes = np.array([trk.last_observation for trk in self.trackers])
        k_observations = np.array(
            [k_previous_obs(trk.observations, trk.age, self.delta_t) for trk in self.trackers])
        """
            First round of association 先針對高分框, 進行匹配,（若有use_feature, 則combine一起配對, 否則單純看IoU)
        """ 
        matching_table =[]
        matched, unmatched_dets, unmatched_trks = associate(self,
            dets_high, trks, velocities, k_observations, self.inertia, self.use_feature)
        if len(matched) != 0:
            for det_index, track_index in matched:
                matching_table.append([int(dets_high[det_index][6]), track_index])
        for m in matched:
            self.trackers[m[1]].update(dets_high[m[0], :], dets_high[m[0], 5])

        """
            Second round of associaton by OCR (下面都只考慮bbox的IoU匹配分數)
            可以調整的有assoc_func(也就是bbox的IoU方式選擇:giou、ciou、diou、iou、ct_dist)
            (1)若use_feature :  
                1.第二階段先將剩餘的高分框unmatched_det與unmatched_trks匹配！(避免有高分框因特徵太相似而被忽略)
                2.再將剩餘的unmatched_trks與中分框匹配
            (2)else:
                1.由於第一階段單純只考慮IoU，故接下來先將中分框與unmatched_trks匹配
                2.再將剩下的unmatched_trks與第一階段沒匹配的unmatched_det匹配                    
        """
        # 針對剩下的unmatched_trks和高分框的unmatched_dets「進行單純IoU匹配」
        if self.use_feature:
            if unmatched_dets.shape[0] > 0 and unmatched_trks.shape[0] > 0:
                left_dets = dets_high[unmatched_dets]
                # left_trks = last_boxes[unmatched_trks]
                left_trks = trks[unmatched_trks]
                
                iou_left = self.asso_func(left_dets, left_trks)
                iou_left = np.array(iou_left)
                if iou_left.max() > self.iou_threshold:  
                    """
                        NOTE: by using a lower threshold, e.g., self.iou_threshold - 0.1, you may
                        get a higher performance especially on MOT17/MOT20 datasets. But we keep it
                        uniform here for simplicity
                    """
                    rematched_indices = linear_assignment(-iou_left)
                    to_remove_det_indices = []
                    to_remove_trk_indices = []
                    for m in rematched_indices:
                        det_ind, trk_ind = unmatched_dets[m[0]], unmatched_trks[m[1]]
                        matching_table.append([int(dets_high[det_ind][6]), trk_ind])

                        if iou_left[m[0], m[1]] < self.iou_threshold:
                            continue
                        self.trackers[trk_ind].update(dets_high[det_ind, :], dets_high[det_ind, 5])

                        to_remove_det_indices.append(det_ind)
                        to_remove_trk_indices.append(trk_ind)

                    unmatched_dets = np.setdiff1d(unmatched_dets, np.array(to_remove_det_indices))
                    unmatched_trks = np.setdiff1d(unmatched_trks, np.array(to_remove_trk_indices))

                    # if len(rematched_indices) != 0:
                    #     for det_index, track_index in rematched_indices:
                    #         matching_table.append([int(dets_high[det_index][7]), unmatched_trks[track_index]])

            # BYTE association 針對中分框, 且有un_matched_track時，若iou重合 > threshold ---> 進行匹配
            if self.use_byte and len(dets_second) > 0 and unmatched_trks.shape[0] > 0:
                u_trks = trks[unmatched_trks]
                iou_left = self.asso_func(dets_second, u_trks)          # iou between low score detections and unmatched tracks
                iou_left = np.array(iou_left)
                if iou_left.max() > self.det_thresh_byte:
                    """
                        NOTE: by using a lower threshold, e.g., self.iou_threshold - 0.1, you may
                        get a higher performance especially on MOT17/MOT20 datasets. But we keep it
                        uniform here for simplicity
                    """
                    matched_indices = linear_assignment(-iou_left)
                    to_remove_trk_indices = []
                    to_remove_detsecond_indices = []
                    for m in matched_indices:
                        det_ind, trk_ind = m[0], unmatched_trks[m[1]]
                        matching_table.append([int(dets_second[det_ind][6]), trk_ind])

                        if iou_left[m[0], m[1]] < self.det_thresh_byte:
                            continue
                        self.trackers[trk_ind].update(dets_second[det_ind, :], dets_second[det_ind, 5])
     
                        to_remove_trk_indices.append(trk_ind)
                        to_remove_detsecond_indices.append(det_ind)

                    unmatched_dets_second = np.setdiff1d(unmatched_dets_second, np.array(to_remove_detsecond_indices))
                    unmatched_trks = np.setdiff1d(unmatched_trks, np.array(to_remove_trk_indices))
            
                # if len(matched_indices) != 0:
                #     for det_index, track_index in matched_indices:
                #         matching_table.append([int(dets_second[det_index][7]), unmatched_trks[track_index]])
        else:
            # BYTE association 針對中分框, 且有un_matched_track時，若iou重合 > threshold ---> 進行匹配
            if self.use_byte and len(dets_second) > 0 and unmatched_trks.shape[0] > 0:
                u_trks = trks[unmatched_trks]
                iou_left = self.asso_func(dets_second, u_trks)          # iou between low score detections and unmatched tracks
                iou_left = np.array(iou_left)
                if iou_left.max() > self.det_thresh_byte:
                    """
                        NOTE: by using a lower threshold, e.g., self.iou_threshold - 0.1, you may
                        get a higher performance especially on MOT17/MOT20 datasets. But we keep it
                        uniform here for simplicity
                    """
                    matched_indices = linear_assignment(-iou_left)
                    # matched_indices = linear_assignment(-cost_matrix)
                    to_remove_trk_indices = []
                    to_remove_detsecond_indices = []
                    for m in matched_indices:
                        det_ind, trk_ind = m[0], unmatched_trks[m[1]]
                        matching_table.append([int(dets_second[det_ind][6]), trk_ind])

                        if iou_left[m[0], m[1]] < self.det_thresh_byte:
                            continue
                        
                        self.trackers[trk_ind].update(dets_second[det_ind, :], dets_second[det_ind, 5])

                        to_remove_trk_indices.append(trk_ind)
                        to_remove_detsecond_indices.append(det_ind)
                        
                    unmatched_dets_second = np.setdiff1d(unmatched_dets_second, np.array(to_remove_detsecond_indices))
                    unmatched_trks = np.setdiff1d(unmatched_trks, np.array(to_remove_trk_indices))

            if unmatched_dets.shape[0] > 0 and unmatched_trks.shape[0] > 0:
                left_dets = dets_high[unmatched_dets]
                left_trks = last_boxes[unmatched_trks]
                # left_trks = trks[unmatched_trks]
                iou_left = self.asso_func(left_dets, left_trks)
                iou_left = np.array(iou_left)
                if iou_left.max() > self.iou_threshold:  
                    """
                        NOTE: by using a lower threshold, e.g., self.iou_threshold - 0.1, you may
                        get a higher performance especially on MOT17/MOT20 datasets. But we keep it
                        uniform here for simplicity
                    """
                    rematched_indices = linear_assignment(-iou_left)
                    to_remove_det_indices = []
                    to_remove_trk_indices = []
                    for m in rematched_indices:
                        det_ind, trk_ind = unmatched_dets[m[0]], unmatched_trks[m[1]]
                        matching_table.append([int(dets_high[det_ind][6]), trk_ind])

                        if iou_left[m[0], m[1]] < self.iou_threshold:
                            continue

                        self.trackers[trk_ind].update(dets_high[det_ind, :], dets_high[det_ind, 5])

                        
                        to_remove_det_indices.append(det_ind)
                        to_remove_trk_indices.append(trk_ind)
                    
                    unmatched_dets = np.setdiff1d(unmatched_dets, np.array(to_remove_det_indices))
                    unmatched_trks = np.setdiff1d(unmatched_trks, np.array(to_remove_trk_indices))

        for m in unmatched_trks:
            self.trackers[m].update(None, None)
            self.trackers[m].mark_missed() #檢查是否遺失太久
            
        # create and initialise new trackers for unmatched detections
        for i in unmatched_dets:
            trk = KalmanBoxTracker(dets_high[i, :], self.max_age , self.min_hits, dets_high[i, 5], delta_t=self.delta_t, use_feature = self.use_feature, image_size = (self.width, self.height), id = self.count, dir_history_num=self.dir_history_num)
            self.count += 1
            self.trackers.append(trk)
            self.update_lst['new_ids'].append(trk.id)

        if self.use_byte: #針對use_byte, 還需對中分框裡匹配到的新det進行initial
            for i in unmatched_dets_second:
                trk = KalmanBoxTracker(dets_second[i, :], self.max_age , self.min_hits, dets_second[i, 5], delta_t=self.delta_t, use_feature = self.use_feature, image_size = (self.width, self.height), id = self.count, dir_history_num=self.dir_history_num)
                self.count += 1
                self.trackers.append(trk)
                self.update_lst['new_ids'].append(trk.id)
                
        if len(matching_table) != 0:
            for det_index,track_index in matching_table:
                trk = self.trackers[track_index]
                if trk.is_confirmed():
                    track_results[det_index] = trk.id

                    last_time = trk.time
                    cur_time = time.time()
                    speed, direction = get_speed_direction(last_time,
                                                           cur_time,
                                                           pre_box=trk.history_observations[-2][:4],
                                                           pre_n_box=trk.history_observations[0][:4],
                                                           cur_box=dets[det_index, :4],
                                                           pos_lambda=self.pos_lambda,
                                                           direction_type=self.direction_type)

                    trk.time = cur_time
                    trk.speed = speed
                    trk.direction = direction
                    speed_results[det_index] = trk.speed
                    direction_results[det_index] = trk.direction

        delete_list=[]
        for i, trk in enumerate(self.trackers):
            if trk.last_observation.sum() < 0:                
                d = trk.get_state()[0]
            else:
                """
                    this is optional to use the recent observation or the kalman filter prediction,
                    we didn't notice significant difference here
                """
                d = trk.last_observation[:4] #前一幀的結果x

            if self.use_feature:
                b_features.append(np.concatenate((d, [trk.id+1], [trk.cls], [trk.conf], trk.feature)).reshape(1, -1))
            # remove dead tracklet
            if trk.is_deleted():
                delete_list.append(i)
                self.update_lst['disappeared_ids'].append(trk.id)

        for i in reversed(delete_list):
            self.trackers.pop(i)
            
        # partial_fit用以記錄當前box_id的特徵
        if len(b_features) > 0:
            if self.use_feature :
                box = np.concatenate(b_features)
                b_features = box[:, 7:] 
                b_id = box[:,4]
                b_conf = box[:,6]
                #最後把這次配對到的ID的特徵更新
                if self.device == 'cuda':
                    self.partial_fit(np.asarray(b_features), np.asarray(b_id), np.asarray(b_conf))
                else:
                    self.partial_fit(np.asarray(b_features), np.asarray(b_id), np.asarray(b_conf))

        tracking_results = {
            'track_ids': track_results,
            'speed_results': speed_results,
            'direction_results': direction_results,
            'feature_results': features if self.use_feature else None
        }

        return tracking_results
