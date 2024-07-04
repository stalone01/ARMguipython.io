from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFrame
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class SensorMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moniteur des capteurs")
        self.setGeometry(100, 100, 1200, 800)

        # Set main layout
        main_layout = QVBoxLayout()

        # Title bar with Bluetooth status and buttons
        title_layout = QHBoxLayout()
        title_label = QLabel("Moniteur des capteurs")
        title_label.setFont(QFont("Aptos", 24))
        title_layout.addWidget(title_label, alignment=Qt.AlignLeft)

        self.bluetooth_status = QLabel("Non connecté")
        self.bluetooth_status.setFont(QFont("Aptos", 14))
        title_layout.addWidget(self.bluetooth_status, alignment=Qt.AlignRight)

        connect_button = QPushButton("Connecté")
        connect_button.setFont(QFont("Aptos", 14))
        title_layout.addWidget(connect_button, alignment=Qt.AlignRight)

        home_button = QPushButton("Accueil")
        home_button.setFont(QFont("Aptos", 14))
        title_layout.addWidget(home_button, alignment=Qt.AlignRight)

        main_layout.addLayout(title_layout)

        # Central panel with sensor data
        central_layout = QHBoxLayout()

        # Left menu panel
        menu_layout = QVBoxLayout()
        menu_label = QLabel("MENU")
        menu_label.setFont(QFont("Aptos", 18))
        menu_layout.addWidget(menu_label)
        for menu_item in ["My profile", "Dashboard", "Messages", "Leaders", "Statistics", "Logout"]:
            button = QPushButton(menu_item)
            button.setFont(QFont("Aptos", 14))
            menu_layout.addWidget(button)
        central_layout.addLayout(menu_layout)

        # Sensor data panels
        sensor_layout = QVBoxLayout()
        
        # Vibration panel
        vibration_panel = QFrame()
        vibration_panel.setFrameShape(QFrame.Box)
        vibration_layout = QVBoxLayout()
        vibration_label = QLabel("VIBRATION")
        vibration_label.setFont(QFont("Aptos", 18))
        vibration_layout.addWidget(vibration_label)
        vibration_panel.setLayout(vibration_layout)
        sensor_layout.addWidget(vibration_panel)

        # Pressure panel
        pressure_panel = QFrame()
        pressure_panel.setFrameShape(QFrame.Box)
        pressure_layout = QVBoxLayout()
        pressure_label = QLabel("PRESSION")
        pressure_label.setFont(QFont("Aptos", 18))
        pressure_layout.addWidget(pressure_label)
        pressure_panel.setLayout(pressure_layout)
        sensor_layout.addWidget(pressure_panel)

        # TDS panel
        tds_panel = QFrame()
        tds_panel.setFrameShape(QFrame.Box)
        tds_layout = QVBoxLayout()
        tds_label = QLabel("TDS")
        tds_label.setFont(QFont("Aptos", 18))
        tds_layout.addWidget(tds_label)
        tds_panel.setLayout(tds_layout)
        sensor_layout.addWidget(tds_panel)

        # Temperature panel
        temperature_panel = QFrame()
        temperature_panel.setFrameShape(QFrame.Box)
        temperature_layout = QVBoxLayout()
        temperature_label = QLabel("TEMPERATURE")
        temperature_label.setFont(QFont("Aptos", 18))
        temperature_layout.addWidget(temperature_label)
        temperature_panel.setLayout(temperature_layout)
        sensor_layout.addWidget(temperature_panel)

        # Touch panel
        touch_panel = QFrame()
        touch_panel.setFrameShape(QFrame.Box)
        touch_layout = QVBoxLayout()
        touch_label = QLabel("TOUCHES")
        touch_label.setFont(QFont("Aptos", 18))
        touch_layout.addWidget(touch_label)
        touch_panel.setLayout(touch_layout)
        sensor_layout.addWidget(touch_panel)

        central_layout.addLayout(sensor_layout)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

if __name__ == "__main__":
    app = QApplication([])
    window = SensorMonitorApp()
    window.show()
    app.exec()
