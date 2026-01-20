"""Design Agent - Responsible for visual design and layout"""
from typing import Any, Dict, List, Optional
from .base_agent import BaseAgent
from ..core.task import Task


class DesignAgent(BaseAgent):
    """
    Design Agent: Handles visual design and layout decisions.

    Responsibilities:
    - Define color schemes and themes
    - Determine slide layouts
    - Specify font styles and sizes
    - Create visual hierarchy
    - Recommend chart types for data visualization
    """

    # Pre-defined color schemes
    COLOR_SCHEMES = {
        "corporate": {
            "primary": "1F4E79",      # Dark blue
            "secondary": "2E75B6",    # Medium blue
            "accent": "F4B942",       # Gold
            "text": "333333",         # Dark gray
            "background": "FFFFFF",   # White
        },
        "modern": {
            "primary": "2D3436",      # Charcoal
            "secondary": "636E72",    # Gray
            "accent": "00B894",       # Teal
            "text": "2D3436",         # Charcoal
            "background": "FFFFFF",   # White
        },
        "vibrant": {
            "primary": "6C5CE7",      # Purple
            "secondary": "A29BFE",    # Light purple
            "accent": "FD79A8",       # Pink
            "text": "2D3436",         # Charcoal
            "background": "FFFFFF",   # White
        },
    }

    # Layout templates
    LAYOUTS = {
        "title": {
            "title_position": {"x": 0.5, "y": 0.4, "width": 9, "height": 1.5},
            "subtitle_position": {"x": 0.5, "y": 0.6, "width": 9, "height": 0.8},
        },
        "content": {
            "title_position": {"x": 0.5, "y": 0.1, "width": 9, "height": 0.8},
            "body_position": {"x": 0.5, "y": 0.25, "width": 9, "height": 4.5},
        },
        "two_column": {
            "title_position": {"x": 0.5, "y": 0.1, "width": 9, "height": 0.8},
            "left_position": {"x": 0.5, "y": 0.25, "width": 4.2, "height": 4.5},
            "right_position": {"x": 5.0, "y": 0.25, "width": 4.2, "height": 4.5},
        },
        "comparison": {
            "title_position": {"x": 0.5, "y": 0.1, "width": 9, "height": 0.8},
            "left_position": {"x": 0.5, "y": 0.25, "width": 4.2, "height": 4.5},
            "right_position": {"x": 5.0, "y": 0.25, "width": 4.2, "height": 4.5},
        },
    }

    def __init__(self):
        super().__init__(
            name="DesignAgent",
            role="Visual Design & Layout",
            description="Creates visual designs, layouts, and styling for presentations"
        )
        self.current_scheme = "corporate"

    async def execute_task(self, task: Task) -> Any:
        """Execute design-related tasks"""
        task_type = task.input_data.get("type", "create_theme") if task.input_data else "create_theme"

        if task_type == "create_theme":
            return await self._create_theme(task.input_data)
        elif task_type == "design_slide":
            return await self._design_slide(task.input_data)
        elif task_type == "design_presentation":
            return await self._design_presentation(task.input_data)
        elif task_type == "recommend_chart":
            return await self._recommend_chart(task.input_data)
        else:
            return await self._create_theme(task.input_data)

    async def _create_theme(self, input_data: Dict) -> Dict:
        """Create presentation theme"""
        scheme_name = input_data.get("scheme", "corporate")
        custom_colors = input_data.get("custom_colors", {})

        self.log(f"Creating theme: {scheme_name}")

        # Get base scheme
        colors = self.COLOR_SCHEMES.get(scheme_name, self.COLOR_SCHEMES["corporate"]).copy()

        # Apply custom colors if provided
        colors.update(custom_colors)

        theme = {
            "name": scheme_name,
            "colors": colors,
            "fonts": {
                "title": {"name": "Yu Gothic UI", "size": 36, "bold": True},
                "subtitle": {"name": "Yu Gothic UI", "size": 24, "bold": False},
                "heading": {"name": "Yu Gothic UI", "size": 28, "bold": True},
                "body": {"name": "Yu Gothic UI", "size": 18, "bold": False},
                "caption": {"name": "Yu Gothic UI", "size": 12, "bold": False},
            },
            "spacing": {
                "margin": 0.5,  # inches
                "line_spacing": 1.2,
                "paragraph_spacing": 12,  # points
            },
        }

        self.current_scheme = scheme_name
        self.log(f"Theme created with {len(colors)} colors")
        return theme

    async def _design_slide(self, input_data: Dict) -> Dict:
        """Design layout for a single slide"""
        slide_type = input_data.get("slide_type", "content")
        content = input_data.get("content", {})

        self.log(f"Designing slide layout: {slide_type}")

        # Get base layout
        layout = self.LAYOUTS.get(slide_type, self.LAYOUTS["content"]).copy()

        design = {
            "layout_type": slide_type,
            "positions": layout,
            "style": {
                "colors": self.COLOR_SCHEMES.get(self.current_scheme, self.COLOR_SCHEMES["corporate"]),
            },
            "elements": [],
        }

        # Add design elements based on slide type
        if slide_type == "title":
            design["elements"].append({"type": "title", "style": "centered"})
            design["elements"].append({"type": "subtitle", "style": "centered"})
        elif slide_type == "content":
            design["elements"].append({"type": "title", "style": "left"})
            design["elements"].append({"type": "bullet_list", "style": "standard"})
        elif slide_type in ["two_column", "comparison"]:
            design["elements"].append({"type": "title", "style": "left"})
            design["elements"].append({"type": "column_left", "style": "standard"})
            design["elements"].append({"type": "column_right", "style": "standard"})

        return design

    async def _design_presentation(self, input_data: Dict) -> Dict:
        """Design complete presentation styling"""
        content = input_data.get("content", {})
        theme_name = input_data.get("theme", "corporate")

        self.log("Designing complete presentation...")

        # Create theme
        theme = await self._create_theme({"scheme": theme_name})

        # Design each slide
        slide_designs = []
        for slide in content.get("slides", []):
            slide_design = await self._design_slide({
                "slide_type": slide.get("type", "content"),
                "content": slide,
            })
            slide_design["slide_number"] = slide.get("slide_number", len(slide_designs) + 1)
            slide_designs.append(slide_design)

        presentation_design = {
            "theme": theme,
            "slides": slide_designs,
            "global_settings": {
                "width": 10,  # inches (16:9 aspect)
                "height": 5.625,  # inches
                "background": theme["colors"]["background"],
            },
        }

        self.log(f"Designed {len(slide_designs)} slides")
        return presentation_design

    async def _recommend_chart(self, input_data: Dict) -> Dict:
        """Recommend chart type for data visualization"""
        data_type = input_data.get("data_type", "comparison")
        data_points = input_data.get("data_points", 0)

        self.log(f"Recommending chart for: {data_type}")

        recommendations = {
            "comparison": "bar_chart",
            "trend": "line_chart",
            "composition": "pie_chart",
            "distribution": "histogram",
            "relationship": "scatter_plot",
        }

        chart_type = recommendations.get(data_type, "bar_chart")

        return {
            "recommended_chart": chart_type,
            "alternatives": list(set(recommendations.values()) - {chart_type})[:2],
            "reasoning": f"Based on {data_type} data with {data_points} points",
        }
