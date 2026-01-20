#!/usr/bin/env python3
"""
Multi-Agent PowerPoint Orchestrator
===================================

Main entry point for the presentation generation system.

Usage:
    python main.py --topic "プレゼンテーションのテーマ" [options]

Options:
    --topic         プレゼンテーションのトピック (required)
    --data-file     データファイルパス (Excel/CSV)
    --theme         テーマ名 (corporate, modern, vibrant)
    --output        出力ファイル名
    --num-slides    スライド数
"""

import asyncio
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from src.agents import CEOAgent


console = Console()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Multi-Agent PowerPoint Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="プレゼンテーションのトピック"
    )
    parser.add_argument(
        "--data-file",
        type=str,
        default=None,
        help="データファイルパス (Excel/CSV)"
    )
    parser.add_argument(
        "--theme",
        type=str,
        default="corporate",
        choices=["corporate", "modern", "vibrant"],
        help="カラーテーマ"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="presentation.pptx",
        help="出力ファイル名"
    )
    parser.add_argument(
        "--num-slides",
        type=int,
        default=5,
        help="目標スライド数"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="出力ディレクトリ"
    )

    args = parser.parse_args()

    # Show header
    console.print(Panel(
        "[bold cyan]Multi-Agent PowerPoint Orchestrator[/bold cyan]\n\n"
        "🤖 CEO Agent がサブエージェントを統括して\n"
        "   自動的にプレゼンテーションを生成します",
        title="[bold]Welcome[/bold]",
        border_style="cyan"
    ))

    # Validate data file if provided
    if args.data_file:
        data_path = Path(args.data_file)
        if not data_path.exists():
            console.print(f"[red]エラー: データファイルが見つかりません: {args.data_file}[/red]")
            return 1

    # Initialize CEO Agent
    ceo = CEOAgent(output_dir=args.output_dir)

    # Create requirements
    requirements = {
        "topic": args.topic,
        "data_file": args.data_file,
        "theme": args.theme,
        "output_filename": args.output,
        "num_slides": args.num_slides,
    }

    # Run the orchestration
    console.print()
    result = await ceo.create_presentation(requirements)

    # Show result
    if result.get("success"):
        console.print(Panel(
            f"[bold green]✅ プレゼンテーション生成完了！[/bold green]\n\n"
            f"📄 ファイル: {result.get('file_path')}\n"
            f"📊 スライド数: {result.get('slide_count')}",
            title="[green]Success[/green]",
            border_style="green"
        ))
        return 0
    else:
        console.print(Panel(
            f"[bold red]❌ エラーが発生しました[/bold red]\n\n"
            f"詳細: {result.get('error')}",
            title="[red]Error[/red]",
            border_style="red"
        ))
        return 1


def run():
    """Synchronous wrapper for main"""
    return asyncio.run(main())


if __name__ == "__main__":
    exit(run())
