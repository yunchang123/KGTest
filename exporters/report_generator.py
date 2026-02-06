"""
分析报告生成器
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import pandas as pd

from ..config import FUNCTION_CLASS_MAP


class ReportGenerator:
    """报告生成器"""

    def __init__(self, df: pd.DataFrame, graph_stats: Dict):
        self.df = df
        self.graph_stats = graph_stats
        self.report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_markdown_report(self, output_path: Path) -> Path:
        """生成Markdown格式报告"""
        lines = []

        # 标题
        lines.append("# PCB元件知识图谱分析报告")
        lines.append("")
        lines.append(f"**生成时间**: {self.report_time}")
        lines.append("")

        # 数据概览
        lines.append("## 1. 数据概览")
        lines.append("")
        lines.append(f"- **总元件数**: {len(self.df)}")
        lines.append(f"- **封装类型数**: {self.df['C'].nunique()}")
        lines.append(f"- **功能类别数**: {self.df['FunctionClass'].nunique()}")
        lines.append(f"- **物理类别数**: {self.df['PhysicalClass'].nunique()}")
        lines.append("")

        # 知识图谱统计
        lines.append("## 2. 知识图谱统计")
        lines.append("")
        lines.append(f"- **总节点数**: {self.graph_stats.get('total_nodes', 0)}")
        lines.append(f"- **总边数**: {self.graph_stats.get('total_edges', 0)}")
        lines.append(f"- **节点类型数**: {len(self.graph_stats.get('node_types', {}))}")
        lines.append(f"- **关系类型数**: {len(self.graph_stats.get('relation_types', {}))}")
        lines.append("")

        # 节点类型分布
        lines.append("### 节点类型分布")
        lines.append("")
        for node_type, count in self.graph_stats.get('node_types', {}).items():
            lines.append(f"- {node_type}: {count}个")
        lines.append("")

        # Top封装
        lines.append("## 3. 热门封装类型")
        lines.append("")
        top_packages = self.df['C'].value_counts().head(10)
        lines.append("| 排名 | 封装 | 元件数量 | 占比 |")
        lines.append("|------|------|----------|------|")
        total = len(self.df)
        for i, (pkg, count) in enumerate(top_packages.items(), 1):
            pct = count / total * 100
            lines.append(f"| {i} | {pkg} | {count} | {pct:.1f}% |")
        lines.append("")

        # 功能类别分布
        lines.append("## 4. 功能类别分布")
        lines.append("")
        func_dist = self.df['FunctionClass'].value_counts().sort_index()
        lines.append("| 类别 | 名称 | 数量 | 占比 |")
        lines.append("|------|------|------|------|")
        for func, count in func_dist.items():
            name = FUNCTION_CLASS_MAP.get(func, f'Class_{func}')
            pct = count / total * 100
            lines.append(f"| {func} | {name} | {count} | {pct:.1f}% |")
        lines.append("")

        # 尺寸统计
        lines.append("## 5. 尺寸统计")
        lines.append("")
        lines.append(f"- **平均长度**: {self.df['ChipL'].mean():.2f} mm")
        lines.append(f"- **平均宽度**: {self.df['ChipW'].mean():.2f} mm")
        lines.append(f"- **平均高度**: {self.df['ChipH'].mean():.2f} mm")
        lines.append(f"- **最大长度**: {self.df['ChipL'].max():.2f} mm")
        lines.append(f"- **最大宽度**: {self.df['ChipW'].max():.2f} mm")
        lines.append(f"- **最大高度**: {self.df['ChipH'].max():.2f} mm")
        lines.append("")

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return output_path

    def generate_json_report(self, output_path: Path) -> Path:
        """生成JSON格式报告"""
        report = {
            'metadata': {
                'generated_at': self.report_time,
                'version': '1.0'
            },
            'data_summary': {
                'total_components': len(self.df),
                'unique_packages': self.df['C'].nunique(),
                'unique_functions': self.df['FunctionClass'].nunique(),
                'unique_physical': self.df['PhysicalClass'].nunique()
            },
            'graph_statistics': self.graph_stats,
            'package_distribution': self.df['C'].value_counts().head(10).to_dict(),
            'function_distribution': self.df['FunctionClass'].value_counts().to_dict(),
            'size_statistics': {
                'length': {
                    'mean': self.df['ChipL'].mean(),
                    'std': self.df['ChipL'].std(),
                    'min': self.df['ChipL'].min(),
                    'max': self.df['ChipL'].max()
                },
                'width': {
                    'mean': self.df['ChipW'].mean(),
                    'std': self.df['ChipW'].std(),
                    'min': self.df['ChipW'].min(),
                    'max': self.df['ChipW'].max()
                },
                'height': {
                    'mean': self.df['ChipH'].mean(),
                    'std': self.df['ChipH'].std(),
                    'min': self.df['ChipH'].min(),
                    'max': self.df['ChipH'].max()
                }
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return output_path


def generate_report(df: pd.DataFrame, graph_stats: Dict, output_dir: Path) -> Dict[str, Path]:
    """便捷函数：生成所有报告"""
    generator = ReportGenerator(df, graph_stats)
    output_dir.mkdir(exist_ok=True)

    return {
        'markdown': generator.generate_markdown_report(output_dir / "report.md"),
        'json': generator.generate_json_report(output_dir / "report.json")
    }
