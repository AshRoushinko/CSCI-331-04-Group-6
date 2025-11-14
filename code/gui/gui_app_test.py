"""
NY Route Planner GUI Application
A comprehensive PyQt6 interface for the route planning system
"""

import sys
from pathlib import Path
import json
from typing import Optional, List, Dict
from datetime import datetime

# Setup path to allow imports from project root
ROOT = Path(__file__).resolve().parents[2]  # Go up to CSCI-331-04-Group-6
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
import matplotlib.pyplot as plt

# Import project modules
try:
    # Try package-style imports first (when run from project root)
    from code.utilities.data_loader import load_graph, get_graph_statistics
    from code.utilities.route_planner import RoutePlanner
    from code.utilities.visualizer import GraphVisualizer
    from code.heartofitall.graph import Graph
    # Import algorithm classes directly for testing
    from code.algorithms.dfs import DFS
    from code.algorithms.bfs import BFS
    from code.algorithms.ucs import UCS
    from code.algorithms.greedy import GreedyBestFirst
    from code.algorithms.astar import AStar
except ModuleNotFoundError:
    # Fall back to relative imports (when run directly from gui folder)
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from code.utilities.data_loader import load_graph, get_graph_statistics
    from code.utilities.route_planner import RoutePlanner
    from code.utilities.visualizer import GraphVisualizer
    from code.heartofitall.graph import Graph
    # Import algorithm classes directly for testing
    from code.algorithms.dfs import DFS
    from code.algorithms.bfs import BFS
    from code.algorithms.ucs import UCS
    from code.algorithms.greedy import GreedyBestFirst
    from code.algorithms.astar import AStar


class AlgorithmWorker(QThread):
    """Worker thread for running algorithms without blocking GUI"""
    progress = pyqtSignal(str)  # Algorithm name
    result = pyqtSignal(object)  # SearchResult
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, graph, algorithm_class, algorithm_name, start_city, goal_city):
        super().__init__()
        self.graph = graph
        self.algorithm_class = algorithm_class  # Actual algorithm class (e.g., DFS)
        self.algorithm_name = algorithm_name    # Name for display (e.g., "DFS")
        self.start_city = start_city  # Changed from self.start to avoid collision!
        self.goal_city = goal_city    # Changed from self.goal for consistency

    def run(self):
        try:
            # Debug: Print what we're trying to run
            print(f"[DEBUG] AlgorithmWorker running: algorithm_class={self.algorithm_class}")
            print(f"[DEBUG] Algorithm name: {self.algorithm_name}")
            print(f"[DEBUG] Start: {self.start_city}, Goal: {self.goal_city}")
            print(f"[DEBUG] Type of algorithm_class: {type(self.algorithm_class)}")

            self.progress.emit(f"Running {self.algorithm_name}...")

            # Directly instantiate and run the algorithm
            algorithm_instance = self.algorithm_class(self.graph, self.start_city, self.goal_city)
            print(f"[DEBUG] Created instance: {algorithm_instance}")

            result = algorithm_instance.search()
            print(f"[DEBUG] Search completed successfully")

            self.result.emit(result)
        except Exception as e:
            import traceback
            error_msg = f"Error in {self.algorithm_name}: {str(e)}\n{traceback.format_exc()}"
            print(f"[DEBUG] Error occurred: {error_msg}")
            self.error.emit(error_msg)
        finally:
            self.finished.emit()


