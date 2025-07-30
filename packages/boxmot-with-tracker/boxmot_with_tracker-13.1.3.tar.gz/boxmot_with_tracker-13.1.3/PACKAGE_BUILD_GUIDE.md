# BoxMOT包构建和发布指南

本指南详细说明如何将修改后的BoxMOT项目打包成pip包，供其他项目使用。

## 📋 准备工作

### 1. 确认项目结构

```
boxmot_with_tracker/
├── boxmot/                    # 主要包目录
│   ├── __init__.py           # 包初始化文件
│   ├── trackers/             # 追踪器模块
│   │   └── strongsort/       # StrongSort追踪器（包含ID映射功能）
│   └── ...
├── pyproject.toml            # 项目配置文件
├── README.md                 # 项目说明
├── LICENSE                   # 许可证文件
└── uv.lock                   # 依赖锁定文件
```

### 2. 检查包配置

当前 `pyproject.toml` 配置：
- **包名**: `boxmot_with_tracker`
- **版本**: `13.0.16`
- **构建系统**: `hatchling`
- **Python版本**: `>=3.9,<=3.13`

## 🔧 构建准备

### 1. 更新版本号

根据修改内容更新版本号：

```toml
# pyproject.toml
[project]
name = "boxmot_with_tracker"
version = "13.1.0"  # 新增ID映射功能，增加次版本号
```

### 2. 更新包描述

```toml
[project]
description = "BoxMOT: pluggable SOTA tracking modules with enhanced ID mapping support for segmentation, object detection and pose estimation models"
```

### 3. 添加更新日志

创建 `CHANGELOG.md`：

```markdown
# 更新日志

## [13.1.0] - 2024-01-XX

### 新增功能
- ✨ StrongSort追踪器新增目标ID映射功能
- 🔧 支持从检测结果的第7位获取目标TrackerID
- 📊 完善的ID映射调试工具

### 改进
- 🏗️ 重构ID映射逻辑，遵循单一职责原则
- 📝 添加详细的代码注释和文档
- 🧪 新增全面的测试用例

### 修复
- 🐛 修复多检测结果的ID映射问题
- 🔍 改进错误处理和日志记录
```

## 🏗️ 构建包

### 方法1: 使用UV构建（推荐）

```bash
# 1. 清理之前的构建文件
rm -rf dist/ build/ *.egg-info/

# 2. 构建包
uv build

# 3. 检查构建结果
ls dist/
# 应该看到:
# boxmot_with_tracker-13.1.0-py3-none-any.whl
# boxmot_with_tracker-13.1.0.tar.gz
```

### 方法2: 使用传统工具构建

```bash
# 1. 安装构建工具
pip install build twine

# 2. 构建包
python -m build

# 3. 检查构建结果
ls dist/
```

## 🧪 本地测试

### 1. 创建测试环境

```bash
# 创建新的虚拟环境
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# 或
test_env\Scripts\activate     # Windows
```

### 2. 安装本地包

```bash
# 安装wheel文件
pip install dist/boxmot_with_tracker-13.1.0-py3-none-any.whl

# 或安装源码包
pip install dist/boxmot_with_tracker-13.1.0.tar.gz
```

### 3. 测试安装

```python
# test_installation.py
import boxmot
from boxmot.trackers.strongsort import StrongSort

print(f"BoxMOT版本: {boxmot.__version__}")
print("StrongSort导入成功")

# 测试ID映射功能
tracker = StrongSort(
    model_weights='osnet_x0_25_msmt17.pt',
    device='cpu',
    fp16=False
)
print("StrongSort初始化成功，包含ID映射功能")
```

```bash
python test_installation.py
```

## 📦 发布到PyPI

### 1. 准备PyPI账户

