#!/usr/bin/env python3
"""
电磁干扰定位感知系统启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖包是否安装"""
    try:
        import flask
        import numpy
        import scipy
        print("✓ 所有依赖包已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖包: {e}")
        return False

def install_dependencies():
    """安装依赖包"""
    print("正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError:
        print("✗ 依赖包安装失败")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("EW THREAT DETECTION SYSTEM")
    print("=" * 50)
    
    # 检查当前目录
    if not Path("app.py").exists():
        print("✗ 请在项目根目录下运行此脚本")
        sys.exit(1)
    
    # 检查依赖
    if not check_dependencies():
        choice = input("是否自动安装依赖包? (y/n): ")
        if choice.lower() == 'y':
            if not install_dependencies():
                sys.exit(1)
        else:
            print("请手动安装依赖包: pip install -r requirements.txt")
            sys.exit(1)
    
    # 启动应用
    print("\n正在启动系统...")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n系统已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
