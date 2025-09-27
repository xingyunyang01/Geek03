#!/usr/bin/env python3
"""
启动脚本 - 深度研究助手Streamlit应用
"""

import subprocess
import sys
import os

def main():
    """启动Streamlit应用"""
    try:
        # 检查是否安装了streamlit
        import streamlit
        print("✅ Streamlit已安装")
    except ImportError:
        print("❌ Streamlit未安装，正在安装依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # 启动应用
    print("🚀 启动深度研究助手...")
    print("📱 应用将在浏览器中打开: http://localhost:8501")
    print("⏹️  按 Ctrl+C 停止应用")
    
    # 运行streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])

if __name__ == "__main__":
    main() 