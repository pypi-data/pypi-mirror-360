#!/usr/bin/env python3
"""
发布脚本 - 用于发布 bitfieldrw 包到 PyPI
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True):
    """运行命令并显示输出"""
    print(f"运行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        print(f"命令失败，返回码: {result.returncode}")
        sys.exit(1)
    
    return result


def main():
    """主发布流程"""
    # 确保在项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("=== 开始发布 bitfieldrw 包 ===")
    
    # 1. 运行测试
    print("\n1. 运行测试...")
    run_command("python -m unittest discover tests -v")
    
    # 2. 清理之前的构建
    print("\n2. 清理之前的构建...")
    run_command("rm -rf dist/ build/ *.egg-info/", check=False)
    
    # 3. 使用 uv 构建包
    print("\n3. 构建包...")
    run_command("uv build")
    
    # 4. 检查包
    print("\n4. 检查包...")
    run_command("uv run twine check dist/*")
    
    # 5. 询问是否上传到 PyPI
    print("\n5. 准备上传到 PyPI...")
    
    # 检查是否是测试上传
    test_upload = input("是否先上传到 TestPyPI? (y/N): ").lower().strip()
    
    if test_upload == 'y':
        print("上传到 TestPyPI...")
        run_command("uv run twine upload --repository testpypi dist/*")
        print("TestPyPI 上传完成！")
        print("可以通过以下命令测试安装:")
        print("pip install --index-url https://test.pypi.org/simple/ bitfieldrw")
        
        confirm = input("\n是否继续上传到正式 PyPI? (y/N): ").lower().strip()
        if confirm != 'y':
            print("取消上传到正式 PyPI")
            return
    
    # 上传到正式 PyPI
    confirm = input("确认上传到正式 PyPI? (y/N): ").lower().strip()
    if confirm == 'y':
        print("上传到 PyPI...")
        run_command("uv run twine upload dist/*")
        print("\n=== 发布完成! ===")
        print("可以通过以下命令安装:")
        print("pip install bitfieldrw")
    else:
        print("取消发布")


if __name__ == "__main__":
    main()
