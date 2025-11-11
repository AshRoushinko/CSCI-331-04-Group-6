"""
NY Route Planner GUI Application
A comprehensive PyQt interface for the route planning system
"""

import sys
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime

# --- Qt compatibility shim: prefer PyQt6, fall back to PyQt5 ---
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QComboBox, QPushButton, QTextEdit, QLabel, QGroupBox,
        QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
        QTabWidget, QCheckBox, QSpinBox, QSlider, QProgressBar,
        QMenuBar, QMenu, QFileDialog, QMessageBox,
        QToolBar, QStatusBar, QGridLayout, QListWidget,
        QRadioButton, QButtonGroup, QFrame
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
    from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QAction
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
    QT6 = True
except ImportError:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QComboBox, QPushButton, QTextEdit, QLabel, QGroupBox,
        QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
        QTabWidget, QCheckBox, QSpinBox, QSlider, QProgressBar,
        QMenuBar, QMenu, QAction, QFileDialog, QMessageBox,
        QToolBar, QStatusBar, QGridLayout, QListWidget,
        QRadioButton, QButtonGroup, QFrame
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
    from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    QT6 = False

# Orientation shim for QSplitter
try:
    ORIENT_H = Qt.Orientation.Horizontal  # PyQt6
except AttributeError:
    ORIENT_H = Qt.Horizontal  # PyQt5

# Header resize mode shim (PyQt6 uses enum)
try:
    HEADER_STRETCH = QHeaderView.ResizeMode.Stretch  # PyQt6
except AttributeError:
    HEADER_STRETCH = QHeaderView.Stretch  # PyQt5

import matplotlib.pyplot as plt

# Ensure project root on sys.path for 'code' package
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import project modules (your project must have a top-level folder named 'code')
from code.route_planner import RoutePlanner, ComparisonResult  # adjust if your path differs
from code.utilities.data_loader import load_graph, get_graph_statistics
from code.utilities.visualizer import GraphVisualizer
from code.heartofitall.graph import Graph


class AlgorithmWorker(QThread):
    """Worker thread for running algorithms without blocking GUI"""
    progress = pyqtSignal(str)     # Algorithm name / status
    result = pyqtSignal(object)    # SearchResult
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, route_planner, algorithm, start, goal):
        super().__init__()
        self.route_planner = route_planner
        self.algorithm = algorithm
        self.start = start
        self.goal = goal

    def run(self):
        try:
            self.progress.emit(f"Running {self.algorithm}...")
            result = self.route_planner.run_single_algorithm(
                self.algorithm, self.start, self.goal
            )
            self.result.emit(result)
        except Exception as e:
            self.error.emit(f"{self.algorithm}: {e}")
        finally:
            self.finished.emit()