class RouteFinderGUI(QMainWindow):
    """Main GUI Application for NY Route Planner"""

    def __init__(self):
        super().__init__()
        self.graph = None
        self.route_planner = None
        self.visualizer = None
        self.current_results = []
        self.comparison_result = None

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
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)

        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Create main content area with tabs
        self.tab_widget = QTabWidget()

        # Tab 1: Route Finding
        self.route_tab = self.create_route_finding_tab()
        self.tab_widget.addTab(self.route_tab, "Route Finding")

        # Tab 2: Algorithm Comparison
        self.comparison_tab = self.create_comparison_tab()
        self.tab_widget.addTab(self.comparison_tab, "Algorithm Comparison")

        # Tab 3: Graph Statistics
        self.stats_tab = self.create_statistics_tab()
        self.tab_widget.addTab(self.stats_tab, "Graph Statistics")

        # Tab 4: Settings
        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "Settings")

        main_layout.addWidget(self.tab_widget)

    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        export_action = QAction('Export Results', self)
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu('View')

        refresh_action = QAction('Refresh Graph', self)
        refresh_action.triggered.connect(self.refresh_graph)
        view_menu.addAction(refresh_action)

        # Help menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create the application toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Run button
        run_action = QAction('Run Search', self)
        run_action.triggered.connect(self.run_single_search)
        toolbar.addAction(run_action)

        toolbar.addSeparator()

        # Compare button
        compare_action = QAction('Compare All', self)
        compare_action.triggered.connect(self.run_comparison)
        toolbar.addAction(compare_action)

        toolbar.addSeparator()

        # Clear button
        clear_action = QAction('Clear Results', self)
        clear_action.triggered.connect(self.clear_results)
        toolbar.addAction(clear_action)

    def create_route_finding_tab(self):
        """Create the route finding interface tab"""
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # Left panel: Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(350)

        # Route Selection
        route_group = QGroupBox("Route Selection")
        route_layout = QGridLayout()

        route_layout.addWidget(QLabel("Start City:"), 0, 0)
        self.start_combo = QComboBox()
        route_layout.addWidget(self.start_combo, 0, 1)

        route_layout.addWidget(QLabel("Goal City:"), 1, 0)
        self.goal_combo = QComboBox()
        route_layout.addWidget(self.goal_combo, 1, 1)

        route_group.setLayout(route_layout)
        left_layout.addWidget(route_group)

        # Algorithm Selection
        algo_group = QGroupBox("Algorithm Selection")
        algo_layout = QVBoxLayout()

        # NOTE: TESTING MODE - Dropdown is ignored, DFS is hardcoded in run_single_search()
        self.algo_combo = QComboBox()
        self._ALGO_LABEL_TO_KEY = {
            "DFS (Depth-First Search)": "DFS",
            "BFS (Breadth-First Search)": "BFS",
            "UCS (Uniform Cost Search)": "UCS",
            "Greedy Best-First": "Greedy",
            "A* Search": "A*",
        }

        self.algo_combo.addItems(list(self._ALGO_LABEL_TO_KEY.keys()))

        algo_layout.addWidget(self.algo_combo)

        self.heuristic_checkbox = QCheckBox("Use Manhattan Heuristic")
        self.heuristic_checkbox.setChecked(True)
        algo_layout.addWidget(self.heuristic_checkbox)

        algo_group.setLayout(algo_layout)
        left_layout.addWidget(algo_group)

        # Visualization Options
        viz_group = QGroupBox("Visualization Options")
        viz_layout = QVBoxLayout()

        self.show_path_checkbox = QCheckBox("Show Path")
        self.show_path_checkbox.setChecked(True)
        viz_layout.addWidget(self.show_path_checkbox)

        self.show_expanded_checkbox = QCheckBox("Show Expanded Nodes")
        self.show_expanded_checkbox.setChecked(True)
        viz_layout.addWidget(self.show_expanded_checkbox)

        self.show_weights_checkbox = QCheckBox("Show Edge Weights")
        viz_layout.addWidget(self.show_weights_checkbox)

        self.animation_checkbox = QCheckBox("Animate Search")
        viz_layout.addWidget(self.animation_checkbox)

        viz_group.setLayout(viz_layout)
        left_layout.addWidget(viz_group)

        # Control Buttons
        button_layout = QHBoxLayout()

        self.run_button = QPushButton("Run Algorithm")
        self.run_button.clicked.connect(self.run_single_search)
        button_layout.addWidget(self.run_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_results)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        button_layout.addWidget(self.clear_button)

        left_layout.addLayout(button_layout)

        # Results Display
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)

        results_group.setLayout(results_layout)
        left_layout.addWidget(results_group)

        left_layout.addStretch()

        # Right panel: Visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Graph visualization
        self.graph_figure = plt.figure(figsize=(10, 8))
        self.graph_canvas = FigureCanvas(self.graph_figure)
        self.graph_toolbar = NavigationToolbar(self.graph_canvas, self)

        right_layout.addWidget(self.graph_toolbar)
        right_layout.addWidget(self.graph_canvas)

        # Add panels to main layout
        layout.addWidget(left_panel)
        layout.addWidget(right_panel, 1)  # Give more space to visualization

        return tab

    def create_comparison_tab(self):
        """Create the algorithm comparison tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Top controls
        controls_layout = QHBoxLayout()

        # City selection
        controls_layout.addWidget(QLabel("Start:"))
        self.comp_start_combo = QComboBox()
        controls_layout.addWidget(self.comp_start_combo)

        controls_layout.addWidget(QLabel("Goal:"))
        self.comp_goal_combo = QComboBox()
        controls_layout.addWidget(self.comp_goal_combo)

        controls_layout.addStretch()

        # Algorithm selection
        algo_select_group = QGroupBox("Select Algorithms")
        algo_select_layout = QHBoxLayout()

        self.algo_checkboxes = {}
        algorithms = ["DFS", "BFS", "UCS", "Greedy", "A*"]
        for algo in algorithms:
            checkbox = QCheckBox(algo)
            checkbox.setChecked(True)
            self.algo_checkboxes[algo] = checkbox
            algo_select_layout.addWidget(checkbox)

        algo_select_group.setLayout(algo_select_layout)
        controls_layout.addWidget(algo_select_group)

        # Options
        self.parallel_checkbox = QCheckBox("Run in Parallel")
        controls_layout.addWidget(self.parallel_checkbox)

        # Run button
        self.compare_button = QPushButton("Run Comparison")
        self.compare_button.clicked.connect(self.run_comparison)
        controls_layout.addWidget(self.compare_button)

        layout.addLayout(controls_layout)

        # Results section
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Comparison table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.addWidget(QLabel("Algorithm Performance:"))

        self.comparison_table = QTableWidget()
        self.comparison_table.setColumnCount(6)
        self.comparison_table.setHorizontalHeaderLabels([
            "Algorithm", "Path Length", "Cost", "Nodes Expanded", "Runtime (ms)", "Optimal"
        ])
        self.comparison_table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(self.comparison_table)

        splitter.addWidget(table_widget)

        # Comparison charts
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)
        chart_layout.addWidget(QLabel("Performance Metrics:"))

        self.comparison_figure = plt.figure(figsize=(12, 5))
        self.comparison_canvas = FigureCanvas(self.comparison_figure)
        chart_layout.addWidget(self.comparison_canvas)

        splitter.addWidget(chart_widget)

        layout.addWidget(splitter)

        return tab

    def create_statistics_tab(self):
        """Create the graph statistics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Statistics display
        stats_group = QGroupBox("Graph Statistics")
        stats_layout = QGridLayout()

        self.stats_labels = {}
        stats_info = [
            ("Total Cities:", "total_cities"),
            ("Total Edges:", "total_edges"),
            ("Average Degree:", "avg_degree"),
            ("Total Road Miles:", "total_miles"),
            ("Min Distance:", "min_distance"),
            ("Max Distance:", "max_distance"),
            ("Average Distance:", "avg_distance")
        ]

        for i, (label_text, key) in enumerate(stats_info):
            label = QLabel(label_text)
            value_label = QLabel("N/A")
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.stats_labels[key] = value_label

            stats_layout.addWidget(label, i, 0)
            stats_layout.addWidget(value_label, i, 1)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # City connections
        connections_group = QGroupBox("City Connections")
        connections_layout = QVBoxLayout()

        self.city_list = QListWidget()
        connections_layout.addWidget(self.city_list)

        connections_group.setLayout(connections_layout)
        layout.addWidget(connections_group)

        layout.addStretch()

        return tab

    def create_settings_tab(self):
        """Create the settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Display Settings
        display_group = QGroupBox("Display Settings")
        display_layout = QVBoxLayout()

        # Node size slider
        node_layout = QHBoxLayout()
        node_layout.addWidget(QLabel("Node Size:"))
        self.node_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.node_size_slider.setRange(10, 100)
        self.node_size_slider.setValue(50)
        self.node_size_label = QLabel("50")
        self.node_size_slider.valueChanged.connect(
            lambda v: self.node_size_label.setText(str(v))
        )
        node_layout.addWidget(self.node_size_slider)
        node_layout.addWidget(self.node_size_label)
        display_layout.addLayout(node_layout)

        # Edge width slider
        edge_layout = QHBoxLayout()
        edge_layout.addWidget(QLabel("Edge Width:"))
        self.edge_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.edge_width_slider.setRange(1, 10)
        self.edge_width_slider.setValue(2)
        self.edge_width_label = QLabel("2")
        self.edge_width_slider.valueChanged.connect(
            lambda v: self.edge_width_label.setText(str(v))
        )
        edge_layout.addWidget(self.edge_width_slider)
        edge_layout.addWidget(self.edge_width_label)
        display_layout.addLayout(edge_layout)

        display_group.setLayout(display_layout)
        layout.addWidget(display_group)

        # Performance Settings
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QVBoxLayout()

        # Max nodes spinbox
        nodes_layout = QHBoxLayout()
        nodes_layout.addWidget(QLabel("Max Nodes to Expand:"))
        self.max_nodes_spinbox = QSpinBox()
        self.max_nodes_spinbox.setRange(100, 100000)
        self.max_nodes_spinbox.setValue(10000)
        self.max_nodes_spinbox.setSuffix(" nodes")
        nodes_layout.addWidget(self.max_nodes_spinbox)
        perf_layout.addLayout(nodes_layout)

        # Timeout spinbox
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Algorithm Timeout:"))
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(1, 300)
        self.timeout_spinbox.setValue(30)
        self.timeout_spinbox.setSuffix(" seconds")
        timeout_layout.addWidget(self.timeout_spinbox)
        perf_layout.addLayout(timeout_layout)

        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)

        # Export Settings
        export_group = QGroupBox("Export Settings")
        export_layout = QVBoxLayout()

        export_path_layout = QHBoxLayout()
        self.export_path_label = QLabel("Export Path: [Not Set]")
        export_path_layout.addWidget(self.export_path_label)

        self.export_path_button = QPushButton("Choose Path")
        self.export_path_button.clicked.connect(self.choose_export_path)
        export_path_layout.addWidget(self.export_path_button)

        export_layout.addLayout(export_path_layout)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        layout.addStretch()

        return tab

    def load_data(self):
        """Load graph data and initialize components"""
        try:
            # Locate CSVs
            here = Path(__file__).resolve()
            project_root = None
            for up in [here, *here.parents]:
                if (up / "data" / "cities.csv").exists() and (up / "data" / "edges.csv").exists():
                    project_root = up
                    break
            if project_root is None:
                project_root = here.parents[1]

            cities_csv = project_root / "data" / "cities.csv"
            edges_csv = project_root / "data" / "edges.csv"

            # Load graph
            self.graph = load_graph(cities_csv, edges_csv)

            # Planner + visualizer
            self.route_planner = RoutePlanner(self.graph)
            self.visualizer = GraphVisualizer(self.graph, self.graph_figure)

            # Populate city combos
            cities = sorted(self.graph.get_all_cities())
            for cb in (self.start_combo, self.goal_combo, self.comp_start_combo, self.comp_goal_combo):
                cb.clear()
                cb.addItems(cities)

            # Sensible defaults
            if "Rochester" in cities:
                self.start_combo.setCurrentText("Rochester")
                self.comp_start_combo.setCurrentText("Rochester")
            if "Buffalo" in cities:
                self.goal_combo.setCurrentText("Buffalo")
                self.comp_goal_combo.setCurrentText("Buffalo")

            # Update statistics panel
            self.update_statistics()

            # City list with connection counts
            self.city_list.clear()
            for city in cities:
                connections = len(self.graph.get_neighbors(city))
                self.city_list.addItem(f"{city} ({connections} connections)")

            # Draw the graph
            self.refresh_graph()
            self.statusBar.showMessage("Data loaded successfully")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")
            self.statusBar.showMessage("Failed to load data")

    def run_single_search(self):
        """Run a single algorithm search - HARDCODED TO DFS FOR TESTING"""

        # FIRST: Check if self.worker already exists and what it is
        print(f"\n[DEBUG] === INITIAL STATE CHECK ===")
        if hasattr(self, 'worker'):
            print(f"[DEBUG] self.worker already exists!")
            print(f"[DEBUG] Existing self.worker = {self.worker}")
            print(f"[DEBUG] Existing self.worker type = {type(self.worker)}")
            print(f"[DEBUG] Is existing self.worker a string? {isinstance(self.worker, str)}")
        else:
            print(f"[DEBUG] self.worker does not exist yet")
        print(f"[DEBUG] === END INITIAL CHECK ===\n")

        start = self.start_combo.currentText()
        goal = self.goal_combo.currentText()

        if not start or not goal:
            QMessageBox.warning(self, "Warning", "Please select start and goal cities")
            return

        # ===== TESTING MODE: HARDCODED TO DFS =====
        # Ignore the dropdown for now and always use DFS
        algorithm_class = DFS
        algorithm_name = "DFS (Testing Mode)"

        print(f"\n{'='*60}")
        print(f"[DEBUG] Starting search with hardcoded algorithm")
        print(f"[DEBUG] Algorithm class: {algorithm_class}")
        print(f"[DEBUG] Algorithm class type: {type(algorithm_class)}")
        print(f"[DEBUG] Is algorithm_class a string? {isinstance(algorithm_class, str)}")
        print(f"[DEBUG] Algorithm name: {algorithm_name}")
        print(f"[DEBUG] Start: {start}, Goal: {goal}")
        print(f"[DEBUG] Graph object: {self.graph}")
        print(f"[DEBUG] Graph type: {type(self.graph)}")
        print(f"{'='*60}\n")
        # ===========================================

        try:
            self.statusBar.showMessage(f"Running {algorithm_name}...")

            # CRITICAL DEBUG: Check types BEFORE creating worker
            print(f"[DEBUG] About to create AlgorithmWorker...")
            print(f"[DEBUG] AlgorithmWorker class: {AlgorithmWorker}")
            print(f"[DEBUG] AlgorithmWorker type: {type(AlgorithmWorker)}")
            print(f"[DEBUG] Is AlgorithmWorker a string? {isinstance(AlgorithmWorker, str)}")

            # Create worker thread with algorithm CLASS, not string
            # Using start_city and goal_city to avoid collision with QThread.start()
            worker_result = AlgorithmWorker(
                self.graph,          # Pass graph directly
                algorithm_class,     # Pass DFS class
                algorithm_name,      # Pass name for display
                start,               # start_city parameter
                goal                 # goal_city parameter
            )

            # CRITICAL DEBUG: Check what we got back
            print(f"\n[DEBUG] Worker created!")
            print(f"[DEBUG] worker_result = {worker_result}")
            print(f"[DEBUG] worker_result type = {type(worker_result)}")
            print(f"[DEBUG] Is worker_result a string? {isinstance(worker_result, str)}")
            print(f"[DEBUG] worker_result has 'start' method? {hasattr(worker_result, 'start')}")
            if hasattr(worker_result, 'start'):
                print(f"[DEBUG] worker_result.start = {worker_result.start}")
                print(f"[DEBUG] worker_result.start type = {type(worker_result.start)}")
                print(f"[DEBUG] Is worker_result.start a string? {isinstance(worker_result.start, str)}")

            # Now assign to self.worker
            self.worker = worker_result

            print(f"\n[DEBUG] After assignment:")
            print(f"[DEBUG] self.worker = {self.worker}")
            print(f"[DEBUG] self.worker type = {type(self.worker)}")
            print(f"[DEBUG] Is self.worker a string? {isinstance(self.worker, str)}")
            print(f"[DEBUG] self.worker.start = {self.worker.start}")
            print(f"[DEBUG] self.worker.start type = {type(self.worker.start)}")
            print(f"[DEBUG] Is self.worker.start a string? {isinstance(self.worker.start, str)}")

            # Connect signals
            print(f"\n[DEBUG] Connecting signals...")
            self.worker.progress.connect(self.statusBar.showMessage)
            self.worker.result.connect(self.display_result)
            self.worker.error.connect(lambda msg: QMessageBox.critical(self, "Error", msg))
            self.worker.finished.connect(lambda: self.statusBar.showMessage("Search complete"))
            print(f"[DEBUG] Signals connected successfully")

            # Check one more time before starting
            print(f"\n[DEBUG] Final check before start():")
            print(f"[DEBUG] self.worker.start callable? {callable(self.worker.start)}")
            print(f"[DEBUG] About to call self.worker.start()...")

            self.worker.start()

            print(f"[DEBUG] self.worker.start() called successfully!")

        except Exception as e:
            import traceback
            error_msg = f"Search failed: {str(e)}\n{traceback.format_exc()}"
            print(f"\n[DEBUG] Exception in run_single_search:")
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def display_result(self, result):
        """Display search result"""
        self.current_results.append(result)

        # Update results text
        result_text = f"\n{'='*50}\n"
        result_text += f"Algorithm: {result.algorithm_name}\n"
        result_text += f"Start: {result.start} | Goal: {result.goal}\n"
        result_text += f"Path: {' -> '.join(result.path)}\n"
        result_text += f"Cost: {result.cost:.1f} miles\n"
        result_text += f"Nodes Expanded: {result.nodes_expanded}\n"
        result_text += f"Runtime: {result.runtime*1000:.3f} ms\n"
        result_text += f"Optimal: {'Yes' if result.is_optimal else 'No'}\n"

        self.results_text.append(result_text)

        # Update visualization - simplified approach without draw_search_result
        # Just refresh the graph with the path information shown in a different way
        if self.visualizer:
            try:
                # Clear and redraw the graph
                self.visualizer.figure = self.graph_figure
                self.visualizer.ax = self.graph_figure.clear()
                self.visualizer.ax = self.graph_figure.add_subplot(111)

                # Draw the base graph
                self.visualizer.draw_graph(
                    show_weights=self.show_weights_checkbox.isChecked(),
                    title=f"Route: {result.start} → {result.goal} ({result.algorithm_name})"
                )

                # If show_path is checked, manually highlight the path
                if self.show_path_checkbox.isChecked() and result.path and len(result.path) > 1:
                    # Get positions of cities in the path
                    path_positions = []
                    for city in result.path:
                        if hasattr(self.graph.cities[city], 'latitude') and hasattr(self.graph.cities[city], 'longitude'):
                            lon = self.graph.cities[city].longitude
                            lat = self.graph.cities[city].latitude
                            path_positions.append((lon, lat))

                    # Draw the path as a thick red line
                    if len(path_positions) >= 2:
                        lons = [pos[0] for pos in path_positions]
                        lats = [pos[1] for pos in path_positions]
                        self.visualizer.ax.plot(lons, lats, 'r-', linewidth=3, label='Path', zorder=5)

                        # Mark start and goal
                        self.visualizer.ax.plot(lons[0], lats[0], 'go', markersize=12, label='Start', zorder=6)
                        self.visualizer.ax.plot(lons[-1], lats[-1], 'bs', markersize=12, label='Goal', zorder=6)
                        self.visualizer.ax.legend()

                self.graph_canvas.draw()

            except Exception as e:
                print(f"[DEBUG] Visualization error: {e}")
                # If visualization fails, just refresh the graph normally
                self.refresh_graph()

    def run_comparison(self):
        """Run algorithm comparison"""
        start = self.comp_start_combo.currentText()
        goal = self.comp_goal_combo.currentText()

        if not start or not goal:
            QMessageBox.warning(self, "Warning", "Please select start and goal cities")
            return

        # Get selected algorithms
        selected_algos = [
            algo for algo, checkbox in self.algo_checkboxes.items()
            if checkbox.isChecked()
        ]

        if not selected_algos:
            QMessageBox.warning(self, "Warning", "Please select at least one algorithm")
            return

        try:
            self.statusBar.showMessage("Running comparison...")

            # Run comparison
            parallel = self.parallel_checkbox.isChecked()
            comparison = self.route_planner.run_comparison(
                start, goal, selected_algos, parallel
            )

            self.comparison_result = comparison

            # Update table
            self.comparison_table.setRowCount(len(comparison.results))
            for i, result in enumerate(comparison.results):
                self.comparison_table.setItem(i, 0, QTableWidgetItem(result.algorithm_name))
                self.comparison_table.setItem(i, 1, QTableWidgetItem(str(len(result.path))))
                self.comparison_table.setItem(i, 2, QTableWidgetItem(f"{result.cost:.1f}"))
                self.comparison_table.setItem(i, 3, QTableWidgetItem(str(result.nodes_expanded)))
                self.comparison_table.setItem(i, 4, QTableWidgetItem(f"{result.runtime*1000:.3f}"))

                optimal_text = "Yes" if result.is_optimal else "No"
                optimal_item = QTableWidgetItem(optimal_text)
                if result.is_optimal:
                    optimal_item.setBackground(QColor(200, 255, 200))
                else:
                    optimal_item.setBackground(QColor(255, 200, 200))
                self.comparison_table.setItem(i, 5, optimal_item)

            # Update comparison charts
            self.comparison_figure.clear()
            comparison_fig = self.visualizer.create_comparison_chart(comparison.results)

            # Copy the comparison chart to our canvas
            for ax_src in comparison_fig.axes:
                ax_dest = self.comparison_figure.add_subplot(
                    1, 3, comparison_fig.axes.index(ax_src) + 1
                )
                # Copy the content
                for line in ax_src.lines:
                    ax_dest.plot(line.get_xdata(), line.get_ydata())
                for bar_container in ax_src.containers:
                    heights = [bar.get_height() for bar in bar_container]
                    positions = [bar.get_x() for bar in bar_container]
                    colors = [bar.get_facecolor() for bar in bar_container]
                    ax_dest.bar(range(len(heights)), heights, color=colors[0])

                ax_dest.set_title(ax_src.get_title())
                ax_dest.set_xlabel(ax_src.get_xlabel())
                ax_dest.set_ylabel(ax_src.get_ylabel())
                ax_dest.set_xticklabels([r.algorithm_name for r in comparison.results])
                ax_dest.grid(True, alpha=0.3)

            self.comparison_figure.suptitle(
                f'Algorithm Comparison: {start} to {goal}',
                fontsize=14,
                fontweight='bold'
            )
            self.comparison_figure.tight_layout(rect=[0, 0, 1, 0.96])
            self.comparison_canvas.draw()

            # Update status
            optimal_str = ", ".join(comparison.optimal_algorithms)
            self.statusBar.showMessage(
                f"Comparison complete. Optimal: {optimal_str} | "
                f"Fastest: {comparison.fastest_algorithm} | "
                f"Least Expanded: {comparison.least_expanded_algorithm}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Comparison failed: {str(e)}")
            self.statusBar.showMessage("Comparison failed")

    def refresh_graph(self):
        """Refresh the graph visualization"""
        if self.visualizer:
            self.visualizer.figure = self.graph_figure
            self.visualizer.ax = self.graph_figure.clear()
            self.visualizer.ax = self.graph_figure.add_subplot(111)
            self.visualizer.draw_graph(
                show_weights=self.show_weights_checkbox.isChecked(),
                title="New York State Route Network"
            )
            self.graph_canvas.draw()

    def update_statistics(self):
        """Update graph statistics display"""
        if self.graph:
            stats = get_graph_statistics(self.graph)

            self.stats_labels["total_cities"].setText(str(stats['total_cities']))
            self.stats_labels["total_edges"].setText(str(stats['total_edges']))
            self.stats_labels["avg_degree"].setText(f"{stats['average_degree']:.2f}")
            self.stats_labels["total_miles"].setText(f"{stats['total_road_miles']:.1f}")
            self.stats_labels["min_distance"].setText(f"{stats['min_distance']:.1f}")
            self.stats_labels["max_distance"].setText(f"{stats['max_distance']:.1f}")
            self.stats_labels["avg_distance"].setText(f"{stats['avg_distance']:.1f}")

    def clear_results(self):
        """Clear all results"""
        self.results_text.clear()
        self.comparison_table.setRowCount(0)
        self.refresh_graph()
        self.statusBar.showMessage("Results cleared")

    def export_results(self):
        """Export results to file"""
        if not self.comparison_result:
            QMessageBox.warning(self, "Warning", "No results to export")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "", "JSON Files (*.json);;CSV Files (*.csv)"
        )

        if filename:
            try:
                if filename.endswith('.json'):
                    # Export as JSON
                    data = {
                        'start': self.comparison_result.start,
                        'goal': self.comparison_result.goal,
                        'results': [
                            {
                                'algorithm': r.algorithm_name,
                                'path': r.path,
                                'cost': r.cost,
                                'nodes_expanded': r.nodes_expanded,
                                'runtime': r.runtime,
                                'optimal': r.is_optimal
                            }
                            for r in self.comparison_result.results
                        ],
                        'optimal_algorithms': self.comparison_result.optimal_algorithms,
                        'fastest': self.comparison_result.fastest_algorithm,
                        'least_expanded': self.comparison_result.least_expanded_algorithm
                    }

                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)

                elif filename.endswith('.csv'):
                    # Export as CSV
                    import csv
                    with open(filename, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            'Algorithm', 'Path', 'Cost', 'Nodes Expanded',
                            'Runtime (ms)', 'Optimal'
                        ])
                        for r in self.comparison_result.results:
                            writer.writerow([
                                r.algorithm_name,
                                ' -> '.join(r.path),
                                r.cost,
                                r.nodes_expanded,
                                r.runtime * 1000,
                                r.is_optimal
                            ])

                QMessageBox.information(self, "Success", f"Results exported to {filename}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    def choose_export_path(self):
        """Choose export directory"""
        directory = QFileDialog.getExistingDirectory(self, "Choose Export Directory")
        if directory:
            self.export_path_label.setText(f"Export Path: {directory}")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About NY Route Planner",
            "New York State Route Planner\n\n"
            "A comprehensive route finding application implementing:\n"
            "• DFS (Depth-First Search)\n"
            "• BFS (Breadth-First Search)\n"
            "• UCS (Uniform Cost Search)\n"
            "• Greedy Best-First Search\n"
            "• A* Search\n\n"
            "CSCI Project 3 - Group 6\n"
            "Version 1.0"
        )


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look

    # Set application icon if available
    # app.setWindowIcon(QIcon('icon.png'))

    gui = RouteFinderGUI()
    gui.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()