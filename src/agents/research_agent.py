"""Research Agent - Responsible for data collection and analysis"""
from typing import Any, Dict, List, Optional
import pandas as pd
from pathlib import Path
import json
import os
from .base_agent import BaseAgent
from ..core.task import Task

# Try to import web search libraries
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class ResearchAgent(BaseAgent):
    """
    Research Agent: Collects and analyzes data for presentation content.

    Responsibilities:
    - Read and parse Excel/CSV data files
    - Extract key insights and statistics
    - Identify important data points for visualization
    - Summarize research findings
    - Web search for additional information
    - Compare data across multiple sources
    """

    def __init__(self):
        super().__init__(
            name="ResearchAgent",
            role="Research & Data Analysis",
            description="Collects data, analyzes information, and extracts insights for presentation content"
        )
        self.data_cache: Dict[str, pd.DataFrame] = {}
        self.research_cache: Dict[str, Any] = {}

    async def execute_task(self, task: Task) -> Any:
        """Execute research-related tasks"""
        task_type = task.input_data.get("type", "analyze") if task.input_data else "analyze"

        if task_type == "read_excel":
            return await self._read_excel(task.input_data)
        elif task_type == "read_csv":
            return await self._read_csv(task.input_data)
        elif task_type == "analyze_data":
            return await self._analyze_data(task.input_data)
        elif task_type == "extract_insights":
            return await self._extract_insights(task.input_data)
        elif task_type == "compare_data":
            return await self._compare_data(task.input_data)
        elif task_type == "web_search":
            return await self._web_search(task.input_data)
        elif task_type == "aggregate_research":
            return await self._aggregate_research(task.input_data)
        elif task_type == "generate_chart_data":
            return await self._generate_chart_data(task.input_data)
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

    async def _read_csv(self, input_data: Dict) -> Dict:
        """Read and parse CSV file"""
        file_path = input_data.get("file_path")
        encoding = input_data.get("encoding", "utf-8")

        if not file_path:
            raise ValueError("file_path is required")

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.log(f"Reading CSV file: {file_path}")

        try:
            df = pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="shift-jis")

        cache_key = f"csv:{file_path}"
        self.data_cache[cache_key] = df

        result = {
            "file_path": str(file_path),
            "cache_key": cache_key,
            "rows": len(df),
            "columns": list(df.columns),
            "sample": df.head(5).to_dict() if len(df) > 0 else {},
        }

        self.log(f"Loaded CSV with {len(df)} rows")
        return result

    async def _compare_data(self, input_data: Dict) -> Dict:
        """Compare data from multiple sources"""
        datasets = input_data.get("datasets", [])
        compare_columns = input_data.get("compare_columns", [])

        self.log(f"Comparing {len(datasets)} datasets...")

        comparison = {
            "datasets": len(datasets),
            "comparisons": [],
            "summary": {},
        }

        # Load datasets from cache or input
        dfs = []
        for ds in datasets:
            if isinstance(ds, str) and ds in self.data_cache:
                dfs.append({"name": ds, "df": self.data_cache[ds]})
            elif isinstance(ds, dict):
                dfs.append({"name": ds.get("name", "dataset"), "df": pd.DataFrame(ds.get("data", {}))})

        if len(dfs) < 2:
            return {"error": "Need at least 2 datasets for comparison", "datasets": len(dfs)}

        # Compare numeric columns
        for col in compare_columns or []:
            col_comparison = {"column": col, "values": {}}
            for ds in dfs:
                if col in ds["df"].columns:
                    col_comparison["values"][ds["name"]] = {
                        "mean": float(ds["df"][col].mean()) if pd.api.types.is_numeric_dtype(ds["df"][col]) else None,
                        "sum": float(ds["df"][col].sum()) if pd.api.types.is_numeric_dtype(ds["df"][col]) else None,
                    }
            comparison["comparisons"].append(col_comparison)

        self.log("Data comparison complete")
        return comparison

    async def _web_search(self, input_data: Dict) -> Dict:
        """Perform web search for additional information"""
        query = input_data.get("query", "")
        max_results = input_data.get("max_results", 5)

        self.log(f"Web search: {query}")

        # Note: This is a placeholder. In production, you would integrate
        # with a real search API (Google, Bing, etc.)
        if not HAS_REQUESTS:
            return {
                "query": query,
                "results": [],
                "note": "Web search not available (requests library not installed)"
            }

        # Cache check
        cache_key = f"search:{query}"
        if cache_key in self.research_cache:
            self.log("Returning cached search results")
            return self.research_cache[cache_key]

        # Placeholder response - in production, integrate real search API
        result = {
            "query": query,
            "results": [],
            "note": "Search API integration required for live results"
        }

        self.research_cache[cache_key] = result
        return result

    async def _aggregate_research(self, input_data: Dict) -> Dict:
        """Aggregate research from multiple sources"""
        sources = input_data.get("sources", [])
        topic = input_data.get("topic", "")

        self.log(f"Aggregating research for: {topic}")

        aggregated = {
            "topic": topic,
            "sources": len(sources),
            "data_points": [],
            "key_findings": [],
            "data_for_charts": [],
        }

        for source in sources:
            if isinstance(source, dict):
                # Extract data points
                if "statistics" in source:
                    for col, stats in source["statistics"].items():
                        aggregated["data_points"].append({
                            "source": source.get("name", "unknown"),
                            "column": col,
                            "stats": stats
                        })

                # Extract insights
                if "insights" in source:
                    aggregated["key_findings"].extend(source["insights"])

        self.log(f"Aggregated {len(aggregated['data_points'])} data points")
        return aggregated

    async def _generate_chart_data(self, input_data: Dict) -> Dict:
        """Generate data formatted for chart creation"""
        source = input_data.get("source")
        chart_type = input_data.get("chart_type", "bar")
        x_column = input_data.get("x_column")
        y_column = input_data.get("y_column")
        group_by = input_data.get("group_by")

        self.log(f"Generating chart data: {chart_type}")

        # Get dataframe from cache or input
        df = None
        if isinstance(source, str) and source in self.data_cache:
            df = self.data_cache[source]
        elif isinstance(source, dict):
            df = pd.DataFrame(source)

        if df is None:
            return {"error": "No valid data source provided"}

        chart_data = {
            "chart_type": chart_type,
            "data": {},
            "labels": [],
        }

        if chart_type == "bar" and x_column and y_column:
            if group_by:
                grouped = df.groupby([x_column, group_by])[y_column].sum().unstack()
                chart_data["data"] = grouped.to_dict()
            else:
                chart_data["data"] = dict(zip(df[x_column], df[y_column]))
                chart_data["labels"] = list(df[x_column])

        elif chart_type == "pie" and x_column and y_column:
            chart_data["data"] = dict(zip(df[x_column], df[y_column]))

        elif chart_type == "line" and x_column and y_column:
            chart_data["data"] = dict(zip(df[x_column], df[y_column]))
            chart_data["labels"] = list(df[x_column])

        self.log("Chart data generated")
        return chart_data

    def get_cached_data(self, key: str) -> Optional[pd.DataFrame]:
        """Get cached dataframe by key"""
        return self.data_cache.get(key)

    def list_cached_data(self) -> List[str]:
        """List all cached data keys"""
        return list(self.data_cache.keys())
