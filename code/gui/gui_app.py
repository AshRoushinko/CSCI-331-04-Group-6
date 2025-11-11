"""
NY Route Planner GUI Application
A comprehensive PyQt5 interface for the route planning system
"""

import sys
import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

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
import matplotlib.pyplot as plt

# Import project modules
from route_planner import RoutePlanner, ComparisonResult
from data_loader import load_graph, get_graph_statistics
from visualizer import GraphVisualizer
from graph import Graph


class AlgorithmWorker(QThread):
    """Worker thread for running algorithms without blocking GUI"""
    progress = pyqtSignal(str)  # Algorithm name
    result = pyqtSignal(object)  # SearchResult
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
            self.error.emit(f"Error in {self.algorithm}: {str(e)}")
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

        # Route selection group
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

        # Algorithm selection group
        algo_group = QGroupBox("Algorithm Selection")
        algo_layout = QVBoxLayout()

        self.algo_radio_buttons = {}
        self.algo_button_group = QButtonGroup()

        algorithms = ["DFS", "BFS", "UCS", "Greedy", "A*"]
        for algo in algorithms:
            radio = QRadioButton(algo)
            self.algo_radio_buttons[algo] = radio
            self.algo_button_group.addButton(radio)
            algo_layout.addWidget(radio)

        # Select A* by default
        self.algo_radio_buttons["A*"].setChecked(True)

        algo_group.setLayout(algo_layout)
        left_layout.addWidget(algo_group)

        # Control buttons
        button_layout = QHBoxLayout()

        self.run_button = QPushButton("Run Search")
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

        # Results display
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

        # Graph canvas
        self.graph_figure = plt.Figure(figsize=(10, 8))
        self.graph_canvas = FigureCanvas(self.graph_figure)
        self.graph_toolbar = NavigationToolbar(self.graph_canvas, self)

        right_layout.addWidget(self.graph_toolbar)
        right_layout.addWidget(self.graph_canvas)

        # Add panels to main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 1050])

        layout.addWidget(splitter)

        return tab

    def create_comparison_tab(self):
        """Create the algorithm comparison tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        control_panel.setMaximumHeight(100)

        control_layout.addWidget(QLabel("Start:"))
        self.comp_start_combo = QComboBox()
        control_layout.addWidget(self.comp_start_combo)

        control_layout.addWidget(QLabel("Goal:"))
        self.comp_goal_combo = QComboBox()
        control_layout.addWidget(self.comp_goal_combo)

        # Algorithm checkboxes
        algo_select_group = QGroupBox("Select Algorithms")
        algo_select_layout = QHBoxLayout()

        self.algo_checkboxes = {}
        for algo in ["DFS", "BFS", "UCS", "Greedy", "A*"]:
            checkbox = QCheckBox(algo)
            checkbox.setChecked(True)
            self.algo_checkboxes[algo] = checkbox
            algo_select_layout.addWidget(checkbox)

        algo_select_group.setLayout(algo_select_layout)
        control_layout.addWidget(algo_select_group)

        self.compare_button = QPushButton("Run Comparison")
        self.compare_button.clicked.connect(self.run_comparison)
        control_layout.addWidget(self.compare_button)

        control_layout.addStretch()

        layout.addWidget(control_panel)

        # Results table
        self.comparison_table = QTableWidget()
        self.comparison_table.setColumnCount(6)
        self.comparison_table.setHorizontalHeaderLabels([
            "Algorithm", "Path Length", "Path Cost (miles)",
            "Nodes Expanded", "Runtime (ms)", "Optimal"
        ])
        self.comparison_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.comparison_table)

        # Comparison charts
        self.comparison_figure = plt.Figure(figsize=(12, 6))
        self.comparison_canvas = FigureCanvas(self.comparison_figure)
        layout.addWidget(self.comparison_canvas)

        return tab

    def create_statistics_tab(self):
        """Create the graph statistics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Statistics display
        stats_group = QGroupBox("Graph Statistics")
        stats_layout = QGridLayout()

        self.stats_labels = {}
        stats_items = [
            ("Total Cities:", "total_cities"),
            ("Total Edges:", "total_edges"),
            ("Average Degree:", "avg_degree"),
            ("Total Road Miles:", "total_miles"),
            ("Min Distance:", "min_distance"),
            ("Max Distance:", "max_distance"),
            ("Average Distance:", "avg_distance")
        ]

        for i, (label, key) in enumerate(stats_items):
            stats_layout.addWidget(QLabel(label), i, 0)
            value_label = QLabel("0")
            self.stats_labels[key] = value_label
            stats_layout.addWidget(value_label, i, 1)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # City list
        city_group = QGroupBox("Cities in Graph")
        city_layout = QVBoxLayout()

        self.city_list = QListWidget()
        city_layout.addWidget(self.city_list)

        city_group.setLayout(city_layout)
        layout.addWidget(city_group)

        # Refresh button
        refresh_button = QPushButton("Refresh Statistics")
        refresh_button.clicked.connect(self.update_statistics)
        layout.addWidget(refresh_button)

        layout.addStretch()

        return tab

    def create_settings_tab(self):
        """Create the settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Display settings
        display_group = QGroupBox("Display Settings")
        display_layout = QVBoxLayout()

        self.show_weights_checkbox = QCheckBox("Show Edge Weights")
        self.show_weights_checkbox.setChecked(True)
        display_layout.addWidget(self.show_weights_checkbox)

        self.animate_search_checkbox = QCheckBox("Animate Search (Future Feature)")
        self.animate_search_checkbox.setEnabled(False)
        display_layout.addWidget(self.animate_search_checkbox)

        display_group.setLayout(display_layout)
        layout.addWidget(display_group)

        # Performance settings
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QVBoxLayout()

        self.parallel_checkbox = QCheckBox("Run Algorithms in Parallel")
        self.parallel_checkbox.setChecked(False)
        perf_layout.addWidget(self.parallel_checkbox)

        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)

        # Export settings
        export_group = QGroupBox("Export Settings")
        export_layout = QVBoxLayout()

        self.export_path_label = QLabel("Export Path: ./results/")
        export_layout.addWidget(self.export_path_label)

        choose_path_button = QPushButton("Choose Export Path")
        choose_path_button.clicked.connect(self.choose_export_path)
        export_layout.addWidget(choose_path_button)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        layout.addStretch()

        return tab

    def load_data(self):
        """Load graph data from CSV files"""
        try:
            # Load graph
            cities_file = Path("/mnt/user-data/uploads/cities.csv")
            edges_file = Path("/mnt/user-data/uploads/edges.csv")

            # Fix the column name issue in data_loader
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

            # Update city list
            self.city_list.addItems(cities)

            # Initial graph display
            self.refresh_graph()

            # Update statistics
            self.update_statistics()

            self.statusBar.showMessage("Data loaded successfully")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")

    def load_graph_with_fix(self, cities_file, edges_file):
        """Load graph with fixed column names"""
        graph = Graph()

        # Load cities (handle column name variations)
        import csv
        with open(cities_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Handle both 'city' and 'city_name' columns
                city_name = row.get('city', row.get('city_name', '')).strip()
                lat = float(row.get('latitude', row.get('latitude ', '')).strip())
                lon = float(row.get('longitude', row.get('longitude', '')).strip())
                graph.add_city(city_name, lat, lon)

        # Load edges (handle column name variations)
        with open(edges_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                city1 = row['city1'].strip()
                city2 = row['city2'].strip()
                # Handle both 'distance' and 'distance_miles' columns
                distance = float(row.get('distance', row.get('distance_miles', '')).strip())
                graph.add_edge(city1, city2, distance, bidirectional=True)

        return graph

    def run_single_search(self):
        """Run a single search algorithm"""
        # Get selected algorithm
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

        try:
            # Run algorithm
            self.statusBar.showMessage(f"Running {selected_algo}...")
            result = self.route_planner.run_single_algorithm(selected_algo, start, goal)

            # Display results
            self.results_text.clear()
            self.results_text.append(f"Algorithm: {result.algorithm_name}\n")
            self.results_text.append(f"Start: {start}\n")
            self.results_text.append(f"Goal: {goal}\n")
            self.results_text.append("-" * 40 + "\n")
            self.results_text.append(f"Path Found: {' → '.join(result.path)}\n")
            self.results_text.append(f"Total Distance: {result.cost:.1f} miles\n")
            self.results_text.append(f"Nodes Expanded: {result.nodes_expanded}\n")
            self.results_text.append(f"Runtime: {result.runtime * 1000:.3f} ms\n")
            self.results_text.append(f"Optimal: {'Yes' if result.is_optimal else 'No'}\n")

            # Update visualization
            self.visualizer.figure = self.graph_figure
            self.visualizer.ax = self.graph_figure.clear()
            self.visualizer.ax = self.graph_figure.add_subplot(111)

            # Highlight the path
            node_colors = {start: '#ff6b6b', goal: '#51cf66'}
            self.visualizer.draw_graph(
                highlight_path=result.path,
                show_weights=self.show_weights_checkbox.isChecked(),
                node_colors=node_colors,
                title=f"{selected_algo} Path from {start} to {goal}"
            )

            self.graph_canvas.draw()

            self.statusBar.showMessage(f"Search completed: {result.cost:.1f} miles")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")
            self.statusBar.showMessage("Search failed")

    def run_comparison(self):
        """Run comparison of multiple algorithms"""
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
                self.comparison_table.setItem(i, 4, QTableWidgetItem(f"{result.runtime * 1000:.3f}"))

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

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()