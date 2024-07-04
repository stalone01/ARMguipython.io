import sys
import random
import pyttsx3
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QGridLayout, QLabel, QFrame, QSplitter
from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtGui import QPainter, QFont, QPixmap, QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Moniteur de Capteurs")
        self.showMaximized()

        # Créer le layout principal
        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout(self.central_widget)

        # Ajouter un titre
        self.title = QLabel("Moniteur de Capteurs")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Aptos", 24))
        self.title.setStyleSheet("color: #2c3e50;")
        self.central_layout.addWidget(self.title)

        # Ajouter une barre de boutons en haut à droite
        self.top_button_bar = QHBoxLayout()
        self.top_button_bar.addStretch(1)
        self.connect_button = QPushButton("Connecter")
        self.home_button = QPushButton("Accueil")
        self.connection_status = QLabel("Non connecté")
        self.connection_status.setFont(QFont("Aptos", 14))
        self.connection_status.setStyleSheet("color: #7f8c8d;")

        self.top_button_bar.addWidget(self.connection_status)
        self.top_button_bar.addWidget(self.connect_button)
        self.top_button_bar.addWidget(self.home_button)
        self.central_layout.addLayout(self.top_button_bar)

        self.connect_button.setFixedSize(120, 40)
        self.home_button.setFixedSize(120, 40)
        self.connect_button.setFont(QFont("Aptos", 14))
        self.home_button.setFont(QFont("Aptos", 14))

        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                font-size: 14px;
                font-family: 'Aptos';
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        self.home_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 14px;
                font-family: 'Aptos';
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)

        self.home_button.clicked.connect(self.show_all_charts)

        # Ajouter la barre latérale
        self.sidebar = QFrame()
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar_layout = QVBoxLayout(self.sidebar)

        # Boutons du menu
        self.buttons = {}
        sensors = ["Pression", "Vibration", "Temperature", "Touches", "TDS"]
        for sensor in sensors:
            btn = QPushButton(sensor)
            btn.setFixedHeight(40)
            btn.setFont(QFont("Aptos", 14))
            btn.clicked.connect(self.display_sensor_chart)
            self.sidebar_layout.addWidget(btn)
            self.buttons[sensor] = btn

        # Style de la barre latérale
        self.sidebar.setStyleSheet("""
        background-color: #2c3e50;
        color: white;
        """)
        for btn in self.buttons.values():
            btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                border: none;
                color: white;
                text-align: left;
                padding: 10px;
                font-family: 'Aptos';
            }
            QPushButton:hover {
                background-color: #16a085;
            }
            """)

        # Créer la zone de contenu principal
        self.content_area = QSplitter(Qt.Horizontal)

        # Grid layout pour les affichages des données
        self.data_display_widget = QWidget()
        self.data_grid_layout = QGridLayout(self.data_display_widget)

        # Affichage des données des capteurs
        self.displays = {}
        for i, sensor in enumerate(sensors):
            display = self.create_sensor_display(sensor)
            self.data_grid_layout.addWidget(display, i//2, i%2)
            self.displays[sensor] = display

        self.content_area.addWidget(self.sidebar)
        self.content_area.addWidget(self.data_display_widget)

        # Ajouter la barre latérale et la zone de contenu au layout principal
        self.central_layout.addWidget(self.content_area)
        self.central_layout.setStretch(0, 1)
        self.central_layout.setStretch(1, 4)
        self.setCentralWidget(self.central_widget)

        # Configuration du timer pour générer des données de capteur factices
        self.timer = QTimer()
        self.timer.timeout.connect(self.generate_fake_sensor_data)
        self.timer.start(1500)

        self.engine = pyttsx3.init()
        self.current_display = None 

    def create_sensor_display(self, label_text):
        container = QWidget()
        layout = QVBoxLayout(container)
        label = QLabel(label_text)
        label.setFont(QFont("Aptos", 20))
        layout.addWidget(label)

        value_label = QLabel("Valeur: 0")
        value_label.setFont(QFont("Aptos", 16))
        value_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(value_label)
        container.value_label = value_label

        if label_text == "Touches":
            container.image_label = QLabel()
            layout.addWidget(container.image_label)
        else:
            series = QLineSeries()
            chart = QChart()
            chart.addSeries(series)
            chart.createDefaultAxes()
            chart.setTitle(label_text)
            chart.legend().hide()

            axisX = QValueAxis()
            axisX.setLabelFormat("%i")
            axisX.setTitleText("Temps")
            chart.addAxis(axisX, Qt.AlignBottom)
            series.attachAxis(axisX)

            axisY = QValueAxis()
            axisY.setLabelFormat("%i")
            axisY.setTitleText("Valeur")
            chart.addAxis(axisY, Qt.AlignLeft)
            series.attachAxis(axisY)

            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setMinimumSize(QSize(200, 200))

            layout.addWidget(chart_view)

            container.series = series
            container.chart = chart
            container.axisX = axisX
            container.axisY = axisY

        container.setStyleSheet("""
            background-color: #ecf0f1;
            color: black;
            border: 1px solid #bdc3c7;
            padding: 10px;
            border-radius: 5px;
        """)
        return container

    def display_sensor_chart(self):
        button = self.sender()
        sensor = button.text()

        for name, display in self.displays.items():
            display.hide()
        
        self.displays[sensor].show()
        self.content_area.setSizes([1, 4])
        self.speak(f"Affichage des données pour {sensor}")

    def generate_fake_sensor_data(self):
        fake_data = {
            "Pression": random.uniform(0, 30),
            "Vibration": random.uniform(0, 100),
            "Temperature": random.uniform(0, 40),
            "Touches": random.randint(0, 4),
            "TDS": random.uniform(0, 1200)
        }
        for sensor, value in fake_data.items():
            self.update_chart(self.displays[sensor], value)
            self.update_value_label(self.displays[sensor], value)

    def update_chart(self, display, value):
        if hasattr(display, 'series'):
            count = display.series.count()
            display.series.append(count, value)

            display.axisX.setMax(count)
            display.axisY.setMax(max(display.axisY.max(), value))

    def update_value_label(self, display, value):
        sensor = display.chart.title() if hasattr(display, 'chart') else "Touches"
        description = ""
        if sensor == "Temperature":
            description = "Froid" if value < 10 else "Chaud"
        elif sensor == "Pression":
            if value < 2:
                description = "sans objet"
            elif 2 <= value < 20:
                description = "objet mou"
            elif 20 <= value < 25:
                description = "objet un peu dur"
            else:
                description = "objet dur"
        elif sensor == "Vibration":
            description = "Niveau de vibration"
            display.chart.axisX().setTickCount(int(display.series.count() * 8))
        elif sensor == "TDS":
            if value < 5:
                description = "eau non détectée"
            elif 5 <= value < 40:
                description = "eau manque des minérales"
            elif 40 <= value < 80:
                description = "eau courante"
            elif 80 <= value < 150:
                description = "eau filtrée"
            elif 150 <= value < 300:
                description = "eau minérale"
            elif 300 <= value < 700:
                description = "eau non potable"
            else:
                description = "eau très salée"
        elif sensor == "Touches":
            finger_index = value
            fingers = ["Index", "Majeur", "Pouce", "Annulaire", "Auriculaire"]
            description = f"{fingers[finger_index]} touché"
            self.update_touch_image(display, finger_index)

        display.value_label.setText(f"Valeur: {value:.2f} - {description}")

    def update_touch_image(self, display, finger_index):
        pixmap = QPixmap(200, 200)
        pixmap.fill(Qt.white)
        painter = QPainter(pixmap)
        painter.setPen(Qt.black)
        fingers = ["Index", "Majeur", "Pouce", "Annulaire", "Auriculaire"]
        for i, finger in enumerate(fingers):
            if i == finger_index:
                painter.setBrush(Qt.black)
            else:
                painter.setBrush(Qt.white)
            painter.drawEllipse(40 * i + 10, 100, 30, 30)
        painter.end()
        display.image_label.setPixmap(pixmap)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def show_all_charts(self):
        for display in self.displays.values():
            display.show()
        self.content_area.setSizes([1, 4])
        self.speak("Affichage de tous les graphiques")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
