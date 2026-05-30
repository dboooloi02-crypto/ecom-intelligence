"""
Task Worker — GUI 异步任务系统
"""
from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool

class WorkerSignals(QObject):
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(str)

class PipelineWorker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_cb'] = self.signals.progress.emit
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except TypeError as e:
            if 'progress_cb' in str(e):
                self.kwargs.pop('progress_cb', None)
                result = self.fn(*self.args, **self.kwargs)
                self.signals.finished.emit(result)
            else:
                self.signals.error.emit(str(e))
        except Exception as e:
            self.signals.error.emit(str(e))

class TaskManager:
    def __init__(self, max_threads=4):
        self.pool = QThreadPool()
        self.pool.setMaxThreadCount(max_threads)
    def run(self, worker: PipelineWorker):
        self.pool.start(worker)
    def active_count(self) -> int:
        return self.pool.activeThreadCount()