class RouteFinderGUI(QMainWindow):
    """Main GUI Application for NY Route Planner"""

    def __init__(self):
        super().__init__()
        self.graph: Optional[Graph] = None
        self.route_planner: Optional[RoutePlanner] = None
        self.visualizer: Optional[GraphVisualizer] = None
        self.current_results = []
        self.comparison_result: Optional[ComparisonResult] = None

        self.initUI()
        self.load_data()

    def initUI(self):
        """Initialize the user interface"""
        self.setWindowTitle("New York State Route Planner")
        self.setGeometry(100, 100, 1400, 900)

        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px 0 4px;
            }
            QPushButton {
                padding: 6px 10px;
            }
            QTableWidget {
                background: white;
            }
        """)

        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_search_tab(), "Single Search")
        self.tabs.addTab(self.create_comparison_tab(), "Compare Algorithms")
        layout.addWidget(self.tabs)

        # Status Bar
        self.statusBar().showMessage("Ready")

    def create_search_tab(self):
        """Create the single search tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Top controls group
        controls = QGroupBox("Search Controls")
        controls_layout = QGridLayout(controls)

        self.start_combo = QComboBox()
        self.goal_combo = QComboBox()

        self.algo_radio_buttons = {}
        algo_box = QGroupBox("Algorithm")
        algo_layout = QVBoxLayout(algo_box)
        for name in ["BFS", "DFS", "UCS", "Greedy", "A*", "IDA*"]:
            rb = QRadioButton(name)
            self.algo_radio_buttons[name] = rb
            algo_layout.addWidget(rb)
        self.algo_radio_buttons["A*"].setChecked(True)

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_single_search)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(140)

        row = 0
        controls_layout.addWidget(QLabel("Start:"), row, 0)
        controls_layout.addWidget(self.start_combo, row, 1)
        controls_layout.addWidget(QLabel("Goal:"), row, 2)
        controls_layout.addWidget(self.goal_combo, row, 3)
        row += 1
        controls_layout.addWidget(algo_box, row, 0, 1, 2)
        controls_layout.addWidget(self.run_button, row, 2, 1, 2)
        row += 1
        controls_layout.addWidget(self.output_text, row, 0, 1, 4)

        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(controls)

        # Right panel: Visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Graph canvas
        self.graph_figure = plt.Figure(figsize=(10, 8))
        self.graph_canvas = FigureCanvas(self.graph_figure)
        self.graph_toolbar = NavigationToolbar(self.graph_canvas, self)

        right_layout.addWidget(self.graph_toolbar)
        right_layout.addWidget(self.graph_canvas)

        # Add panels to main layout
        splitter = QSplitter(ORIENT_H)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 1050])

        layout.addWidget(splitter)

        return tab

    def create_comparison_tab(self):
        """Create the algorithm comparison tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        top = QGroupBox("Comparison Controls")
        g = QGridLayout(top)

        self.comp_start_combo = QComboBox()
        self.comp_goal_combo = QComboBox()

        self.algo_checkboxes = {}
        algo_box = QGroupBox("Algorithms to compare")
        v = QVBoxLayout(algo_box)
        for name in ["BFS", "DFS", "UCS", "Greedy", "A*", "IDA*"]:
            cb = QCheckBox(name)
            cb.setChecked(name in ["UCS", "A*"])
            self.algo_checkboxes[name] = cb
            v.addWidget(cb)

        self.parallel_checkbox = QCheckBox("Run in parallel (if supported)")
        self.compare_button = QPushButton("Compare")
        self.compare_button.clicked.connect(self.run_comparison)

        g.addWidget(QLabel("Start:"), 0, 0)
        g.addWidget(self.comp_start_combo, 0, 1)
        g.addWidget(QLabel("Goal:"), 0, 2)
        g.addWidget(self.comp_goal_combo, 0, 3)
        g.addWidget(algo_box, 1, 0, 1, 2)
        g.addWidget(self.parallel_checkbox, 1, 2, 1, 2)
        g.addWidget(self.compare_button, 2, 2, 1, 2)

        # Results table
        self.comparison_table = QTableWidget(0, 5)
        self.comparison_table.setHorizontalHeaderLabels(
            ["Algorithm", "Path Length", "Cost (mi)", "Nodes Expanded", "Runtime (ms)"]
        )
        self.comparison_table.horizontalHeader().setSectionResizeMode(HEADER_STRETCH)
        self.comparison_table.setMinimumHeight(180)

        layout.addWidget(top)
        layout.addWidget(self.comparison_table)

        return tab

    # ----------------------- Data Loading -----------------------

    def load_data(self):
        """Load graph data from CSV files"""
        try:
            # Load graph (project-relative paths)
            base_dir = Path(__file__).resolve().parents[2]
            cities_file = base_dir / "data" / "cities.csv"
            edges_file  = base_dir / "data" / "edges.csv"

            # Load using a robust reader that tolerates column-name variants
            self.graph = self.load_graph_with_fix(cities_file, edges_file)
            self.route_planner = RoutePlanner(self.graph)
            self.visualizer = GraphVisualizer(self.graph)

            # Populate city dropdowns
            cities = sorted(self.graph.get_all_cities())
            self.start_combo.addItems(cities)
            self.goal_combo.addItems(cities)
            self.comp_start_combo.addItems(cities)
            self.comp_goal_combo.addItems(cities)

            # Set defaults
            if "Rochester" in cities:
                self.start_combo.setCurrentText("Rochester")
                self.comp_start_combo.setCurrentText("Rochester")
            if "New York City" in cities:
                self.goal_combo.setCurrentText("New York City")
                self.comp_goal_combo.setCurrentText("New York City")

            # Initial draw
            self.draw_graph()
            self.statusBar().showMessage("Data loaded")
        except Exception as e:
            QMessageBox.critical(self, "Error loading data", str(e))

    def load_graph_with_fix(self, cities_file, edges_file):
        """Load graph with fixed column names"""
        graph = Graph()
        import csv

        # Load cities (handle column name variations)
        with open(cities_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                city_name = (row.get('city') or row.get('city_name') or '').strip()
                lat = float((row.get('latitude') or row.get('lat') or row.get('latitude ') or '').strip())
                lon = float((row.get('longitude') or row.get('lon') or '').strip())
                if city_name:
                    graph.add_city(city_name, lat, lon)

        # Load edges (handle column name variations)
        with open(edges_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                city1 = (row.get('city1') or row.get('from') or '').strip()
                city2 = (row.get('city2') or row.get('to') or '').strip()
                distance = float((row.get('distance') or row.get('distance_miles') or '').strip())
                if city1 and city2:
                    graph.add_edge(city1, city2, distance, bidirectional=True)

        return graph

    # ----------------------- Single Search -----------------------

    def run_single_search(self):
        """Run a single search algorithm"""
        selected_algo = None
        for algo, radio in self.algo_radio_buttons.items():
            if radio.isChecked():
                selected_algo = algo
                break

        if not selected_algo:
            QMessageBox.warning(self, "Warning", "Please select an algorithm")
            return

        start = self.start_combo.currentText()
        goal = self.goal_combo.currentText()
        if not start or not goal:
            QMessageBox.warning(self, "Warning", "Please select start and goal cities")
            return

        self.output_text.clear()

        # Worker thread to avoid blocking UI
        self.worker = AlgorithmWorker(self.route_planner, selected_algo, start, goal)
        self.worker.progress.connect(self.append_log)
        self.worker.result.connect(self.show_single_result)
        self.worker.error.connect(self.append_log)
        self.worker.finished.connect(lambda: self.statusBar().showMessage("Done"))
        self.statusBar().showMessage("Running...")
        self.worker.start()

    def show_single_result(self, result):
        """Display the result of a single algorithm run"""
        self.current_results = [result]
        self.append_log(f"Algorithm: {result.algorithm_name}")
        self.append_log(f"Path: {' -> '.join(result.path)}")
        self.append_log(f"Cost: {result.cost:.2f} miles")
        self.append_log(f"Nodes expanded: {result.nodes_expanded}")
        self.append_log(f"Runtime: {result.runtime_ms:.2f} ms")
        self.draw_graph(path=result.path)

    # ----------------------- Comparison -----------------------

    def run_comparison(self):
        """Run comparison of multiple algorithms"""
        start = self.comp_start_combo.currentText()
        goal = self.comp_goal_combo.currentText()

        if not start or not goal:
            QMessageBox.warning(self, "Warning", "Please select start and goal cities")
            return

        selected_algos = [algo for algo, cb in self.algo_checkboxes.items() if cb.isChecked()]
        if not selected_algos:
            QMessageBox.warning(self, "Warning", "Select at least one algorithm")
            return

        try:
            self.statusBar().showMessage("Comparing...")
            parallel = self.parallel_checkbox.isChecked()
            comparison = self.route_planner.run_comparison(start, goal, selected_algos, parallel)
            self.comparison_result = comparison

            self.comparison_table.setRowCount(len(comparison.results))
            for i, result in enumerate(comparison.results):
                self.comparison_table.setItem(i, 0, QTableWidgetItem(result.algorithm_name))
                self.comparison_table.setItem(i, 1, QTableWidgetItem(str(len(result.path))))
                self.comparison_table.setItem(i, 2, QTableWidgetItem(f"{result.cost:.1f}"))
                self.comparison_table.setItem(i, 3, QTableWidgetItem(str(result.nodes_expanded)))
                self.comparison_table.setItem(i, 4, QTableWidgetItem(f"{result.runtime_ms:.2f}"))

            # Draw best path (lowest cost)
            best = min(comparison.results, key=lambda r: r.cost)
            self.draw_graph(path=best.path)
            self.append_log("Comparison complete.")
        except Exception as e:
            QMessageBox.critical(self, "Comparison error", str(e))
        finally:
            self.statusBar().showMessage("Ready")

    # ----------------------- Visualization -----------------------

    def draw_graph(self, path: Optional[List[str]] = None):
        """Render the graph and (optionally) a path on the canvas."""
        self.graph_figure.clear()
        ax = self.graph_figure.add_subplot(111)
        ax.set_title("NY State Graph")

        if self.visualizer:
            self.visualizer.draw_graph(ax=ax, highlight_path=path)

        self.graph_canvas.draw_idle()

    def append_log(self, text: str):
        self.output_text.append(text)

    # ----------------------- Menu / Actions (placeholder) -----------------------

    def create_menus(self):
        """If you later add menus, create them here."""
        pass


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look

    gui = RouteFinderGUI()
    gui.show()

    # PyQt6 uses exec(), PyQt5 uses exec_()
    exec_fn = getattr(app, 'exec', None) or app.exec_
    sys.exit(exec_fn())


if __name__ == '__main__':
    main()
