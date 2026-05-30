"""
Local Server — 接收 Chrome 扩展推送
"""
import logging
import threading
from flask import Flask, request, jsonify
from PySide6.QtCore import Signal, QObject

log = logging.getLogger(__name__)
PORT = 5719

class ServerSignals(QObject):
    data_received  = Signal(list)
    status_changed = Signal(str)

class LocalServer(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = ServerSignals()
        self._app = self._build_app()
        self._thread = None
    def _build_app(self) -> Flask:
        app = Flask(__name__)
        app.logger.disabled = True
        import logging as l; l.getLogger("werkzeug").setLevel(l.ERROR)
        server = self
        @app.after_request
        def _cors(resp):
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            return resp
        @app.route("/api/products", methods=["POST", "OPTIONS"])
        def receive_products():
            if request.method == "OPTIONS":
                return jsonify({"ok": True})
            try:
                body = request.get_json(force=True, silent=True) or {}
                products = body.get("products", [])
                if not products:
                    return jsonify({"error": "products 字段为空"}), 400
                log.info("LocalServer 收到 %d 条商品", len(products))
                server.signals.data_received.emit(products)
                return jsonify({"ok": True, "count": len(products)})
            except Exception as e:
                log.error("LocalServer 处理失败: %s", e)
                return jsonify({"error": str(e)}), 500
        @app.route("/api/ping", methods=["GET"])
        def ping():
            return jsonify({"ok": True, "app": "ShopeeScout", "version": "1.5"})
        return app
    def start(self):
        def _run():
            self.signals.status_changed.emit(f"本地服务已启动 → localhost:{PORT}")
            log.info("LocalServer 启动 localhost:%d", PORT)
            try:
                self._app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False, threaded=True)
            except OSError as e:
                self.signals.status_changed.emit(f"❌ 端口 {PORT} 已被占用")
        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
