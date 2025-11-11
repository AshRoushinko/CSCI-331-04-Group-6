import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QComboBox, QVBoxLayout, QWidget, QLabel, QTextEdit
from main import run_compare


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NY Route Planner")
        # self.setGeometry(200, 200, 300, 200)

        layout = QVBoxLayout()

        header = QLabel("Select a destination and click 'Find Routes'")
        layout.addWidget(header)

        self.combobox = QComboBox()
        self.combobox.addItems(['Buffalo', 'Syracuse', 'Albany', 'New York City'])
        layout.addWidget(self.combobox)

        button = QPushButton("Find Routes")
        button.setCheckable(True)
        button.clicked.connect(self.the_button_was_clicked)
        layout.addWidget(button)

        self.output = QTextEdit("")
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        Widget = QWidget()
        font = Widget.font()
        font.setPointSize(18)
        Widget.setFont(font)
        Widget.setLayout(layout)
        self.setCentralWidget(Widget)

        # Set the central widget of the Window.
        # self.setCentralWidget(button)

    def the_button_was_clicked(self):
        print("Clicked!")
        self.output.setText(f"Finding routes from Rochester to {self.combobox.currentText()}...")
        routes = run_compare("Rochester", self.combobox.currentText())
        # self.output.setText(f"Finding routes from Rochester to {self.combobox.currentText()}...")
        self.output.setText(f"Routes found: ")
        for route in routes:
            self.output.append(route)
        ##self.output.append("".join(routes))


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

