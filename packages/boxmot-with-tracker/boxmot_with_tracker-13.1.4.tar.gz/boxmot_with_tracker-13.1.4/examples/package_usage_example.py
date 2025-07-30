#!/usr/bin/env python3
"""
BoxMOT包使用示例

本示例展示如何在其他项目中使用boxmot_with_tracker包，
特别是StrongSort追踪器的ID映射功能。

安装包:
    pip install boxmot_with_tracker

或从TestPyPI安装:
    pip install --index-url https://test.pypi.org/simple/ boxmot_with_tracker
"""

import cv2
import numpy as np
from typing import List, Tuple

# 导入BoxMOT
try:
    from boxmot import create_tracker
    print("✅ BoxMOT导入成功")
except ImportError as e:
    print(f"❌ BoxMOT导入失败: {e}")
    print("请先安装包: pip install boxmot_with_tracker")
    exit(1)


class VideoTracker:
    """视频追踪器类
    
    封装BoxMOT追踪器，提供简单易用的接口。
    """
    
    def __init__(self, 
                 tracker_type: str = 'strongsort',
                 reid_weights: str = None,
                 device: str = 'cpu',
                 half: bool = False):
        """初始化追踪器
        
        Args:
            tracker_type: 追踪器类型
            reid_weights: ReID模型权重文件
            device: 计算设备 ('cpu' 或 'cuda')
            half: 是否使用半精度
        """
        # 使用默认配置创建追踪器
        from boxmot.trackers.strongsort.strongsort import StrongSort
        self.tracker = StrongSort(
            reid_weights=reid_weights,
            device=device,
            half=half
        )
        print(f"🎯 追踪器初始化成功: {tracker_type}")
    
    def track_frame(self, 
                   frame: np.ndarray, 
                   detections: np.ndarray) -> np.ndarray:
        """追踪单帧
        
        Args:
            frame: 输入图像 [H, W, C]
            detections: 检测结果 [N, 7] - [x1,y1,x2,y2,conf,class,target_id]
            
        Returns:
            np.ndarray: 追踪结果 [N, 8] - [x1,y1,x2,y2,track_id,conf,class,-1]
        """
        return self.tracker.update(detections, frame)
    
    def reset(self):
        """重置追踪器"""
        # 重新创建追踪器实例
        from boxmot.trackers.strongsort.strongsort import StrongSort
        self.tracker = StrongSort(
            reid_weights=None,
            device='cpu',
            half=False
        )


def create_sample_detections(frame_idx: int) -> np.ndarray:
    """创建示例检测数据
    
    模拟目标检测器的输出，包含目标ID信息。
    
    Args:
        frame_idx: 帧索引
        
    Returns:
        np.ndarray: 检测结果 [N, 7]
    """
    # 模拟移动的目标
    base_x = 100 + frame_idx * 5  # 水平移动
    base_y = 150 + int(10 * np.sin(frame_idx * 0.1))  # 垂直振荡
    
    detections = np.array([
        # [x1, y1, x2, y2, conf, class, target_id]
        [base_x, base_y, base_x + 80, base_y + 120, 0.95, 0, 1001],  # 人员1
        [base_x + 200, base_y + 50, base_x + 280, base_y + 170, 0.88, 0, 1002],  # 人员2
        [base_x + 400, base_y - 20, base_x + 520, base_y + 80, 0.76, 1, 2001],  # 车辆1
    ])
    
    return detections


