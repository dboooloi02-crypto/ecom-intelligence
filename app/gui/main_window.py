"""
选品决策助手 GUI — 市场报告视图

数据来源选择（CSV/AI搜索）
    ↓
市场报告卡片（宏观分析）
    ↓
AI示例商品列表（标注：非实时数据）
    ↓
未来：Shopee真实数据
"""
import sys
import os
import csv

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QSplitter,
    QListWidget, QListWidgetItem, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QIcon

from app.core.logger import get_logger
from app.core.tasks.worker import TaskManager, PipelineWorker
from app.pipelines.csv_pipeline import CSVPipeline
from app.pipelines.ai_pipeline import AIPipeline
from app.reports.generator import ReportGenerator
from app.shared.models.product import Product
from app.shared.models.market_report import MarketReport

# Colors
C_BG = "#f8f9fa"
C_SIDEBAR = "#1e293b"
C_SIDEBAR_TEXT = "#94a3b8"
C_BLUE = "#3b82f6"
C_WHITE = "#ffffff"
C_BORDER = "#e2e8f0"
C_GREEN = "#22c55e"
C_YELLOW = "#eab308"
C_RED = "#ef4444"
C_TEXT = "#1e293b"
C_TEXT2 = "#64748b"
C_TAG_BG = "#fef9c3"
C_TAG_TEXT = "#854d0e"


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.log = get_logger("gui")
        self.log.info("启动 GUI")
        self.setWindowTitle("选品决策助手")
        self.setMinimumSize(1100, 750)
        self.setStyleSheet(f"background: {C_BG};")

        self.csv_pipeline = CSVPipeline()
        try:
            self.ai_pipeline = AIPipeline(api_key=os.environ.get("ZHIPUAI_API_KEY", ""))
        except Exception:
            self.ai_pipeline = None
        from app.core.shopee_pipeline import ShopeePipeline
        self.shopee_pipeline = ShopeePipeline()
        from app.core.local_server import LocalServer
        self._local_server = LocalServer(self)
        self._local_server.signals.data_received.connect(self._on_extension_data)
        self.reporter = ReportGenerator()
        self.task_mgr = TaskManager()
        self.current_mode = "ai"
        self.current_report = None
        self.csv_products = []

        self._build_ui()

        # LocalServer 启动（必须等 _build_ui 创建 status_label 后再连接）
        self._local_server.signals.status_changed.connect(lambda msg: self.status_label.setText(msg))
        self._local_server.start()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar)

        content = self._build_content()
        main_layout.addWidget(content, 1)

    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"background: {C_SIDEBAR};")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(4)

        brand = QLabel("选品决策助手")
        brand.setStyleSheet(f"color: white; font-size: 18px; font-weight: bold; padding: 0 20px 20px 20px;")
        layout.addWidget(brand)

        title = QLabel("数据来源")
        title.setStyleSheet(f"color: {C_SIDEBAR_TEXT}; font-size: 11px; padding: 10px 20px 4px 20px;")
        layout.addWidget(title)

        self.btn_ai = QPushButton("AI 搜索")
        self.btn_ai.setCheckable(True)
        self.btn_ai.setChecked(True)
        self.btn_ai.clicked.connect(lambda: self._switch_mode("ai"))
        self.btn_ai.setStyleSheet(self._btn_style(True))
        layout.addWidget(self.btn_ai)

        self.btn_csv = QPushButton("CSV 导入")
        self.btn_csv.setCheckable(True)
        self.btn_csv.clicked.connect(lambda: self._switch_mode("csv"))
        self.btn_csv.setStyleSheet(self._btn_style(False))
        layout.addWidget(self.btn_csv)

        self.btn_shopee = QPushButton("Shopee 搜索")
        self.btn_shopee.clicked.connect(self._run_shopee_search)
        self.btn_shopee.setStyleSheet("""
            QPushButton { background: transparent; color: #94a3b8; border: none;
                padding: 10px 20px; text-align: left; font-size: 13px; }
            QPushButton:hover { background: #334155; color: white; }
        """)
        layout.addWidget(self.btn_shopee)

        layout.addStretch()
        ver = QLabel("v2.1 · 市场研究系统")
        ver.setStyleSheet(f"color: {C_SIDEBAR_TEXT}; font-size: 10px; padding: 0 20px;")
        layout.addWidget(ver)
        return sidebar

    def _btn_style(self, active):
        if active:
            return f"QPushButton {{ background: {C_BLUE}; color: white; border: none; padding: 10px 20px; text-align: left; font-size: 13px; }}"
        return f"QPushButton {{ background: transparent; color: {C_SIDEBAR_TEXT}; border: none; padding: 10px 20px; text-align: left; font-size: 13px; }} QPushButton:hover {{ background: #334155; color: white; }}"

    def _build_content(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        self.content_layout = QVBoxLayout(container)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(12)

        # Input area
        self.input_widget, self.input_layout = QWidget(), QHBoxLayout()
        self.input_widget.setLayout(self.input_layout)
        self.input_layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词，例如：宠物饮水机")
        self.search_input.setStyleSheet(self._input_style())
        self.search_input.returnPressed.connect(self._run_ai_search)
        self.input_layout.addWidget(self.search_input, 1)

        self.action_btn = QPushButton("AI 搜索")
        self.action_btn.setStyleSheet(self._btn_primary_style())
        self.action_btn.clicked.connect(self._run_ai_search)
        self.input_layout.addWidget(self.action_btn)

        self.content_layout.addWidget(self.input_widget)

        # Market report area
        self.report_container = QWidget()
        self.report_layout = QVBoxLayout(self.report_container)
        self.report_layout.setContentsMargins(0, 0, 0, 0)
        self.report_layout.setSpacing(12)
        self.content_layout.addWidget(self.report_container, 1)

        # Status bar
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet(f"color: {C_TEXT2}; font-size: 12px;")
        self.content_layout.addWidget(self.status_label)

        # Empty state
        self.empty_label = QLabel("输入关键词，开始市场研究")
        self.empty_label.setStyleSheet(f"color: {C_TEXT2}; font-size: 16px; padding: 80px;")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.report_layout.addWidget(self.empty_label)

        scroll.setWidget(container)
        return scroll

    def _input_style(self):
        return f"QLineEdit {{ background: {C_WHITE}; border: 1px solid {C_BORDER}; border-radius: 8px; padding: 10px; font-size: 14px; }} QLineEdit:focus {{ border-color: {C_BLUE}; }}"

    def _btn_primary_style(self):
        return f"QPushButton {{ background: {C_BLUE}; color: white; border: none; border-radius: 8px; padding: 10px 24px; font-size: 14px; font-weight: bold; }} QPushButton:hover {{ background: #2563eb; }}"

    def _switch_mode(self, mode):
        self.current_mode = mode
        self.btn_ai.setStyleSheet(self._btn_style(mode == "ai"))
        self.btn_csv.setStyleSheet(self._btn_style(mode == "csv"))
        if mode == "ai":
            self.search_input.setPlaceholderText("输入关键词，例如：宠物饮水机")
            self.action_btn.setText("AI 搜索")
            self.search_input.show()
        else:
            self.search_input.setPlaceholderText("选择 CSV 文件...")
            self.action_btn.setText("选择文件")
            self.search_input.hide()
        self._clear_report()

    def _clear_report(self):
        self.current_report = None
        self._clear_layout(self.report_layout)
        self.empty_label = QLabel("输入关键词，开始市场研究" if self.current_mode == "ai" else "选择 CSV 文件导入数据")
        self.empty_label.setStyleSheet(f"color: {C_TEXT2}; font-size: 16px; padding: 80px;")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.report_layout.addWidget(self.empty_label)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _run_ai_search(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            return
        if self.ai_pipeline is None:
            self.status_label.setText("❌ AI 搜索需要配置 ZHIPUAI_API_KEY 环境变量（商业版功能）")
            return
        self.status_label.setText(f"AI 正在分析「{keyword}」...")
        self.action_btn.setEnabled(False)
        self._clear_layout(self.report_layout)

        loading = QLabel("AI 正在分析市场...")
        loading.setStyleSheet(f"color: {C_TEXT2}; font-size: 14px; padding: 40px;")
        loading.setAlignment(Qt.AlignCenter)
        self.report_layout.addWidget(loading)

        worker = PipelineWorker(self.ai_pipeline.run, keyword)
        worker.signals.progress.connect(self._on_ai_progress)
        worker.signals.finished.connect(self._on_ai_done)
        worker.signals.error.connect(self._on_ai_error)
        self.task_mgr.run(worker)

    def _on_ai_done(self, report):
        self.action_btn.setEnabled(True)
        self.current_report = report
        self._clear_layout(self.report_layout)
        self.status_label.setText(f"分析完成 — 评分 {report.market_score}")

    def _on_ai_progress(self, msg: str):
        self.status_label.setText(msg)

    def _on_ai_error(self, msg: str):
        self.action_btn.setEnabled(True)
        self.status_label.setText("分析失败")
        self._clear_layout(self.report_layout)
        err_label = QLabel(f"AI 分析出错：{msg}")
        err_label.setStyleSheet(f"color: {C_RED}; font-size: 14px; padding: 40px;")
        err_label.setAlignment(Qt.AlignCenter)
        self.report_layout.addWidget(err_label)

    def _run_csv_import(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择 CSV 文件", "", "CSV 文件 (*.csv)")
        if not path:
            return
        self.status_label.setText(f"正在分析 {os.path.basename(path)}...")
        try:
            rows = []
            with open(path, encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    rows.append(row)
            if not rows:
                QMessageBox.warning(self, "提示", "CSV 文件为空")
                return
            products = self.csv_pipeline.run(rows)
            self._render_product_table(products, source_tag="CSV")
            self.status_label.setText(f"CSV 分析完成 — {len(products)} 个商品")
        except Exception as e:
            self.status_label.setText("导入失败")
            QMessageBox.warning(self, "错误", f"CSV 解析失败：{e}")

    def _render_product_table(self, products: list, source_tag: str = "CSV"):
        self._clear_layout(self.report_layout)
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["推荐", "商品", "售价", "月销", "综合分", "来源"])
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setStyleSheet(f"""QTableWidget {{ background: {C_WHITE}; border: 1px solid {C_BORDER}; border-radius: 8px; font-size: 13px; }} QHeaderView::section {{ background: {C_BG}; color: {C_TEXT2}; padding: 8px; border: none; font-size: 12px; }}""")
        table.setRowCount(len(products))
        for i, p in enumerate(products):
            rec = p.recommendation
            table.setItem(i, 0, QTableWidgetItem(rec))
            table.setItem(i, 1, QTableWidgetItem(p.title[:50]))
            table.setItem(i, 2, QTableWidgetItem(f"¥{p.price:.0f}"))
            table.setItem(i, 3, QTableWidgetItem(str(p.sold)))
            table.setItem(i, 4, QTableWidgetItem(f"{p.final_score:.1f}"))
            table.setItem(i, 5, QTableWidgetItem(source_tag))
            color = C_GREEN if "推荐" in rec else (C_YELLOW if "观察" in rec else C_RED)
            table.item(i, 0).setForeground(QColor(color))
        self.report_layout.addWidget(table)

    def _run_shopee_search(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            return
        self.status_label.setText("🔄 连接 Shopee...")
        self.btn_shopee.setEnabled(False)
        worker = PipelineWorker(self.shopee_pipeline.run, keyword)
        worker.signals.progress.connect(self._on_ai_progress)
        worker.signals.finished.connect(self._on_shopee_done)
        worker.signals.error.connect(self._on_shopee_error)
        self.task_mgr.run(worker)

    def _on_shopee_done(self, products):
        self.btn_shopee.setEnabled(True)
        if not products:
            self.status_label.setText("⚠️ 未获取到数据")
            return
        self._render_product_table(products, source_tag="Shopee实时")
        self.status_label.setText(f"✅ Shopee 实时数据：{len(products)} 个商品")

    def _on_shopee_error(self, msg: str):
        self.btn_shopee.setEnabled(True)
        self.status_label.setText(f"❌ {msg}")

    def _on_extension_data(self, raw_products: list):
        self.status_label.setText(f"⚙️ 正在计算 {len(raw_products)} 个商品评分...")
        rows = [{"title": str(p.get("title", "")), "price": str(p.get("price", 0)), "sold": str(p.get("sold", 0)), "rating": str(p.get("rating", 0))} for p in raw_products]
        try:
            products = self.csv_pipeline.run(rows)
            for product, raw in zip(products, raw_products):
                product.source_tag = "shopee_realtime"
                product.url = raw.get("url", "")
            self._render_product_table(products, source_tag="Shopee实时")
            self.status_label.setText(f"✅ 扩展数据：{len(products)} 个商品")
        except Exception as e:
            self.status_label.setText(f"❌ 评分失败：{e}")

    def run(self):
        self.show()
