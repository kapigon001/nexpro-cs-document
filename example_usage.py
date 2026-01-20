#!/usr/bin/env python3
"""
Example: Multi-Agent PowerPoint Orchestrator の使用例

このスクリプトは、マルチエージェントシステムの
基本的な使い方を示すサンプルです。
"""

import asyncio
from pathlib import Path
from src.agents import CEOAgent


async def example_basic():
    """基本的な使用例: トピックのみ指定"""
    print("=" * 60)
    print("Example 1: 基本的なプレゼンテーション生成")
    print("=" * 60)

    ceo = CEOAgent(output_dir="output")

    result = await ceo.create_presentation({
        "topic": "2024年度 事業計画",
        "theme": "corporate",
        "output_filename": "business_plan.pptx",
        "num_slides": 5,
    })

    print(f"\n結果: {'成功' if result['success'] else '失敗'}")
    if result['success']:
        print(f"生成ファイル: {result['file_path']}")

    return result


async def example_with_data():
    """データファイルを使用した例"""
    print("\n" + "=" * 60)
    print("Example 2: Excelデータを使用したプレゼンテーション生成")
    print("=" * 60)

    # Check if data file exists
    data_file = Path("E社比較.xlsx")
    if not data_file.exists():
        print(f"データファイルが見つかりません: {data_file}")
        return None

    ceo = CEOAgent(output_dir="output")

    result = await ceo.create_presentation({
        "topic": "E社との比較分析",
        "data_file": str(data_file),
        "theme": "modern",
        "output_filename": "e_company_comparison.pptx",
        "num_slides": 6,
    })

    print(f"\n結果: {'成功' if result['success'] else '失敗'}")
    if result['success']:
        print(f"生成ファイル: {result['file_path']}")

    return result


async def example_different_themes():
    """異なるテーマでの生成例"""
    print("\n" + "=" * 60)
    print("Example 3: 異なるテーマでのプレゼンテーション生成")
    print("=" * 60)

    themes = ["corporate", "modern", "vibrant"]
    results = []

    for theme in themes:
        print(f"\n--- テーマ: {theme} ---")
        ceo = CEOAgent(output_dir="output")

        result = await ceo.create_presentation({
            "topic": "製品紹介",
            "theme": theme,
            "output_filename": f"product_intro_{theme}.pptx",
            "num_slides": 4,
        })

        results.append(result)

    return results


async def main():
    """全ての例を実行"""
    print("\n🤖 Multi-Agent PowerPoint Orchestrator - 使用例\n")

    # 基本例
    await example_basic()

    # データ使用例
    await example_with_data()

    print("\n" + "=" * 60)
    print("全ての例が完了しました")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
