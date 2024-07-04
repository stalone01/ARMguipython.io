import sys
import random
import pyttsx3
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QListWidget, QTextEdit, QSplitter, QGridLayout, QLabel, QDialogButtonBox, QDialog, QComboBox
from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtGui import QPainter, QFont
import serial
import serial.tools.list_ports


class PortSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("select Port")
        self.setFixedSize(300,150)
        layout = QVBoxLayout(self)
        self.port_combobox = QComboBox()

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.acceptDrops.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def populate_ports(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combobox.addItem(port.device)
    
    def get_selecteed_port(self):
        return self.port_combobox.currentText()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("interface graphique")
        self.setGeometry(100, 100, 800, 600)

        #navbar
        self.navbar = QWidget()
        self.navbar.setFixedHeight(125)
        self.navbar_layout = QHBoxLayout()

        #btn pour connecter à l'arduino
        self.connect_btn = QPushButton("Se connecter")
        self.connect_btn.setFixedWidth(160)
        self.connect_btn.clicked.connect(self.show_port_selection_dialog)

        #btn reset
        self.reset_btn = QPushButton("retour")
        self.reset_btn.setFixedWidth(160)
        self.reset_btn.clicked.connect(self.reset_displays)

        self.navbar_layout.addWidget(self.connect_btn)
        self.navbar_layout.addWidget(self.reset_btn)
        self.navbar.setLayout(self.navbar_layout)

        #style de navbar
        self.navbar.setStyleSheet("""
        background: qlineargradient(
                                  x1:0, y1:0, x2:1, y2:0,
                                  stop: 0 black, stop: 0.3 red, stop: 1 black
                             );
        border-radius: 10px;
                        """)
        
        self.connect_btn.setStyleSheet("""
                    color: white;
                    background-color:blue;
                    border: 2px solid white;
                    border-radius: 10px;
                    padding: 5px 15px;    
                    """)
        self.reset_btn.setStyleSheet("""
                    color: white;
                    background-color:blue;
                    border: 2px solid white;
                    border-radius: 10px;
                    padding: 5px 15px;    
                    """)
        
        #ajout de colonne principales
        self.splitter = QSplitter(Qt.Horizontal)

        #list des capteurs
        self.sensors_list = QListWidget()
        self.sensors_list.setFixedWidth(200)
        self.sensors_list.addItem("TEMPERATURE")
        self.sensors_list.addItem("VIBRATION")
        self.sensors_list.addItem("PRESSION")
        self.sensors_list.addItem("TOUCHE")
        self.sensors_list.addItem("QUALITE D'EAU")
        self.sensors_list.addItem("TACTILE")

        self.sensors_list.currentRowChanged.connect(self.display_sensor_data)
        self.splitter.addWidget(self.sensors_list)

        #style liste des capteurs
        self.sensors_list.setStyleSheet("""
                    QListWidget{
                            background-color: maroon;
                            color: white;
                            border-radius: 10px;
                    }
                    QListWidget::item{
                            background-color: blue;
                            margin: 10px;
                            padding: 20px;
                            border: 1px solid white;
                            border-radius: 10px;
                            text-align: center;
                    }
                    QListWidget::item:selected{
                            background-color: #0559f7;
                    }
                """)
        #Grid layout pour l'affichage des données
        self.data_display_widget = QWidget()
        self.data_grid_layout = QGridLayout(self.data_display_widget)

        #affichage des données des capteurs
        self.temp_display = self.create_sensor_display("Temperature",line_plot=True)
        self.rigorisite_display = self.create_sensor_display("Vibration",line_plot=True)
        self.pressure_display = self.create_sensor_display("Pression",line_plot=True)
        self.touch_display = self.create_sensor_display("Touché",line_plot=True)
        self.water_qualit_display = self.create_sensor_display("qualité d'eau",line_plot=True)
        self.tactile_display = self.create_sensor_display("tactile",line_plot=True)

        #ajout des affichages des donnees des capteurs dans le grid
        self.data_grid_layout.addWidget(self.temp_display, 0, 0)
        self.data_grid_layout.addWidget(self.rigorisite_display, 0, 1)
        self.data_grid_layout.addWidget(self.pressure_display, 0, 2)
        self.data_grid_layout.addWidget(self.touch_display, 1, 0)
        self.data_grid_layout.addWidget(self.water_qualit_display, 1, 1)
        self.data_grid_layout.addWidget(self.tactile_display, 1, 2)

        self.splitter.addWidget(self.data_display_widget)

        #Taille relatives aux widgets
        self.splitter.setSizes([int(self.width()*0.2), int(self.width()*0.8)])

        #combiner le navbar et les colonnes principales
        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout(self.central_widget)

        self.central_layout.addWidget(self.navbar)
        self.central_layout.addWidget(self.splitter)

        self.setCentralWidget(self.central_widget)

        #Style de  au widget central
        self.central_widget.setStyleSheet("""
                                    background: qlineargradient(
                                  x1:0, y1:0, x2:1, y2:0,
                                  stop: 0 #250344, stop: 0.3 #0b3fce, stop: 1 #86066b
                             );
                                        """)
        
        #serial setup
        self.arduino = None
        self.timer = QTimer()
        # self.timer.timeout.connect(self.read_from_arduino) #decommentena ref mis arduino
        self.timer.timeout.connect(self.generate_fake_sensor_data) #commentena ref tena izy
        self.timer.start(1500) #commentena ref tena izy

        self.engine = pyttsx3.init()
        self.current_display = None 

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def stop_speaking(self):
        self.engine.stop()


    def create_sensor_display(self, label_text, line_plot=True):
        container = QWidget()
        layout = QVBoxLayout(container)
        label = QLabel(label_text)
        label.setStyleSheet("""
                font-size: 30px;
                font-family: 'Courier New';
                text-transform: uppercase;
                            """)
        layout.addWidget(label)

        if line_plot:
            #creation de line chart pour le capteur
            series = QLineSeries()
            chart = QChart()
            chart.addSeries(series)
            chart.createDefaultAxes()
            chart.setTitle(label_text)
            chart.legend().hide()

            axisX = QValueAxis()
            axisX.setLabelFormat("%i")
            axisX.setTitleText("Time")
            chart.addAxis(axisX, Qt.AlignBottom)
            series.attachAxis(axisX)

            axisY=QValueAxis()
            axisY.setLabelFormat("%i")
            axisY.setTitleText("Value")
            chart.addAxis(axisY, Qt.AlignLeft)
            series.attachAxis(axisY)

            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setMinimumSize(QSize(200, 200))

            layout.addWidget(chart_view)

            container.series = series
            container.chart = chart
            container.axisX = axisX
            container.axisy = axisY
       
        container.setStyleSheet("""
                    background-color: #e5e2e7;
                    color: black;
                    border: 1.3px solid black;
                    padding: 6px;
                    border-radius: 12px;
                                    """)
        return container

    def show_port_selection_dialog(self):
        dialog = PortSelectionDialog()
        if dialog.exec():
            selected_port = dialog.get_selecteed_port()
            self.connect_to_arduino(selected_port)
    
    def connect_to_arduino(self, port):
        self.arduino = serial.Serial(port, 9600)
        self.connect_btn.setText(f"Connecté  à port {port}")
      

    def read_from_arduino(self):
        if self.arduino and self.arduino.in_waiting > 0:
            data = self.arduino.readline().decode.strip()
            self.process_sensor_data(data)

    def process_sensor_data(self, data):
        sensor_data = data.split(",")
        for sensor in sensor_data:
            sensor_type, value = sensor.split(":")
            value = float(value)
            if sensor_type == "Temperature":
                self.update_chart(self.temp_display,value)
            elif sensor_type == "rigorisité":
                self.update_chart(self.rigorisite_display,value)
            elif sensor_type == "pression":
                self.update_chart(self.pressure_display,value)
            elif sensor_type == "touché":
                self.update_chart(self.touch_display,value)
            elif sensor_type == "qualité d'eau":
                self.update_chart(self.water_qualit_display,value)
            elif sensor_type == "tactile":
                self.update_chart(self.tactile_display,value)
    
    def update_chart(self, display, value):
        if isinstance(display.series, QLineSeries):
            count = display.series.count()
            display.series.append(count, value)

            display.axisX.setMax(count)
            display.axisy.setMax(max(display.axisy.max(), value))

            title = ""
            message = ""

            if display == self.temp_display:
                if value > 50:
                    title = "Temperature : tres chaud"
                    message = "tres chaud !!!"
                elif value < 20:
                    title = "Temperature : tres froid"
                    message = 'tres froid !!!'
                else:
                    title = "Temperature : ambiante"
                    message = 'temperature ambiante !!!'
            elif display == self.rigorisite_display:
                if value > 50:
                    title = "Surface : rigoreux"
                    message = 'surface rigoureux !!!'

                else:
                    title = "Surface : surface lisse"
                    message = 'surface lisse !!!'
            elif display == self.pressure_display:
                if value > 100:
                    title = "Objet ou surface : dur"
                    message = 'objet dur !!!'
                elif 100 > value > 50:
                    title = "Objet ou surface : moins dur"
                    message = 'objet moins dur !!!'
                else:
                    title = "objet mou !!!"
                    message = 'objet mou !!!'
            elif display == self.touch_display:
                if value > 0.8:
                    title = "sansation : ça fait tres mal"
                    message = 'ça fait mal !!!'
                elif 0.8 > value > 0.5 :
                    title = "sensation : ça fait mal"
                    message = 'ça pique !!!'
                else:
                    title = "sensation : chatoulle"
                    message = 'ça chatouille !!!'
            elif display == self.water_qualit_display:
                if value > 50:
                    title = "eau : buvable"
                    message = 'buvable !!!'
                else :
                    title = "eau : non buvable"
                    message = 'non buvable !!!'
            elif display == self.tactile_display:
                if value > 50:
                    title = "touché : la pomme"
                else:
                    title = "touché : les doigts"
            font = QFont("Arial", 10, QFont.Bold)
            display.chart.setTitleFont(font)
            display.chart.setTitle(title)

            if self.current_display == display:
                self.speak(message)
            else:
                self.stop_speaking()
    

    def display_sensor_data(self, index):
        sensor_displays = [self.temp_display, self.rigorisite_display, self.pressure_display, self.touch_display, self.water_qualit_display, self.tactile_display]
        if 0 <= index < len(sensor_displays):
            for display in sensor_displays:
                 display.hide()
            if self.current_display is not None:
                self.current_display.hide()
                self.stop_speaking()  # Stop speaking when switching displays
            self.current_display = sensor_displays[index]
            self.current_display.show()      


    def reset_displays(self, index):
        sensor_displays = [self.temp_display, self.rigorisite_display, self.pressure_display, self.touch_display, self.water_qualit_display, self.tactile_display]
        if 0 <= index < len(sensor_displays):
            for display in sensor_displays:
                display.show() 
            sensor_displays[index].show()
            self.stop_speaking()
            self.current_display = None
            self.sensors_list.clearSelection()


    def generate_fake_sensor_data(self): #commentena ref mis arduino 
        fake_data = f"Temperature:{random.uniform(3,150):.2f},"\
                    f"rigorisité:{random.uniform(0, 100):.2f},"\
                    f"pression:{random.uniform(0, 100):.2f},"\
                    f"touché:{random.uniform(0, 150):.2f},"\
                    f"qualité d'eau:{random.uniform(0, 100):.2f},"\
                    f"tactile:{random.uniform(0, 100):.2f}"
        self.process_sensor_data(fake_data)

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