def draw_tracks(frame: np.ndarray, 
               tracks: np.ndarray, 
               detections: np.ndarray = None) -> np.ndarray:
    """在图像上绘制追踪结果
    
    Args:
        frame: 输入图像
        tracks: 追踪结果
        detections: 原始检测结果（可选）
        
    Returns:
        np.ndarray: 绘制后的图像
    """
    result = frame.copy()
    
    # 定义颜色
    colors = {
        0: (0, 255, 0),    # 人员 - 绿色
        1: (255, 0, 0),    # 车辆 - 蓝色
    }
    
    # 绘制追踪结果
    for track in tracks:
        x1, y1, x2, y2, track_id, conf, cls, _ = track
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        track_id, cls = int(track_id), int(cls)
        
        # 获取颜色
        color = colors.get(cls, (128, 128, 128))
        
        # 绘制边界框
        cv2.rectangle(result, (x1, y1), (x2, y2), color, 2)
        
        # 绘制标签
        label = f"ID:{track_id} Cls:{cls} Conf:{conf:.2f}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        cv2.rectangle(result, (x1, y1 - label_size[1] - 10), 
                     (x1 + label_size[0], y1), color, -1)
        cv2.putText(result, label, (x1, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # 如果提供了检测结果，也绘制原始目标ID
    if detections is not None:
        for det in detections:
            x1, y1, x2, y2, conf, cls, target_id = det
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            target_id, cls = int(target_id), int(cls)
            
            # 在右上角绘制原始目标ID
            target_label = f"Target:{target_id}"
            cv2.putText(result, target_label, (x2 - 80, y1 + 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    
    return result


def demo_basic_tracking():
    """基础追踪演示"""
    print("\n=== 基础追踪演示 ===")
    
    # 创建追踪器
    tracker = VideoTracker()
    
    # 创建测试图像
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame.fill(50)  # 深灰色背景
    
    # 模拟多帧追踪
    for frame_idx in range(5):
        print(f"\n📹 处理第 {frame_idx + 1} 帧")
        
        # 生成检测数据
        detections = create_sample_detections(frame_idx)
        print(f"  检测数量: {len(detections)}")
        print(f"  目标ID: {detections[:, 6].astype(int)}")
        
        # 执行追踪
        tracks = tracker.track_frame(frame, detections)
        print(f"  追踪数量: {len(tracks)}")
        
        if len(tracks) > 0:
            track_ids = tracks[:, 4].astype(int)
            print(f"  轨迹ID: {track_ids}")
            
            # 检查ID映射效果
            target_ids = detections[:, 6].astype(int)
            mapped_count = sum(1 for tid in track_ids if tid in target_ids)
            print(f"  ID映射成功: {mapped_count}/{len(target_ids)}")
        else:
            print("  ⚠️  未生成轨迹")


def demo_id_mapping_analysis():
    """ID映射分析演示"""
    print("\n=== ID映射分析演示 ===")
    
    tracker = VideoTracker()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # 测试不同的ID映射场景
    test_cases = [
        {
            "name": "正常映射",
            "detections": np.array([
                [100, 100, 200, 200, 0.9, 0, 1001],
                [300, 150, 400, 250, 0.8, 0, 1002],
            ])
        },
        {
            "name": "包含无效ID",
            "detections": np.array([
                [100, 100, 200, 200, 0.9, 0, 1001],
                [300, 150, 400, 250, 0.8, 0, 0],     # 无效ID
                [500, 200, 600, 300, 0.7, 1, -1],    # 无效ID
            ])
        },
        {
            "name": "重复ID",
            "detections": np.array([
                [100, 100, 200, 200, 0.9, 0, 1001],
                [300, 150, 400, 250, 0.8, 0, 1001],  # 重复ID
            ])
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🧪 测试场景 {i+1}: {test_case['name']}")
        
        detections = test_case['detections']
        target_ids = detections[:, 6].astype(int)
        valid_target_ids = target_ids[target_ids > 0]
        
        print(f"  输入目标ID: {target_ids}")
        print(f"  有效目标ID: {valid_target_ids}")
        
        # 执行追踪
        tracks = tracker.track_frame(frame, detections)
        
        if len(tracks) > 0:
            track_ids = tracks[:, 4].astype(int)
            print(f"  输出轨迹ID: {track_ids}")
            
            # 分析映射效果
            successful_mappings = [tid for tid in track_ids if tid in valid_target_ids]
            print(f"  成功映射: {successful_mappings}")
            print(f"  映射率: {len(successful_mappings)}/{len(valid_target_ids)} = {len(successful_mappings)/len(valid_target_ids)*100:.1f}%" if len(valid_target_ids) > 0 else "  映射率: N/A")
        else:
            print("  ⚠️  未生成轨迹")
        
        # 重置追踪器以避免历史影响
        tracker.reset()


def demo_video_simulation():
    """视频追踪模拟演示"""
    print("\n=== 视频追踪模拟演示 ===")
    
    tracker = VideoTracker()
    
    # 模拟视频参数
    width, height = 640, 480
    num_frames = 10
    
    print(f"📹 模拟视频: {width}x{height}, {num_frames}帧")
    
    # 统计信息
    total_detections = 0
    total_tracks = 0
    successful_mappings = 0
    
    for frame_idx in range(num_frames):
        # 创建帧
        frame = np.random.randint(0, 50, (height, width, 3), dtype=np.uint8)
        
        # 生成检测
        detections = create_sample_detections(frame_idx)
        
        # 执行追踪
        tracks = tracker.track_frame(frame, detections)
        
        # 统计
        total_detections += len(detections)
        total_tracks += len(tracks)
        
        if len(tracks) > 0:
            target_ids = detections[:, 6].astype(int)
            track_ids = tracks[:, 4].astype(int)
            frame_mappings = sum(1 for tid in track_ids if tid in target_ids)
            successful_mappings += frame_mappings
            
            print(f"  帧 {frame_idx+1:2d}: 检测={len(detections)}, 轨迹={len(tracks)}, 映射={frame_mappings}")
        else:
            print(f"  帧 {frame_idx+1:2d}: 检测={len(detections)}, 轨迹=0, 映射=0")
    
    # 输出统计结果
    print(f"\n📊 统计结果:")
    print(f"  总检测数: {total_detections}")
    print(f"  总轨迹数: {total_tracks}")
    print(f"  成功映射: {successful_mappings}")
    print(f"  映射成功率: {successful_mappings/total_detections*100:.1f}%" if total_detections > 0 else "  映射成功率: N/A")


def demo_performance_test():
    """性能测试演示"""
    print("\n=== 性能测试演示 ===")
    
    import time
    
    tracker = VideoTracker()
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # 不同规模的检测数据
    test_sizes = [1, 5, 10, 20]
    
    for size in test_sizes:
        print(f"\n🚀 测试规模: {size} 个检测")
        
        # 生成测试数据
        detections = np.random.rand(size, 7)
        detections[:, :4] *= [600, 400, 600, 400]  # 坐标范围
        detections[:, 4] = np.random.uniform(0.5, 1.0, size)  # 置信度
        detections[:, 5] = np.random.randint(0, 2, size)  # 类别
        detections[:, 6] = np.arange(1001, 1001 + size)  # 目标ID
        
        # 性能测试
        times = []
        for _ in range(50):  # 运行50次取平均
            start_time = time.time()
            tracks = tracker.track_frame(frame, detections)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = np.mean(times) * 1000  # 转换为毫秒
        std_time = np.std(times) * 1000
        fps = 1000 / avg_time if avg_time > 0 else 0
        
        print(f"  平均耗时: {avg_time:.2f} ± {std_time:.2f} ms")
        print(f"  理论FPS: {fps:.1f}")
        print(f"  输出轨迹: {len(tracks) if 'tracks' in locals() else 0}")
        
        # 重置追踪器
        tracker.reset()


def main():
    """主函数"""
    print("🎯 BoxMOT包使用示例")
    print("=" * 50)
    
    try:
        # 运行各种演示
        demo_basic_tracking()
        demo_id_mapping_analysis()
        demo_video_simulation()
        demo_performance_test()
        
        print("\n" + "=" * 50)
        print("🎉 所有演示完成！")
        print("\n📚 更多信息:")
        print("  - 项目文档: README.md")
        print("  - 调试指南: ID_MAPPING_DEBUG_GUIDE.md")
        print("  - 构建指南: PACKAGE_BUILD_GUIDE.md")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()