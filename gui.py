import sys, json, random
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QFormLayout
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
import pyqtgraph as pg
from agent import MqttClient
from init import COMM_ROOT, MAX_SPOTS

class SignalHandler(QObject):
    alarm_signal = pyqtSignal(str)
    barrier_signal = pyqtSignal(str)
    occupancy_signal = pyqtSignal(int)

class StatusDock(QDockWidget):
    def __init__(self):
        super().__init__('Status & Alarms')
        self.occ  = QLabel('0')
        self.bar  = QLabel('CLOSED')
        self.alarms = QTextEdit(); self.alarms.setReadOnly(True)
        w = QWidget(); f = QFormLayout(w)
        f.addRow('Occupied spots:', self.occ)
        f.addRow('Barrier state:', self.bar)
        f.addRow('Alarms:', self.alarms)
        self.setWidget(w)

class PlotDock(QDockWidget):
    def __init__(self):
        super().__init__('Occupancy')
        self.plot = pg.PlotWidget(); self.plot.showGrid(x=True, y=True)
        w = QWidget(); v = QVBoxLayout(w); v.addWidget(self.plot)
        self.setWidget(w)
        self.x = []; self.y = []

class ControlDock(QDockWidget):
    def __init__(self, mqtt):
        super().__init__('Controls')
        self.mqtt = mqtt
        self.btnOpen  = QPushButton('Open Barrier')
        self.btnClose = QPushButton('Close Barrier')
        self.btnExit  = QPushButton('Exit')
        
        self.btnOpen.clicked.connect(lambda: self.send_barrier('OPEN'))
        self.btnClose.clicked.connect(lambda: self.send_barrier('CLOSED'))
        self.btnExit.clicked.connect(lambda: QApplication.quit())

        w = QWidget(); v = QVBoxLayout(w)
        v.addWidget(self.btnOpen); v.addWidget(self.btnClose); v.addWidget(self.btnExit)
        self.setWidget(w)

    def send_barrier(self, s):
        self.mqtt.publish(f"{COMM_ROOT}control/barrier-1/set", json.dumps({'state': s}))
        self.mqtt.publish(f"{COMM_ROOT}sensors/exit/button", 'PRESS')

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Smart Parking — Main GUI')
        self.stat = StatusDock(); self.plotDock = PlotDock()
        self.mqtt = MqttClient('parking-gui'); self.ctrl = ControlDock(self.mqtt)
        self.addDockWidget(0x1, self.stat); self.addDockWidget(0x2, self.plotDock); self.addDockWidget(0x1, self.ctrl)
        
        # Signal handler for thread-safe GUI updates
        self.signal_handler = SignalHandler()
        self.signal_handler.alarm_signal.connect(self.update_alarms)
        self.signal_handler.barrier_signal.connect(self.update_barrier)
        self.signal_handler.occupancy_signal.connect(self.update_occupancy)
        
        self.mqtt.connect()

        def on_msg(c,u,m):
            t = m.topic; p = m.payload.decode('utf-8','ignore')
            if t == f"{COMM_ROOT}alarm":
                try:
                    j = json.loads(p)
                    msg = f"{j.get('level')}: {j.get('message')}"
                except:
                    msg = p
                self.signal_handler.alarm_signal.emit(msg)
            elif t.endswith('/state') and 'barrier-1' in t:
                self.signal_handler.barrier_signal.emit(p)
            elif t.endswith('/occupied'):
                try:
                    val = int(p)
                    self.signal_handler.occupancy_signal.emit(val)
                except:
                    pass

        self.mqtt.client.on_message = on_msg
        self.mqtt.subscribe(f"{COMM_ROOT}alarm")
        self.mqtt.subscribe(f"{COMM_ROOT}sensors/barrier-1/state")
        self.mqtt.subscribe(f"{COMM_ROOT}sensors/lot/occupied")

    def update_alarms(self, msg):
        self.stat.alarms.append(msg)

    def update_barrier(self, state):
        self.stat.bar.setText(state)

    def update_occupancy(self, val):
        self.stat.occ.setText(str(val))
        self.plotDock.x.append(len(self.plotDock.x)+1)
        self.plotDock.y.append(val)
        self.plotDock.plot.plot(self.plotDock.x, self.plotDock.y, clear=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Main(); w.resize(900,600); w.show()
    sys.exit(app.exec_())