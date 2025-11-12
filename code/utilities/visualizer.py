"""
Graph Visualization Module
Provides visualization capabilities for the route planner
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx
import numpy as np
from typing import List, Optional, Dict, Tuple
import math

from code.heartofitall.graph import Graph
from code.heartofitall.search_results import SearchResult


class GraphVisualizer:
    def __init__(self, graph: Graph, figure: Optional["Figure"] = None):
        self.graph = graph
        self.G = self._create_networkx_graph()
        self.pos = {}
        from matplotlib.figure import Figure
        self.figure: Figure = figure or Figure(figsize=(10, 8))
        self.ax = self.figure.add_subplot(111)
        self._setup_positions()

    def _create_networkx_graph(self) -> nx.Graph:
        """Convert our Graph to NetworkX format"""
        G = nx.Graph()

        # Add nodes with position data
        for city_name, city in self.graph.cities.items():
            G.add_node(city_name, pos=(city.longitude, city.latitude))

        # Add edges with weights
        for city_a, neighbors in self.graph.adjacency.items():
            for city_b, distance in neighbors.items():
                if not G.has_edge(city_a, city_b):  # Avoid duplicate edges
                    G.add_edge(city_a, city_b, weight=distance)

        return G

    def _setup_positions(self):
        """Setup node positions based on geographic coordinates"""
        # Use actual lat/lon for positioning
        self.pos = {}
        for city_name, city in self.graph.cities.items():
            # Convert to x,y coordinates (flip lon/lat for standard x,y display)
            self.pos[city_name] = (city.longitude, city.latitude)

    def create_figure(self, figsize: Tuple[int, int] = (14, 10)) -> Figure:
        """Create a matplotlib figure for the graph"""
        self.figure = Figure(figsize=figsize)
        self.ax = self.figure.add_subplot(111)
        return self.figure

    def draw_graph(self,
                   highlight_path: Optional[List[str]] = None,
                   show_weights: bool = True,
                   node_colors: Optional[Dict[str, str]] = None,
                   title: str = "New York State Route Network"):
        """
        Draw the graph with optional path highlighting

        Args:
            highlight_path: Path to highlight in red
            show_weights: Whether to show edge weights
            node_colors: Custom colors for specific nodes
            title: Title for the graph
        """
        if self.ax is None:
            self.create_figure()

        self.ax.clear()

        # Default node colors
        node_color_list = []
        for node in self.G.nodes():
            if node_colors and node in node_colors:
                node_color_list.append(node_colors[node])
            elif node == "Rochester":
                node_color_list.append('#ff6b6b')  # Red for Rochester (start)
            else:
                node_color_list.append('#4ecdc4')  # Teal for other cities

        # Draw all edges first (in gray)
        nx.draw_networkx_edges(self.G, self.pos,
                               edge_color='gray',
                               width=1.5,
                               alpha=0.5,
                               ax=self.ax)

        # Highlight path if provided
        if highlight_path and len(highlight_path) > 1:
            path_edges = [(highlight_path[i], highlight_path[i + 1])
                          for i in range(len(highlight_path) - 1)]
            nx.draw_networkx_edges(self.G, self.pos,
                                   edgelist=path_edges,
                                   edge_color='red',
                                   width=3,
                                   alpha=0.8,
                                   ax=self.ax)

        # Draw nodes
        nx.draw_networkx_nodes(self.G, self.pos,
                               node_color=node_color_list,
                               node_size=500,
                               ax=self.ax)

        # Draw labels
        nx.draw_networkx_labels(self.G, self.pos,
                                font_size=8,
                                font_weight='bold',
                                ax=self.ax)

        # Draw edge weights if requested
        if show_weights:
            edge_labels = nx.get_edge_attributes(self.G, 'weight')
            # Format edge labels to show as integers if they're whole numbers
            edge_labels = {k: int(v) if v == int(v) else f"{v:.1f}"
                           for k, v in edge_labels.items()}
            nx.draw_networkx_edge_labels(self.G, self.pos,
                                         edge_labels=edge_labels,
                                         font_size=7,
                                         ax=self.ax)

        self.ax.set_title(title, fontsize=14, fontweight='bold')
        self.ax.set_xlabel('Longitude', fontsize=10)
        self.ax.set_ylabel('Latitude', fontsize=10)
        self.ax.grid(True, alpha=0.3)

        # Set equal aspect ratio for geographic accuracy
        self.ax.set_aspect('equal', adjustable='box')

        return self.figure

    def create_comparison_chart(self, results: List[SearchResult]) -> Figure:
        """Create bar charts comparing algorithm performance"""
        fig = Figure(figsize=(14, 8))

        # Extract data
        algorithms = [r.algorithm_name for r in results]
        costs = [r.cost for r in results]
        nodes = [r.nodes_expanded for r in results]
        times = [r.runtime * 1000 for r in results]  # Convert to milliseconds

        # Create subplots
        ax1 = fig.add_subplot(131)
        ax2 = fig.add_subplot(132)
        ax3 = fig.add_subplot(133)

        # Color bars based on optimality
        colors = ['green' if r.is_optimal else 'orange' for r in results]

        # Path Cost comparison
        bars1 = ax1.bar(algorithms, costs, color=colors)
        ax1.set_title('Path Cost (miles)', fontweight='bold')
        ax1.set_ylabel('Distance (miles)')
        ax1.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bar, cost in zip(bars1, costs):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                     f'{cost:.1f}', ha='center', va='bottom', fontsize=8)

        # Nodes Expanded comparison
        bars2 = ax2.bar(algorithms, nodes, color=colors)
        ax2.set_title('Nodes Expanded', fontweight='bold')
        ax2.set_ylabel('Number of Nodes')
        ax2.grid(axis='y', alpha=0.3)

        for bar, node_count in zip(bars2, nodes):
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                     str(node_count), ha='center', va='bottom', fontsize=8)

        # Runtime comparison
        bars3 = ax3.bar(algorithms, times, color=colors)
        ax3.set_title('Runtime (milliseconds)', fontweight='bold')
        ax3.set_ylabel('Time (ms)')
        ax3.grid(axis='y', alpha=0.3)

        for bar, time in zip(bars3, times):
            ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                     f'{time:.2f}', ha='center', va='bottom', fontsize=8)

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', label='Optimal'),
            Patch(facecolor='orange', label='Non-optimal')
        ]
        fig.legend(handles=legend_elements, loc='upper right')

        fig.suptitle('Algorithm Performance Comparison', fontsize=14, fontweight='bold')
        fig.tight_layout(rect=[0, 0, 0.95, 0.96])

        return fig

    def animate_search(self, visited_order: List[str], path: List[str],
                       delay: int = 100) -> None:
        """
        Animate the search process (for future implementation)
        Shows nodes being visited and final path
        """
        # This would require integration with the GUI event loop
        # Placeholder for future animation capability
        pass

    def export_graph(self, filename: str, dpi: int = 150):
        """Export the current graph visualization to a file"""
        if self.figure:
            self.figure.savefig(filename, dpi=dpi, bbox_inches='tight')

    @staticmethod
    def calculate_total_distance(path: List[str], graph: Graph) -> float:
        """Calculate total distance for a given path"""
        if len(path) < 2:
            return 0.0

        total = 0.0
        for i in range(len(path) - 1):
            total += graph.get_distance(path[i], path[i + 1])
        return total