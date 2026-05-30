"""
选品决策助手 — 融合版入口
AI Agent 为核心，GUI/CSV/导出 为外围
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication
from app.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("选品决策助手")

    window = MainWindow()
    window.run()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