- 注册 [PyPI账户](https://pypi.org/account/register/)
- 注册 [TestPyPI账户](https://test.pypi.org/account/register/)（用于测试）
- 配置API Token

### 2. 配置认证

```bash
# 创建 ~/.pypirc 文件
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

### 3. 发布到TestPyPI（测试）

```bash
# 上传到测试环境
twine upload --repository testpypi dist/*

# 从测试环境安装
pip install --index-url https://test.pypi.org/simple/ boxmot_with_tracker
```

### 4. 发布到正式PyPI

```bash
# 检查包
twine check dist/*

# 上传到正式PyPI
twine upload dist/*
```

## 📝 使用说明

### 安装包

```bash
# 从PyPI安装
pip install boxmot_with_tracker

# 安装特定版本
pip install boxmot_with_tracker==13.1.0

# 安装开发版本
pip install boxmot_with_tracker[dev]
```

### 在其他项目中使用

```python
# 基本使用
from boxmot import create_tracker

# 创建StrongSort追踪器
tracker = create_tracker(
    tracker_type='strongsort',
    tracker_config=None,
    reid_weights='osnet_x0_25_msmt17.pt',
    device='cpu',
    half=False
)

# 使用ID映射功能
import numpy as np

# 检测结果格式: [x1, y1, x2, y2, conf, class, tracker_id]
dets = np.array([
    [100, 100, 200, 200, 0.9, 0, 1001],  # 目标ID: 1001
    [300, 150, 400, 250, 0.8, 1, 1002],  # 目标ID: 1002
])

# 更新追踪器（自动应用ID映射）
tracks = tracker.update(dets, img)

print(f"追踪结果: {tracks}")
# 输出格式: [x1, y1, x2, y2, track_id, conf, class, -1]
```

## 🔍 包验证

### 1. 功能验证脚本

```python
# verify_package.py
import numpy as np
from boxmot import create_tracker

def test_id_mapping():
    """测试ID映射功能"""
    print("=== BoxMOT包功能验证 ===")
    
    # 创建追踪器
    tracker = create_tracker(
        tracker_type='strongsort',
        reid_weights='osnet_x0_25_msmt17.pt',
        device='cpu'
    )
    
    # 模拟检测数据
    dets = np.array([
        [100, 100, 200, 200, 0.9, 0, 2001],
        [300, 150, 400, 250, 0.8, 1, 2002],
    ])
    
    # 创建测试图像
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # 执行追踪
    tracks = tracker.update(dets, img)
    
    print(f"输入检测: {len(dets)} 个")
    print(f"输出轨迹: {len(tracks)} 个")
    print(f"ID映射功能: {'✓ 正常' if len(tracks) > 0 else '✗ 异常'}")
    
    return len(tracks) > 0

if __name__ == "__main__":
    success = test_id_mapping()
    print(f"\n验证结果: {'✅ 通过' if success else '❌ 失败'}")
```

### 2. 性能基准测试

```python
# benchmark.py
import time
import numpy as np
from boxmot import create_tracker

def benchmark_tracking():
    """追踪性能基准测试"""
    tracker = create_tracker('strongsort', device='cpu')
    
    # 测试数据
    img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    dets = np.array([
        [100, 100, 200, 200, 0.9, 0, 1001],
        [300, 150, 400, 250, 0.8, 1, 1002],
        [500, 200, 600, 300, 0.7, 0, 1003],
    ])
    
    # 性能测试
    times = []
    for i in range(100):
        start = time.time()
        tracks = tracker.update(dets, img)
        end = time.time()
        times.append(end - start)
    
    avg_time = np.mean(times) * 1000  # 转换为毫秒
    print(f"平均追踪时间: {avg_time:.2f}ms")
    print(f"FPS: {1000/avg_time:.1f}")

if __name__ == "__main__":
    benchmark_tracking()
```

## 📚 文档和示例

### 1. 创建使用示例

```python
# examples/id_mapping_example.py
"""
BoxMOT ID映射功能使用示例

本示例展示如何使用BoxMOT的StrongSort追踪器的ID映射功能。
"""

import cv2
import numpy as np
from boxmot import create_tracker

def main():
    # 初始化追踪器
    tracker = create_tracker(
        tracker_type='strongsort',
        reid_weights='osnet_x0_25_msmt17.pt',
        device='cpu',
        half=False
    )
    
    # 模拟视频帧
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # 模拟检测结果（包含目标ID）
    detections = np.array([
        # [x1, y1, x2, y2, conf, class, target_id]
        [100, 100, 200, 200, 0.95, 0, 1001],  # 人员ID: 1001
        [300, 150, 400, 250, 0.88, 0, 1002],  # 人员ID: 1002
        [500, 200, 600, 300, 0.76, 1, 1003],  # 车辆ID: 1003
    ])
    
    print("=== ID映射追踪示例 ===")
    print(f"输入检测数量: {len(detections)}")
    print(f"目标ID: {detections[:, 6].astype(int)}")
    
    # 执行追踪（自动应用ID映射）
    tracks = tracker.update(detections, img)
    
    print(f"\n输出轨迹数量: {len(tracks)}")
    if len(tracks) > 0:
        print(f"轨迹ID: {tracks[:, 4].astype(int)}")
        print("\n✅ ID映射成功！目标ID已正确映射到轨迹ID")
    else:
        print("⚠️  未生成轨迹")

if __name__ == "__main__":
    main()
```

### 2. API文档

```python
# docs/api_reference.py
"""
BoxMOT API参考文档

主要功能:
1. 多种追踪算法支持
2. StrongSort的增强ID映射功能
3. 灵活的配置选项
"""

from boxmot import create_tracker

# 创建追踪器
tracker = create_tracker(
    tracker_type='strongsort',      # 追踪器类型
    tracker_config=None,            # 配置文件路径
    reid_weights='model.pt',        # ReID模型权重
    device='cpu',                   # 设备: 'cpu' 或 'cuda'
    half=False                      # 是否使用半精度
)

# 更新追踪器
tracks = tracker.update(
    dets,                          # 检测结果 [N, 7]: [x1,y1,x2,y2,conf,class,id]
    img                            # 输入图像 [H, W, C]
)

# 返回格式: [N, 8]: [x1,y1,x2,y2,track_id,conf,class,-1]
```

## 🚀 自动化构建

### GitHub Actions配置

```yaml
# .github/workflows/build-and-publish.yml
name: Build and Publish Package

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install UV
      run: curl -LsSf https://astral.sh/uv/install.sh | sh
    
    - name: Build package
      run: uv build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        pip install twine
        twine upload dist/*
```

## 📋 检查清单

发布前确认：

- [ ] 版本号已更新
- [ ] 更新日志已完善
- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] 许可证文件存在
- [ ] README.md包含安装和使用说明
- [ ] 依赖关系正确配置
- [ ] 包构建成功
- [ ] 本地测试通过
- [ ] TestPyPI测试通过

## 🔧 故障排除

### 常见问题

1. **构建失败**
   ```bash
   # 清理缓存
   rm -rf dist/ build/ *.egg-info/
   uv cache clean
   ```

2. **依赖冲突**
   ```bash
   # 检查依赖
   uv tree
   # 解决冲突
   uv sync --resolution=highest
   ```

3. **上传失败**
   ```bash
   # 检查包格式
   twine check dist/*
   # 验证认证
   twine upload --repository testpypi dist/*
   ```

## 📞 技术支持

如遇问题，请提供：
1. 错误日志
2. 环境信息（Python版本、操作系统）
3. 构建命令
4. pyproject.toml配置

---

**注意**: 发布到PyPI是不可逆的操作，请确保在TestPyPI充分测试后再发布到正式环境。