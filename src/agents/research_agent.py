"""Research Agent - Responsible for data collection and analysis"""
from typing import Any, Dict, List, Optional
import pandas as pd
from pathlib import Path
from .base_agent import BaseAgent
from ..core.task import Task


class ResearchAgent(BaseAgent):
    """
    Research Agent: Collects and analyzes data for presentation content.

    Responsibilities:
    - Read and parse Excel/CSV data files
    - Extract key insights and statistics
    - Identify important data points for visualization
    - Summarize research findings
    """

    def __init__(self):
        super().__init__(
            name="ResearchAgent",
            role="Research & Data Analysis",
            description="Collects data, analyzes information, and extracts insights for presentation content"
        )
        self.data_cache: Dict[str, pd.DataFrame] = {}

    async def execute_task(self, task: Task) -> Any:
        """Execute research-related tasks"""
        task_type = task.input_data.get("type", "analyze") if task.input_data else "analyze"

        if task_type == "read_excel":
            return await self._read_excel(task.input_data)
        elif task_type == "analyze_data":
            return await self._analyze_data(task.input_data)
        elif task_type == "extract_insights":
            return await self._extract_insights(task.input_data)
        else:
            return await self._general_research(task.input_data)

    async def _read_excel(self, input_data: Dict) -> Dict:
        """Read and parse Excel file"""
        file_path = input_data.get("file_path")
        if not file_path:
            raise ValueError("file_path is required")

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.log(f"Reading Excel file: {file_path}")

        # Read all sheets
        excel_data = pd.read_excel(file_path, sheet_name=None)

        result = {
            "file_path": str(file_path),
            "sheets": {},
            "summary": {
                "total_sheets": len(excel_data),
                "sheet_names": list(excel_data.keys()),
            }
        }

        for sheet_name, df in excel_data.items():
            self.data_cache[f"{file_path}:{sheet_name}"] = df
            result["sheets"][sheet_name] = {
                "rows": len(df),
                "columns": list(df.columns),
                "sample": df.head(5).to_dict() if len(df) > 0 else {},
            }

        self.log(f"Loaded {len(excel_data)} sheets from Excel file")
        return result

    async def _analyze_data(self, input_data: Dict) -> Dict:
        """Analyze data and extract statistics"""
        data = input_data.get("data")
        if data is None and "cache_key" in input_data:
            data = self.data_cache.get(input_data["cache_key"])

        if data is None:
            raise ValueError("No data provided for analysis")

        if isinstance(data, dict):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise ValueError("Data must be a dict or DataFrame")

        self.log("Analyzing data...")

        analysis = {
            "shape": {"rows": len(df), "columns": len(df.columns)},
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "statistics": {},
            "missing_values": df.isnull().sum().to_dict(),
        }

        # Numeric column statistics
        numeric_cols = df.select_dtypes(include=["number"]).columns
        for col in numeric_cols:
            analysis["statistics"][col] = {
                "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                "median": float(df[col].median()) if not pd.isna(df[col].median()) else None,
                "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                "std": float(df[col].std()) if not pd.isna(df[col].std()) else None,
            }

        self.log("Data analysis complete")
        return analysis

    async def _extract_insights(self, input_data: Dict) -> List[Dict]:
        """Extract key insights from analyzed data"""
        analysis = input_data.get("analysis", {})
        context = input_data.get("context", "")

        self.log("Extracting insights...")

        insights = []

        # Generate insights based on statistics
        stats = analysis.get("statistics", {})
        for col, col_stats in stats.items():
            if col_stats.get("max") and col_stats.get("min"):
                range_val = col_stats["max"] - col_stats["min"]
                insights.append({
                    "type": "range",
                    "column": col,
                    "description": f"{col}の範囲: {col_stats['min']:.2f} ~ {col_stats['max']:.2f}",
                    "value": range_val,
                })

            if col_stats.get("mean"):
                insights.append({
                    "type": "average",
                    "column": col,
                    "description": f"{col}の平均値: {col_stats['mean']:.2f}",
                    "value": col_stats["mean"],
                })

        self.log(f"Extracted {len(insights)} insights")
        return insights

    async def _general_research(self, input_data: Dict) -> Dict:
        """General research task"""
        topic = input_data.get("topic", "")
        sources = input_data.get("sources", [])

        self.log(f"Conducting research on: {topic}")

        return {
            "topic": topic,
            "sources_checked": len(sources),
            "findings": [],
            "recommendations": [],
        }
