#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的ID映射测试脚本

不依赖复杂模型，专注测试ID映射逻辑
"""

import numpy as np
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))


class MockTrack:
    """
    模拟轨迹对象，用于测试
    """
    def __init__(self, track_id, det_ind, confirmed=True, time_since_update=0):
        self.id = track_id
        self.det_ind = det_ind
        self._confirmed = confirmed
        self.time_since_update = time_since_update
    
    def is_confirmed(self):
        return self._confirmed


class MockDetection:
    """
    模拟检测对象，用于测试
    """
    def __init__(self, det_ind):
        self.det_ind = det_ind


class IDMappingTester:
    """
    ID映射功能测试器
    
    专门测试StrongSort中的ID映射逻辑，不依赖完整的追踪器
    """
    
    def __init__(self):
        self.tracks = []  # 模拟轨迹列表
    
    def _has_valid_target_ids(self, target_tracker_id: np.ndarray) -> bool:
        """
        验证目标tracker ID数组是否包含有效数据
        （复制StrongSort中的方法用于测试）
        """
        return (
            len(target_tracker_id) > 0 and 
            np.any(target_tracker_id > 0)  # 至少有一个有效的目标ID
        )
    
    def _create_detection_id_mapping(self, target_tracker_id: np.ndarray, detections: list) -> dict:
        """
        创建检测索引到目标ID的映射字典
        （复制StrongSort中的方法用于测试）
        """
        detection_id_mapping = {}
        
        for i, (detection, target_id) in enumerate(zip(detections, target_tracker_id)):
            if target_id > 0:  # 只处理有效的目标ID
                det_ind = detection.det_ind  # 获取检测索引
                detection_id_mapping[det_ind] = int(target_id)
                
        return detection_id_mapping
    
    def _should_update_track_id(self, track) -> bool:
        """
        判断是否应该更新轨迹的ID
        （复制StrongSort中的方法用于测试）
        """
        return track.is_confirmed() and track.time_since_update < 1
    
    def _update_tracks_with_detection_mapping(self, detection_id_mapping: dict) -> None:
        """
        根据检测映射更新轨迹ID
        （复制StrongSort中的方法用于测试）
        """
        for track in self.tracks:
            if self._should_update_track_id(track):
                # 通过轨迹关联的检测索引查找对应的目标ID
                if hasattr(track, 'det_ind') and track.det_ind in detection_id_mapping:
                    original_id = track.id  # 保存原始ID用于调试
                    target_id = detection_id_mapping[track.det_ind]  # 获取对应的目标ID
                    track.id = target_id    # 更新轨迹ID
                    print(f"轨迹ID更新: {original_id} -> {target_id} (检测索引: {track.det_ind})")
    
    def _apply_target_id_mapping(self, target_tracker_id: np.ndarray, detections: list) -> None:
        """
        应用目标ID映射逻辑
        （复制StrongSort中的方法用于测试）
        """
        if not self._has_valid_target_ids(target_tracker_id):
            print("⚠️  无有效目标ID，跳过映射")
            return
            
        try:
            # 创建检测索引到目标ID的映射
            detection_id_mapping = self._create_detection_id_mapping(target_tracker_id, detections)
            print(f"检测ID映射: {detection_id_mapping}")
            
            # 根据轨迹关联的检测更新轨迹ID
            self._update_tracks_with_detection_mapping(detection_id_mapping)
            
        except Exception as e:
            print(f"目标ID映射过程中发生错误: {e}")
    
    def setup_test_scenario(self, scenario="basic"):
        """
        设置测试场景
        
        Args:
            scenario (str): 测试场景类型
        """
        self.tracks = []  # 清空轨迹
        
        if scenario == "basic":
            # 基础场景：3个轨迹，对应3个检测
            self.tracks = [
                MockTrack(track_id=1, det_ind=0, confirmed=True, time_since_update=0),
                MockTrack(track_id=2, det_ind=1, confirmed=True, time_since_update=0),
                MockTrack(track_id=3, det_ind=2, confirmed=True, time_since_update=0),
            ]
            print("设置基础测试场景: 3个确认轨迹")
            
        elif scenario == "partial":
            # 部分场景：有些轨迹未确认或更新时间过长
            self.tracks = [
                MockTrack(track_id=1, det_ind=0, confirmed=True, time_since_update=0),   # 会更新
                MockTrack(track_id=2, det_ind=1, confirmed=False, time_since_update=0),  # 不会更新（未确认）
                MockTrack(track_id=3, det_ind=2, confirmed=True, time_since_update=2),   # 不会更新（时间过长）
                MockTrack(track_id=4, det_ind=3, confirmed=True, time_since_update=0),   # 会更新
            ]
            print("设置部分更新场景: 4个轨迹，只有2个会被更新")
            
        elif scenario == "mismatch":
            # 不匹配场景：轨迹的检测索引与实际检测不对应
            self.tracks = [
                MockTrack(track_id=1, det_ind=5, confirmed=True, time_since_update=0),  # 检测索引5不存在
                MockTrack(track_id=2, det_ind=1, confirmed=True, time_since_update=0),  # 正常
            ]
            print("设置不匹配场景: 部分轨迹的检测索引不存在")
    
    def create_test_data(self, scenario="basic"):
        """
        创建测试数据
        
        Args:
            scenario (str): 测试场景
            
        Returns:
            tuple: (target_tracker_id, detections)
        """
        if scenario == "basic":
            # 基础数据：3个检测，都有有效目标ID
            target_tracker_id = np.array([1001, 1002, 1003])
            detections = [
                MockDetection(det_ind=0),
                MockDetection(det_ind=1),
                MockDetection(det_ind=2),
            ]
            print(f"创建基础测试数据: 目标ID={target_tracker_id}")
            
        elif scenario == "partial":
            # 部分有效数据：4个检测，部分有有效目标ID
            target_tracker_id = np.array([1001, 0, 1003, 1004])  # 第2个无效
            detections = [
                MockDetection(det_ind=0),
                MockDetection(det_ind=1),
                MockDetection(det_ind=2),
                MockDetection(det_ind=3),
            ]
            print(f"创建部分有效数据: 目标ID={target_tracker_id}")
            
        elif scenario == "mismatch":
            # 不匹配数据：检测数量与轨迹不完全对应
            target_tracker_id = np.array([1001, 1002])
            detections = [
                MockDetection(det_ind=0),
                MockDetection(det_ind=1),
            ]
            print(f"创建不匹配数据: 目标ID={target_tracker_id}")
            
        elif scenario == "no_valid":
            # 无有效ID数据
            target_tracker_id = np.array([0, -1, 0])
            detections = [
                MockDetection(det_ind=0),
                MockDetection(det_ind=1),
                MockDetection(det_ind=2),
            ]
            print(f"创建无有效ID数据: 目标ID={target_tracker_id}")
            
        return target_tracker_id, detections
    
    def print_tracks_status(self, title="轨迹状态"):
        """
        打印当前轨迹状态
        """
        print(f"\n{title}:")
        for i, track in enumerate(self.tracks):
            status = "确认" if track.is_confirmed() else "未确认"
            update_status = "最新" if track.time_since_update < 1 else f"过时({track.time_since_update})" 
            print(f"  轨迹{i+1}: ID={track.id}, 检测索引={track.det_ind}, {status}, {update_status}")
    
    def run_test(self, scenario="basic"):
        """
        运行单个测试场景
        
        Args:
            scenario (str): 测试场景名称
        """
        print(f"\n{'='*50}")
        print(f"测试场景: {scenario}")
        print(f"{'='*50}")
        
        # 设置场景
        self.setup_test_scenario(scenario)
        target_tracker_id, detections = self.create_test_data(scenario)
        
        # 打印初始状态
        self.print_tracks_status("初始轨迹状态")
        
        # 执行ID映射
        print("\n执行ID映射...")
        self._apply_target_id_mapping(target_tracker_id, detections)
        
        # 打印最终状态
        self.print_tracks_status("映射后轨迹状态")
        
        # 分析结果
        self.analyze_mapping_result(target_tracker_id, scenario)
    
    def analyze_mapping_result(self, target_tracker_id, scenario):
        """
        分析映射结果
        
        Args:
            target_tracker_id (np.ndarray): 目标ID数组
            scenario (str): 测试场景
        """
        print("\n结果分析:")
        
        valid_target_ids = target_tracker_id[target_tracker_id > 0]
        current_track_ids = [track.id for track in self.tracks]
        
        print(f"有效目标ID: {valid_target_ids}")
        print(f"当前轨迹ID: {current_track_ids}")
        
        # 检查映射是否成功
        mapped_ids = [tid for tid in current_track_ids if tid in valid_target_ids]
        if len(mapped_ids) > 0:
            print(f"✓ 成功映射的ID: {mapped_ids}")
        else:
            print("⚠️  没有ID被成功映射")
    
    def run_all_tests(self):
        """
        运行所有测试场景
        """
        print("StrongSort ID映射功能简化测试")
        print("测试目标: 验证ID映射逻辑的正确性\n")
        
        test_scenarios = [
            "basic",      # 基础场景
            "partial",    # 部分更新场景
            "mismatch",   # 不匹配场景
            "no_valid",   # 无有效ID场景
        ]
        
        for scenario in test_scenarios:
            try:
                self.run_test(scenario)
            except Exception as e:
                print(f"✗ 场景 {scenario} 测试失败: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*50}")
        print("所有测试完成")
        print(f"{'='*50}")
        
        print("\n测试总结:")
        print("1. basic场景应该成功映射所有ID")
        print("2. partial场景应该只映射部分ID（根据轨迹状态）")
        print("3. mismatch场景应该只映射匹配的检测索引")
        print("4. no_valid场景应该跳过映射（无有效目标ID）")


def main():
    """
    主函数
    """
    tester = IDMappingTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()