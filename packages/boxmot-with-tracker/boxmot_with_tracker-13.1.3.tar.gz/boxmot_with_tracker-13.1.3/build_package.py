#!/usr/bin/env python3
"""
BoxMOT包构建脚本

这个脚本自动化了包的构建、测试和发布流程。

使用方法:
    python build_package.py --help
    python build_package.py build
    python build_package.py test
    python build_package.py publish --test
    python build_package.py publish --production
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class PackageBuilder:
    """包构建器类"""
    
    def __init__(self, project_root: Path):
        """初始化构建器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = project_root
        self.dist_dir = project_root / "dist"
        self.build_dir = project_root / "build"
        
    def clean(self) -> bool:
        """清理构建文件
        
        Returns:
            bool: 清理是否成功
        """
        print("🧹 清理构建文件...")
        
        # 要清理的目录和文件模式
        clean_targets = [
            self.dist_dir,
            self.build_dir,
            self.project_root / "*.egg-info",
            self.project_root / "__pycache__",
        ]
        
        try:
            for target in clean_targets:
                if target.exists():
                    if target.is_dir():
                        shutil.rmtree(target)
                        print(f"  ✓ 删除目录: {target}")
                    else:
                        target.unlink()
                        print(f"  ✓ 删除文件: {target}")
                        
            # 清理Python缓存
            for cache_dir in self.project_root.rglob("__pycache__"):
                shutil.rmtree(cache_dir)
                print(f"  ✓ 删除缓存: {cache_dir}")
                
            print("✅ 清理完成")
            return True
            
        except Exception as e:
            print(f"❌ 清理失败: {e}")
            return False
    
    def build(self) -> bool:
        """构建包
        
        Returns:
            bool: 构建是否成功
        """
        print("🏗️  开始构建包...")
        
        try:
            # 首先清理
            if not self.clean():
                return False
            
            # 检查是否有uv
            if shutil.which("uv"):
                print("  使用UV构建...")
                result = subprocess.run(
                    ["uv", "build"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
            else:
                print("  使用传统工具构建...")
                # 确保安装了build工具
                subprocess.run([sys.executable, "-m", "pip", "install", "build"], check=True)
                result = subprocess.run(
                    [sys.executable, "-m", "build"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                print("✅ 构建成功")
                self._list_build_artifacts()
                return True
            else:
                print(f"❌ 构建失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 构建异常: {e}")
            return False
    
    def _list_build_artifacts(self) -> None:
        """列出构建产物"""
        if self.dist_dir.exists():
            print("\n📦 构建产物:")
            for file in self.dist_dir.iterdir():
                size = file.stat().st_size / 1024 / 1024  # MB
                print(f"  📄 {file.name} ({size:.2f} MB)")
    
    def test_installation(self) -> bool:
        """测试包安装
        
        Returns:
            bool: 测试是否成功
        """
        print("🧪 测试包安装...")
        
        if not self.dist_dir.exists() or not list(self.dist_dir.glob("*.whl")):
            print("❌ 未找到wheel文件，请先构建包")
            return False
        
        try:
            # 找到wheel文件
            wheel_file = next(self.dist_dir.glob("*.whl"))
            
            # 创建测试脚本
            test_script = self._create_test_script()
            
            # 在临时环境中测试
            print("  创建测试环境...")
            test_env = self.project_root / "test_env"
            
            # 创建虚拟环境
            subprocess.run([
                sys.executable, "-m", "venv", str(test_env)
            ], check=True)
            
            # 获取虚拟环境的Python路径
            if sys.platform == "win32":
                venv_python = test_env / "Scripts" / "python.exe"
                venv_pip = test_env / "Scripts" / "pip.exe"
            else:
                venv_python = test_env / "bin" / "python"
                venv_pip = test_env / "bin" / "pip"
            
            # 安装包
            print(f"  安装包: {wheel_file.name}")
            subprocess.run([
                str(venv_pip), "install", str(wheel_file)
            ], check=True)
            
            # 运行测试
            print("  运行功能测试...")
            result = subprocess.run([
                str(venv_python), "-c", test_script
            ], capture_output=True, text=True)
            
            # 清理测试环境
            shutil.rmtree(test_env)
            
            if result.returncode == 0:
                print("✅ 安装测试通过")
                print(f"  测试输出: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ 安装测试失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            # 清理测试环境
            test_env = self.project_root / "test_env"
            if test_env.exists():
                shutil.rmtree(test_env)
            return False
    
    def _create_test_script(self) -> str:
        """创建测试脚本
        
        Returns:
            str: 测试脚本代码
        """
        return """
import sys
try:
    # 测试基本导入
    import boxmot
    print(f"✓ BoxMOT导入成功")
    
    # 测试StrongSort导入
    from boxmot.trackers.strongsort import StrongSort
    print(f"✓ StrongSort导入成功")
    
    # 测试创建追踪器
    from boxmot import create_tracker
    print(f"✓ create_tracker导入成功")
    
    print("🎉 所有测试通过")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 测试失败: {e}")
    sys.exit(1)
"""
    
    def check_package(self) -> bool:
        """检查包完整性
        
        Returns:
            bool: 检查是否通过
        """
        print("🔍 检查包完整性...")
        
        if not self.dist_dir.exists():
            print("❌ dist目录不存在")
            return False
        
        try:
            # 检查是否有twine
            if not shutil.which("twine"):
                print("  安装twine...")
                subprocess.run([sys.executable, "-m", "pip", "install", "twine"], check=True)
            
            # 使用twine检查
            result = subprocess.run([
                "twine", "check", "dist/*"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 包检查通过")
                return True
            else:
                print(f"❌ 包检查失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 检查异常: {e}")
            return False
    
    def publish(self, repository: str = "testpypi") -> bool:
        """发布包
        
        Args:
            repository: 发布仓库 ('testpypi' 或 'pypi')
            
        Returns:
            bool: 发布是否成功
        """
        print(f"📤 发布包到 {repository}...")
        
        # 检查包
        if not self.check_package():
            return False
        
        try:
            # 构建twine命令
            cmd = ["twine", "upload"]
            
            if repository == "testpypi":
                cmd.extend(["--repository", "testpypi"])
                print("  ⚠️  发布到测试环境")
            elif repository == "pypi":
                print("  🚨 发布到生产环境")
                # 确认发布
                confirm = input("  确认发布到生产环境？(yes/no): ")
                if confirm.lower() != "yes":
                    print("  取消发布")
                    return False
            else:
                print(f"❌ 未知仓库: {repository}")
                return False
            
            cmd.append("dist/*")
            
            # 执行发布
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ 发布成功到 {repository}")
                if repository == "testpypi":
                    print("  测试安装: pip install --index-url https://test.pypi.org/simple/ boxmot_with_tracker")
                else:
                    print("  安装命令: pip install boxmot_with_tracker")
                return True
            else:
                print(f"❌ 发布失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 发布异常: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="BoxMOT包构建脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python build_package.py build          # 构建包
  python build_package.py test           # 测试安装
  python build_package.py check          # 检查包
  python build_package.py publish --test # 发布到测试环境
  python build_package.py publish --prod # 发布到生产环境
  python build_package.py all            # 执行完整流程
        """
    )
    
    parser.add_argument(
        "action",
        choices=["clean", "build", "test", "check", "publish", "all"],
        help="要执行的操作"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="发布到测试环境 (TestPyPI)"
    )
    
    parser.add_argument(
        "--prod",
        action="store_true",
        help="发布到生产环境 (PyPI)"
    )
    
    args = parser.parse_args()
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    builder = PackageBuilder(project_root)
    
    print(f"📁 项目目录: {project_root}")
    print(f"🎯 执行操作: {args.action}")
    print("=" * 50)
    
    success = True
    
    if args.action == "clean":
        success = builder.clean()
        
    elif args.action == "build":
        success = builder.build()
        
    elif args.action == "test":
        success = builder.test_installation()
        
    elif args.action == "check":
        success = builder.check_package()
        
    elif args.action == "publish":
        if args.test:
            success = builder.publish("testpypi")
        elif args.prod:
            success = builder.publish("pypi")
        else:
            print("❌ 请指定发布目标: --test 或 --prod")
            success = False
            
    elif args.action == "all":
        print("🚀 执行完整构建流程...\n")
        
        # 1. 构建
        success = builder.build()
        if not success:
            print("❌ 构建失败，停止流程")
            sys.exit(1)
        
        print("\n" + "=" * 50)
        
        # 2. 检查
        success = builder.check_package()
        if not success:
            print("❌ 包检查失败，停止流程")
            sys.exit(1)
        
        print("\n" + "=" * 50)
        
        # 3. 测试安装
        success = builder.test_installation()
        if not success:
            print("❌ 安装测试失败，停止流程")
            sys.exit(1)
        
        print("\n" + "=" * 50)
        print("🎉 完整流程执行成功！")
        print("\n📋 下一步:")
        print("  1. 发布到测试环境: python build_package.py publish --test")
        print("  2. 发布到生产环境: python build_package.py publish --prod")
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 操作完成")
        sys.exit(0)
    else:
        print("❌ 操作失败")
        sys.exit(1)


if __name__ == "__main__":
    main()