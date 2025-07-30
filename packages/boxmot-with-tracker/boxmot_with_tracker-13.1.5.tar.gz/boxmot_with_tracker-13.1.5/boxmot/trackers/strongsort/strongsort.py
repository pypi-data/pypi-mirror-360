# Mikel Broström 🔥 Yolo Tracking 🧾 AGPL-3.0 license

from pathlib import Path

import numpy as np
from torch import device

from boxmot.appearance.reid.auto_backend import ReidAutoBackend
from boxmot.motion.cmc import get_cmc_method
from boxmot.trackers.basetracker import BaseTracker
from boxmot.trackers.strongsort.sort.detection import Detection
from boxmot.trackers.strongsort.sort.tracker import Tracker
from boxmot.utils.matching import NearestNeighborDistanceMetric
from boxmot.utils.ops import xyxy2tlwh


class StrongSort(object):
    """
    StrongSORT Tracker: A tracking algorithm that utilizes a combination of appearance and motion-based tracking.

    Args:
        model_weights (str): Path to the model weights for ReID (Re-Identification).
        device (str): Device on which to run the model (e.g., 'cpu' or 'cuda').
        fp16 (bool): Whether to use half-precision (fp16) for faster inference on compatible devices.
        per_class (bool, optional): Whether to perform per-class tracking. If True, tracks are maintained separately for each object class.
        max_dist (float, optional): Maximum cosine distance for ReID feature matching in Nearest Neighbor Distance Metric.
        max_iou_dist (float, optional): Maximum Intersection over Union (IoU) distance for data association. Controls the maximum allowed distance between tracklets and detections for a match.
        max_age (int, optional): Maximum number of frames to keep a track alive without any detections.
        n_init (int, optional): Number of consecutive frames required to confirm a track.
        nn_budget (int, optional): Maximum size of the feature library for Nearest Neighbor Distance Metric. If the library size exceeds this value, the oldest features are removed.
        mc_lambda (float, optional): Weight for motion consistency in the track state estimation. Higher values give more weight to motion information.
        ema_alpha (float, optional): Alpha value for exponential moving average (EMA) update of appearance features. Controls the contribution of new and old embeddings in the ReID model.
    """

    def __init__(
        self,
        reid_weights: Path,
        device: device,
        half: bool,
        per_class: bool = False,
        min_conf: float = 0.1,
        max_cos_dist=0.2,
        max_iou_dist=0.7,
        max_age=30,
        n_init=3,
        nn_budget=100,
        mc_lambda=0.98,
        ema_alpha=0.9,
    ):

        self.per_class = per_class
        self.min_conf = min_conf
        self.model = ReidAutoBackend(
            weights=reid_weights, device=device, half=half
        ).model

        self.tracker = Tracker(
            metric=NearestNeighborDistanceMetric("cosine", max_cos_dist, nn_budget),
            max_iou_dist=max_iou_dist,
            max_age=max_age,
            n_init=n_init,
            mc_lambda=mc_lambda,
            ema_alpha=ema_alpha,
        )
        self.cmc = get_cmc_method("ecc")()

    def _apply_target_id_mapping(self, target_tracker_id: np.ndarray, detections: list) -> None:
        """
        应用目标ID映射逻辑，将检测到的目标ID映射到对应的轨迹上
        
        Args:
            target_tracker_id (np.ndarray): 检测结果中的目标tracker ID数组，形状为(N,)
            detections (list): 检测对象列表，与target_tracker_id一一对应
            
        Note:
            - 建立检测与轨迹之间的一对一映射关系
            - 只对确认且最近更新的轨迹进行ID映射
            - 遵循单一职责原则，专门处理ID映射逻辑
            - 包含异常处理，确保跟踪系统的稳定性
        """
        if not self._has_valid_target_ids(target_tracker_id):
            return
            
        try:
            # 创建检测索引到目标ID的映射
            detection_id_mapping = self._create_detection_id_mapping(target_tracker_id, detections)
            
            # 根据轨迹关联的检测更新轨迹ID
            self._update_tracks_with_detection_mapping(detection_id_mapping)
            
        except Exception as e:
            print(f"目标ID映射过程中发生错误: {e}")
            # 异常情况下继续使用原有跟踪逻辑，不影响系统稳定性
    
    def _has_valid_target_ids(self, target_tracker_id: np.ndarray) -> bool:
        """
        验证目标tracker ID数组是否包含有效数据
        
        Args:
            target_tracker_id (np.ndarray): 目标tracker ID数组
            
        Returns:
            bool: 如果包含有效目标ID返回True，否则返回False
        """
        return (
            len(target_tracker_id) > 0 and 
            np.any(target_tracker_id > 0)  # 至少有一个有效的目标ID
        )

    def _create_detection_id_mapping(self, target_tracker_id: np.ndarray, detections: list) -> dict:
        """
        创建检测索引到目标ID的映射字典
        
        Args:
            target_tracker_id (np.ndarray): 目标tracker ID数组
            detections (list): 检测对象列表
            
        Returns:
            dict: 检测索引到目标ID的映射，格式为 {det_ind: target_id}
        """
        detection_id_mapping = {}

        for i, (detection, target_id) in enumerate(zip(detections, target_tracker_id)):
            if target_id > 0:  # 只处理有效的目标ID
                det_ind = detection.det_ind  # 获取检测索引
                detection_id_mapping[det_ind] = int(target_id)
                print(f"添加映射-> target_id:{target_id},det_ind :{detection.det_ind}")
                
        return detection_id_mapping
    
    def _update_tracks_with_detection_mapping(self, detection_id_mapping: dict) -> None:
        """
        根据检测映射更新轨迹ID
        
        Args:
            detection_id_mapping (dict): 检测索引到目标ID的映射
            
        Note:
            - 只更新已确认且最近更新的轨迹
            - 通过轨迹的det_ind属性找到对应的目标ID
            - 记录ID更新过程用于调试
            轨迹ID更新: 1 -> 1 (检测索引: 0.0)
            轨迹ID更新: 1 -> 1 (检测索引: 1.0)
        """
        for track in self.tracker.tracks:
            if self._should_update_track_id(track):
                # 通过轨迹关联的检测索引查找对应的目标ID
                if hasattr(track, 'det_ind') and track.det_ind in detection_id_mapping:
                    original_id = track.id  # 保存原始ID用于调试
                    target_id = detection_id_mapping[track.det_ind]  # 获取对应的目标ID
                    track.id = target_id    # 更新轨迹ID
                    print(f"轨迹ID更新: {original_id} -> {target_id} (检测索引: {track.det_ind}) -> detection_id_mapping:{detection_id_mapping}")
    
    def _should_update_track_id(self, track) -> bool:
        """
        判断是否应该更新轨迹的ID
        
        Args:
            track: 轨迹对象
            
        Returns:
            bool: 如果应该更新返回True，否则返回False
            
        Note:
            - 只有确认的轨迹才会被更新
        """
        return track.is_confirmed()

    @BaseTracker.per_class_decorator
    def update(self, dets: np.ndarray, img: np.ndarray, embs: np.ndarray = None) -> np.ndarray:
        print(f"------ dets: {dets}")

        assert isinstance(
            dets, np.ndarray
        ), f"Unsupported 'dets' input format '{type(dets)}', valid format is np.ndarray"
        assert isinstance(
            img, np.ndarray
        ), f"Unsupported 'img' input format '{type(img)}', valid format is np.ndarray"
        assert (
            len(dets.shape) == 2
        ), "Unsupported 'dets' dimensions, valid number of dimensions is two"
        assert (
            dets.shape[1] == 8
        ), "Unsupported 'dets' 2nd dimension lenght, valid lenghts is 8"

        dets = np.hstack([dets, np.arange(len(dets)).reshape(-1, 1)])
        remain_inds = dets[:, 4] >= self.min_conf
        dets = dets[remain_inds]

        xyxy = dets[:, 0:4]
        confs = dets[:, 4]
        clss = dets[:, 5]
        target_tracker_id = dets[:, 6] # 新增：目标trackerID
        det_ind = dets[:, 7]

        if len(self.tracker.tracks) >= 1:
            warp_matrix = self.cmc.apply(img, xyxy)
            for track in self.tracker.tracks:
                track.camera_update(warp_matrix)

        # extract appearance information for each detection
        if embs is not None:
            features = embs[remain_inds]
        else:
            features = self.model.get_features(xyxy, img)

        tlwh = xyxy2tlwh(xyxy)
        detections = [
            Detection(box, conf, cls, det_ind, feat)
            for box, conf, cls, det_ind, feat in zip(
                tlwh, confs, clss, det_ind, features
            )
        ]
        # 打印detections的详细信息
        print(f"---- 即将进行 update 的 detections ({len(detections)}个):")
        for i, det in enumerate(detections):
            print(f"  Detection[{i}]: tlwh={det.tlwh}, conf={det.conf:.3f}, cls={det.cls}, det_ind={det.det_ind}, feat_shape={det.feat.shape if det.feat is not None else None}")
        
        # 打印tracks的详细信息
        print(f"---- before update tracks len: {len(self.tracker.tracks)}; tracks详情:")
        for i, track in enumerate(self.tracker.tracks):
            bbox = track.to_tlbr()
            state_name = {1: 'Tentative', 2: 'Confirmed', 3: 'Deleted'}.get(track.state, 'Unknown')
            print(f"  Track[{i}]: id={track.id}, bbox=[{bbox[0]:.1f},{bbox[1]:.1f},{bbox[2]:.1f},{bbox[3]:.1f}], conf={track.conf:.3f}, cls={track.cls}, det_ind={track.det_ind}, state={state_name}, time_since_update={track.time_since_update}, hits={track.hits}")

        # update tracker
        self.tracker.predict()
        self.tracker.update(detections)
        # 打印update后tracks的详细信息
        print(f"---- after update tracks len: {len(self.tracker.tracks)}; tracks详情:")
        for i, track in enumerate(self.tracker.tracks):
            bbox = track.to_tlbr()
            state_name = {1: 'Tentative', 2: 'Confirmed', 3: 'Deleted'}.get(track.state, 'Unknown')
            print(f"  Track[{i}]: id={track.id}, bbox=[{bbox[0]:.1f},{bbox[1]:.1f},{bbox[2]:.1f},{bbox[3]:.1f}], conf={track.conf:.3f}, cls={track.cls}, det_ind={track.det_ind}, state={state_name}, time_since_update={track.time_since_update}, hits={track.hits}")

        # 应用目标ID映射逻辑
        self._apply_target_id_mapping(target_tracker_id, detections)

        # output bbox identities
        outputs = []
        for track in self.tracker.tracks:
            if not track.is_confirmed() or track.time_since_update >= 1:
                print(f"------ skip this track, biz track {track.is_confirmed()} is not confirmed or track time_since_update {track.time_since_update} < 1")
                continue

            x1, y1, x2, y2 = track.to_tlbr()

            id = track.id
            conf = track.conf
            cls = track.cls
            det_ind = track.det_ind

            outputs.append(
                np.array([*track.to_tlbr(), id, conf, cls, det_ind]).reshape(1, -1)
            )
        if len(outputs) > 0:
            print(f"------ outputs: {outputs}")
            return np.concatenate(outputs)
        return np.array([])
