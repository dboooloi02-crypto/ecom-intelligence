@echo off
chcp 65001 >nul
title 选品决策助手
cd /d "%~dp0"
python main.py
if %errorlevel% neq 0 (
    echo [错误] 程序异常退出
    pause
)
