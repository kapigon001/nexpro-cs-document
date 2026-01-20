"""Chart Agent - Data visualization and chart generation"""
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import io
import tempfile
from .base_agent import BaseAgent
from ..core.task import Task

# Try to import visualization libraries
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# Configure Japanese font
if HAS_MATPLOTLIB:
    plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False


class ChartAgent(BaseAgent):
    """
    Chart Agent: Creates charts and visualizations for presentations.

    Responsibilities:
    - Generate bar charts, line charts, pie charts
    - Create comparison charts
    - Build data tables
    - Export charts as images for PowerPoint
    """

    def __init__(self, output_dir: str = "output/charts"):
        super().__init__(
            name="ChartAgent",
            role="Data Visualization",
            description="Creates charts and visualizations for presentations"
        )
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chart_counter = 0

        if not HAS_MATPLOTLIB:
            self.log("matplotlib not available - chart generation limited", "yellow")

    async def execute_task(self, task: Task) -> Any:
        """Execute chart-related tasks"""
        task_type = task.input_data.get("type", "create_chart") if task.input_data else "create_chart"

        if task_type == "create_chart":
            return await self._create_chart(task.input_data)
        elif task_type == "create_bar_chart":
            return await self._create_bar_chart(task.input_data)
        elif task_type == "create_line_chart":
            return await self._create_line_chart(task.input_data)
        elif task_type == "create_pie_chart":
            return await self._create_pie_chart(task.input_data)
        elif task_type == "create_comparison_chart":
            return await self._create_comparison_chart(task.input_data)
        elif task_type == "create_table_image":
            return await self._create_table_image(task.input_data)
        elif task_type == "analyze_and_visualize":
            return await self._analyze_and_visualize(task.input_data)
        else:
            return await self._create_chart(task.input_data)

    def _get_chart_path(self, name: str = None) -> Path:
        """Generate unique chart file path"""
        self.chart_counter += 1
        filename = f"{name or 'chart'}_{self.chart_counter}.png"
        return self.output_dir / filename

    def _apply_style(self, fig, ax, title: str = "", colors: List[str] = None):
        """Apply consistent styling to charts"""
        if colors is None:
            colors = ['#1F4E79', '#2E75B6', '#5B9BD5', '#9DC3E6', '#BDD7EE']

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        fig.tight_layout()
        return colors

    async def _create_chart(self, input_data: Dict) -> Dict:
        """Create chart based on chart_type"""
        chart_type = input_data.get("chart_type", "bar")

        if chart_type == "bar":
            return await self._create_bar_chart(input_data)
        elif chart_type == "line":
            return await self._create_line_chart(input_data)
        elif chart_type == "pie":
            return await self._create_pie_chart(input_data)
        elif chart_type == "comparison":
            return await self._create_comparison_chart(input_data)
        else:
            return await self._create_bar_chart(input_data)

    async def _create_bar_chart(self, input_data: Dict) -> Dict:
        """Create a bar chart"""
        if not HAS_MATPLOTLIB:
            return {"success": False, "error": "matplotlib not available"}

        self.log("Creating bar chart...")

        data = input_data.get("data", {})
        title = input_data.get("title", "Bar Chart")
        xlabel = input_data.get("xlabel", "")
        ylabel = input_data.get("ylabel", "")
        colors = input_data.get("colors", ['#1F4E79', '#2E75B6', '#5B9BD5'])
        horizontal = input_data.get("horizontal", False)

        labels = list(data.keys())
        values = list(data.values())

        fig, ax = plt.subplots(figsize=(10, 6))

        if horizontal:
            bars = ax.barh(labels, values, color=colors[0])
            ax.set_xlabel(ylabel)
            ax.set_ylabel(xlabel)
        else:
            bars = ax.bar(labels, values, color=colors[0])
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)

        self._apply_style(fig, ax, title, colors)

        # Add value labels
        for bar, value in zip(bars, values):
            if horizontal:
                ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                       f'{value}', va='center', fontsize=10)
            else:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                       f'{value}', ha='center', fontsize=10)

        chart_path = self._get_chart_path("bar")
        fig.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        self.log(f"Bar chart saved: {chart_path}")
        return {"success": True, "path": str(chart_path), "type": "bar"}

    async def _create_line_chart(self, input_data: Dict) -> Dict:
        """Create a line chart"""
        if not HAS_MATPLOTLIB:
            return {"success": False, "error": "matplotlib not available"}

        self.log("Creating line chart...")

        data = input_data.get("data", {})
        title = input_data.get("title", "Line Chart")
        xlabel = input_data.get("xlabel", "")
        ylabel = input_data.get("ylabel", "")
        colors = input_data.get("colors", ['#1F4E79', '#2E75B6', '#5B9BD5', '#9DC3E6'])

        fig, ax = plt.subplots(figsize=(10, 6))

        # Support multiple lines
        if isinstance(list(data.values())[0], dict):
            # Multiple series
            for i, (series_name, series_data) in enumerate(data.items()):
                x = list(series_data.keys())
                y = list(series_data.values())
                color = colors[i % len(colors)]
                ax.plot(x, y, marker='o', linewidth=2, label=series_name, color=color)
            ax.legend()
        else:
            # Single series
            x = list(data.keys())
            y = list(data.values())
            ax.plot(x, y, marker='o', linewidth=2, color=colors[0])

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        self._apply_style(fig, ax, title, colors)
        ax.grid(True, linestyle='--', alpha=0.7)

        chart_path = self._get_chart_path("line")
        fig.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        self.log(f"Line chart saved: {chart_path}")
        return {"success": True, "path": str(chart_path), "type": "line"}

    async def _create_pie_chart(self, input_data: Dict) -> Dict:
        """Create a pie chart"""
        if not HAS_MATPLOTLIB:
            return {"success": False, "error": "matplotlib not available"}

        self.log("Creating pie chart...")

        data = input_data.get("data", {})
        title = input_data.get("title", "Pie Chart")
        colors = input_data.get("colors", ['#1F4E79', '#2E75B6', '#5B9BD5', '#9DC3E6', '#BDD7EE'])
        show_percentage = input_data.get("show_percentage", True)

        labels = list(data.keys())
        values = list(data.values())

        fig, ax = plt.subplots(figsize=(10, 8))

        def autopct_func(pct):
            return f'{pct:.1f}%' if show_percentage else ''

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=colors[:len(labels)],
            autopct=autopct_func,
            startangle=90,
            explode=[0.02] * len(labels)
        )

        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        chart_path = self._get_chart_path("pie")
        fig.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        self.log(f"Pie chart saved: {chart_path}")
        return {"success": True, "path": str(chart_path), "type": "pie"}

    async def _create_comparison_chart(self, input_data: Dict) -> Dict:
        """Create a comparison chart (grouped bar chart)"""
        if not HAS_MATPLOTLIB:
            return {"success": False, "error": "matplotlib not available"}

        self.log("Creating comparison chart...")

        data = input_data.get("data", {})
        title = input_data.get("title", "Comparison")
        xlabel = input_data.get("xlabel", "")
        ylabel = input_data.get("ylabel", "")
        colors = input_data.get("colors", ['#1F4E79', '#5B9BD5', '#ED7D31', '#70AD47'])

        # data format: {"Category1": {"A": 10, "B": 20}, "Category2": {"A": 15, "B": 25}}
        categories = list(data.keys())
        if not categories:
            return {"success": False, "error": "No data provided"}

        groups = list(data[categories[0]].keys())
        n_groups = len(groups)
        n_categories = len(categories)

        fig, ax = plt.subplots(figsize=(12, 6))

        import numpy as np
        x = np.arange(n_groups)
        width = 0.8 / n_categories

        for i, category in enumerate(categories):
            values = [data[category].get(g, 0) for g in groups]
            offset = (i - n_categories/2 + 0.5) * width
            bars = ax.bar(x + offset, values, width, label=category, color=colors[i % len(colors)])

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_xticks(x)
        ax.set_xticklabels(groups)
        ax.legend()

        self._apply_style(fig, ax, title, colors)

        chart_path = self._get_chart_path("comparison")
        fig.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        self.log(f"Comparison chart saved: {chart_path}")
        return {"success": True, "path": str(chart_path), "type": "comparison"}

    async def _create_table_image(self, input_data: Dict) -> Dict:
        """Create a table as an image"""
        if not HAS_MATPLOTLIB or not HAS_PANDAS:
            return {"success": False, "error": "matplotlib or pandas not available"}

        self.log("Creating table image...")

        data = input_data.get("data", {})
        title = input_data.get("title", "")
        header_color = input_data.get("header_color", "#1F4E79")
        row_colors = input_data.get("row_colors", ["#FFFFFF", "#F2F2F2"])

        df = pd.DataFrame(data)

        fig, ax = plt.subplots(figsize=(12, len(df) * 0.5 + 2))
        ax.axis('off')

        if title:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        table = ax.table(
            cellText=df.values,
            colLabels=df.columns,
            cellLoc='center',
            loc='center'
        )

        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)

        # Style header
        for j, col in enumerate(df.columns):
            cell = table[(0, j)]
            cell.set_facecolor(header_color)
            cell.set_text_props(color='white', fontweight='bold')

        # Style rows
        for i in range(len(df)):
            for j in range(len(df.columns)):
                cell = table[(i + 1, j)]
                cell.set_facecolor(row_colors[i % len(row_colors)])

        chart_path = self._get_chart_path("table")
        fig.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        self.log(f"Table image saved: {chart_path}")
        return {"success": True, "path": str(chart_path), "type": "table"}

    async def _analyze_and_visualize(self, input_data: Dict) -> Dict:
        """Analyze data and create appropriate visualizations"""
        data = input_data.get("data", {})
        analysis_type = input_data.get("analysis_type", "auto")

        self.log("Analyzing data for visualization...")

        charts = []

        if not data:
            return {"success": False, "error": "No data provided", "charts": []}

        # Auto-detect best visualization
        if isinstance(data, dict):
            first_value = list(data.values())[0] if data else None

            if isinstance(first_value, dict):
                # Nested dict - comparison chart
                result = await self._create_comparison_chart({
                    "data": data,
                    "title": input_data.get("title", "Comparison Analysis")
                })
                charts.append(result)

            elif isinstance(first_value, (int, float)):
                # Simple dict - bar or pie chart
                if len(data) <= 6:
                    result = await self._create_pie_chart({
                        "data": data,
                        "title": input_data.get("title", "Distribution")
                    })
                    charts.append(result)

                result = await self._create_bar_chart({
                    "data": data,
                    "title": input_data.get("title", "Values"),
                    "horizontal": len(data) > 5
                })
                charts.append(result)

        self.log(f"Created {len(charts)} visualizations")
        return {
            "success": True,
            "charts": charts,
            "count": len(charts)
        }

    def get_chart_for_pptx(self, chart_path: str) -> Optional[bytes]:
        """Get chart image bytes for embedding in PowerPoint"""
        path = Path(chart_path)
        if path.exists():
            return path.read_bytes()
        return None
