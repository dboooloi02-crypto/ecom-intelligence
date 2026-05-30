@echo off
chcp 65001 >nul
title 安装依赖
cd /d "%~dp0"
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
pause
