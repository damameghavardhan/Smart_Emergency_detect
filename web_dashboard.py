import json
import sys
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QObject, QTimer, QUrl, pyqtSignal, pyqtSlot
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow

from Camera import CameraWorker
from Emergency import EmergencyTrafficController


class TrafficBridge(QObject):
    stateChanged = pyqtSignal(str)
    eventAdded = pyqtSignal(dict)
    cameraFrame = pyqtSignal(str)

    def __init__(self, dashboard: "TrafficDashboard") -> None:
        super().__init__(dashboard)
        self.dashboard = dashboard

    @pyqtSlot()
    def requestState(self) -> None:
        self.dashboard.publish_state()

    @pyqtSlot(int)
    def activateEmergency(self, duration: int) -> None:
        self.dashboard.activate_emergency(duration)

    @pyqtSlot()
    def releaseEmergency(self) -> None:
        self.dashboard.release_emergency()

    @pyqtSlot(int)
    def startCamera(self, camera_index: int) -> None:
        self.dashboard.start_camera(camera_index)

    @pyqtSlot()
    def stopCamera(self) -> None:
        self.dashboard.stop_camera()


class TrafficDashboard(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.controller = EmergencyTrafficController()
        self.camera_worker: CameraWorker | None = None
        self.camera_status = "OFFLINE"
        self.camera_index = 0
        self.camera_error = ""
        self.events: list[dict[str, str]] = []
        self.page_ready = False

        self.setWindowTitle("Sentinel | Emergency traffic priority")
        self.resize(1440, 940)
        self.setMinimumSize(360, 620)

        self.web_view = QWebEngineView(self)
        self.web_channel = QWebChannel(self.web_view.page())
        self.bridge = TrafficBridge(self)
        self.web_channel.registerObject("traffic", self.bridge)
        self.web_view.page().setWebChannel(self.web_channel)
        self.web_view.loadFinished.connect(self.on_page_loaded)
        self.setCentralWidget(self.web_view)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.advance_emergency)

        html_path = Path(__file__).with_name("Front.html")
        self.web_view.load(QUrl.fromLocalFile(str(html_path.resolve())))
        self.log_event("System initialized. Simulation ready.")

    def on_page_loaded(self, loaded: bool) -> None:
        self.page_ready = loaded
        if loaded:
            self.publish_state()

    def state_snapshot(self) -> dict:
        return {
            "signal": self.controller.signal,
            "secondsRemaining": self.controller.seconds_remaining,
            "emergencyActive": self.controller.emergency_active,
            "vehicle": self.controller.vehicle or "Ambulance",
            "cameraStatus": self.camera_status,
            "cameraIndex": self.camera_index,
            "cameraError": self.camera_error,
            "events": list(self.events),
        }

    def publish_state(self) -> None:
        if self.page_ready:
            self.bridge.stateChanged.emit(json.dumps(self.state_snapshot()))

    def activate_emergency(self, duration: int) -> None:
        duration = max(5, min(120, int(duration)))
        self.controller.activate("Ambulance", duration)
        self.timer.start()
        self.log_event(f"Manual ambulance priority granted for {duration} seconds.")
        self.publish_state()

    def advance_emergency(self) -> None:
        if not self.controller.emergency_active:
            self.timer.stop()
            return

        expired = self.controller.advance()
        if expired:
            self.timer.stop()
            self.log_event("Priority window expired. Signal returned to RED.")
        self.publish_state()

    def release_emergency(self) -> None:
        if not self.controller.emergency_active:
            return

        self.controller.reset()
        self.timer.stop()
        self.log_event("Priority released by operator. Signal returned to RED.")
        self.publish_state()

    def start_camera(self, camera_index: int) -> None:
        if self.camera_worker and self.camera_worker.isRunning():
            return

        self.camera_index = max(0, min(8, int(camera_index)))
        self.camera_error = ""
        self.camera_status = "STARTING"
        worker = CameraWorker(self.camera_index, preview_fps=15)
        worker.frame_ready.connect(self.on_camera_frame)
        worker.camera_error.connect(self.on_camera_error)
        worker.finished.connect(self.on_camera_finished)
        self.camera_worker = worker
        worker.start()
        self.log_event(f"Camera preview requested for device {self.camera_index:02d}.")
        self.publish_state()

    def on_camera_frame(self, frame: str) -> None:
        if self.camera_status != "ONLINE":
            self.camera_status = "ONLINE"
            self.log_event(f"Camera preview online on device {self.camera_index:02d}.")
            self.publish_state()
        if self.page_ready:
            self.bridge.cameraFrame.emit(frame)

    def on_camera_error(self, message: str) -> None:
        self.camera_error = message
        self.camera_status = "ERROR"
        self.log_event(message)
        self.publish_state()

    def on_camera_finished(self) -> None:
        self.camera_worker = None
        if self.camera_status != "ERROR":
            self.camera_status = "OFFLINE"
        self.publish_state()

    def stop_camera(self) -> None:
        worker = self.camera_worker
        if worker and worker.isRunning():
            self.camera_status = "STOPPING"
            worker.requestInterruption()
            self.log_event("Camera preview stopped by operator.")
            self.publish_state()
            return

        self.camera_status = "OFFLINE"
        self.camera_error = ""
        self.publish_state()

    def log_event(self, message: str) -> None:
        event = {"time": datetime.now().strftime("%H:%M:%S"), "message": message}
        self.events.insert(0, event)
        del self.events[12:]
        if self.page_ready:
            self.bridge.eventAdded.emit(event)

    def closeEvent(self, event) -> None:
        self.timer.stop()
        if self.camera_worker and self.camera_worker.isRunning():
            self.camera_worker.requestInterruption()
            self.camera_worker.wait(2000)
        event.accept()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Sentinel Traffic Control")
    window = TrafficDashboard()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())