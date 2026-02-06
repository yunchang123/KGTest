"""
数据分析图表生成器
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from ..config import FUNCTION_CLASS_MAP, VIS_CONFIG, OUTPUT_DIR


class ChartGenerator:
    """图表生成器"""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.bgcolor = '#0d1117'
        self.panel_color = '#161b22'
        self.edge_color = '#30363d'

    def generate_all_charts(self, output_dir: Path) -> List[Path]:
        """生成所有分析图表"""
        generated_files = []

        # 1. 封装分布图
        path = output_dir / "chart_package_distribution.png"
        self.plot_package_distribution(path)
        generated_files.append(path)

        # 2. 功能类别饼图
        path = output_dir / "chart_function_pie.png"
        self.plot_function_pie(path)
        generated_files.append(path)

        # 3. 尺寸散点图
        path = output_dir / "chart_size_scatter.png"
        self.plot_size_scatter(path)
        generated_files.append(path)

        # 4. 高度分布图
        path = output_dir / "chart_height_distribution.png"
        self.plot_height_distribution(path)
        generated_files.append(path)

        # 5. 综合分析面板
        path = output_dir / "chart_analysis_dashboard.png"
        self.plot_analysis_dashboard(path)
        generated_files.append(path)

        return generated_files

    def plot_package_distribution(self, output_path: Path, top_n: int = 15):
        """绘制封装类型分布图"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_facecolor(self.panel_color)
        fig.patch.set_facecolor(self.bgcolor)

        top_packages = self.df['C'].value_counts().head(top_n)
        bars = ax.barh(range(len(top_packages)), top_packages.values, 
                      color='#5d9cec', alpha=0.8, edgecolor='white', linewidth=0.5)

        ax.set_yticks(range(len(top_packages)))
        ax.set_yticklabels(top_packages.index, color='white', fontsize=10)
        ax.set_xlabel('元件数量', color='white', fontsize=11)
        ax.set_title(f'Top {top_n} 封装类型分布', color='white', 
                    fontsize=14, fontweight='bold', pad=15)
        ax.tick_params(colors='white')
        ax.invert_yaxis()

        # 添加数值标签
        for i, (bar, val) in enumerate(zip(bars, top_packages.values)):
            ax.text(val + 0.5, i, str(val), va='center', color='white', fontsize=9)

        self._style_axis(ax)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, facecolor=self.bgcolor, 
                   bbox_inches='tight')
        plt.close()

    def plot_function_pie(self, output_path: Path):
        """绘制功能类别饼图"""
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_facecolor(self.panel_color)
        fig.patch.set_facecolor(self.bgcolor)

        func_counts = self.df['FunctionClass'].value_counts().sort_index()
        func_names = [FUNCTION_CLASS_MAP.get(f, f'Class_{f}') for f in func_counts.index]
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']

        wedges, texts, autotexts = ax.pie(
            func_counts.values, 
            labels=func_names, 
            autopct='%1.1f%%',
            colors=colors, 
            textprops={'color': 'white', 'fontsize': 11},
            wedgeprops={'edgecolor': 'white', 'linewidth': 2}
        )

        ax.set_title('功能类别分布', color='white', fontsize=14, 
                    fontweight='bold', pad=15)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, facecolor=self.bgcolor, 
                   bbox_inches='tight')
        plt.close()

    def plot_size_scatter(self, output_path: Path):
        """绘制尺寸散点图"""
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_facecolor(self.panel_color)
        fig.patch.set_facecolor(self.bgcolor)

        func_colors = {
            1: '#e74c3c', 2: '#3498db', 7: '#2ecc71',
            11: '#f39c12', 12: '#9b59b6', 14: '#1abc9c'
        }

        for func_class in self.df['FunctionClass'].unique():
            subset = self.df[self.df['FunctionClass'] == func_class]
            label = FUNCTION_CLASS_MAP.get(func_class, f'Class_{func_class}')
            ax.scatter(subset['ChipL'], subset['ChipW'], 
                      c=func_colors.get(func_class, '#95a5a6'), 
                      label=label, alpha=0.7, s=80, 
                      edgecolors='white', linewidth=1)

        ax.set_xlabel('长度 (mm)', color='white', fontsize=12)
        ax.set_ylabel('宽度 (mm)', color='white', fontsize=12)
        ax.set_title('元件尺寸分布 (长×宽)', color='white', 
                    fontsize=14, fontweight='bold', pad=15)
        ax.legend(loc='upper right', facecolor=self.panel_color, 
                 edgecolor='white', labelcolor='white', fontsize=10)

        self._style_axis(ax)
        ax.set_xlim(0, 15)
        ax.set_ylim(0, 15)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, facecolor=self.bgcolor, 
                   bbox_inches='tight')
        plt.close()

    def plot_height_distribution(self, output_path: Path):
        """绘制高度分布直方图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_facecolor(self.panel_color)
        fig.patch.set_facecolor(self.bgcolor)

        heights = self.df['ChipH']
        n, bins, patches = ax.hist(heights, bins=30, color='#08d9d6', 
                                  alpha=0.7, edgecolor='white', linewidth=1)

        ax.axvline(heights.mean(), color='#ff2e63', linestyle='--', 
                  linewidth=2.5, label=f'平均值: {heights.mean():.2f}mm')
        ax.axvline(heights.median(), color='#f39c12', linestyle=':', 
                  linewidth=2.5, label=f'中位数: {heights.median():.2f}mm')

        ax.set_xlabel('高度 (mm)', color='white', fontsize=12)
        ax.set_ylabel('元件数量', color='white', fontsize=12)
        ax.set_title('元件高度分布', color='white', fontsize=14, 
                    fontweight='bold', pad=15)
        ax.legend(facecolor=self.panel_color, edgecolor='white', 
                 labelcolor='white', fontsize=11)

        self._style_axis(ax)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, facecolor=self.bgcolor, 
                   bbox_inches='tight')
        plt.close()

    def plot_analysis_dashboard(self, output_path: Path):
        """绘制综合分析面板"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.patch.set_facecolor(self.bgcolor)

        # 1. Top封装
        ax1 = axes[0, 0]
        ax1.set_facecolor(self.panel_color)
        top_packages = self.df['C'].value_counts().head(10)
        bars = ax1.barh(range(len(top_packages)), top_packages.values, color='#5d9cec')
        ax1.set_yticks(range(len(top_packages)))
        ax1.set_yticklabels(top_packages.index, color='white')
        ax1.set_title('Top 10 封装', color='white', fontsize=12, fontweight='bold')
        ax1.invert_yaxis()
        self._style_axis(ax1)

        # 2. 功能分布
        ax2 = axes[0, 1]
        ax2.set_facecolor(self.panel_color)
        func_counts = self.df['FunctionClass'].value_counts().sort_index()
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
        func_names = [FUNCTION_CLASS_MAP.get(f, f'Class_{f}')[:8] for f in func_counts.index]
        ax2.pie(func_counts.values, labels=func_names, autopct='%1.0f%%',
               colors=colors, textprops={'color': 'white', 'fontsize': 9})
        ax2.set_title('功能类别', color='white', fontsize=12, fontweight='bold')

        # 3. 尺寸分布
        ax3 = axes[1, 0]
        ax3.set_facecolor(self.panel_color)
        func_colors = {1: '#e74c3c', 2: '#3498db', 7: '#2ecc71', 
                      11: '#f39c12', 12: '#9b59b6', 14: '#1abc9c'}
        for func_class in self.df['FunctionClass'].unique()[:6]:
            subset = self.df[self.df['FunctionClass'] == func_class]
            ax3.scatter(subset['ChipL'], subset['ChipW'], 
                       c=func_colors.get(func_class, '#95a5a6'), 
                       alpha=0.6, s=50, edgecolors='white', linewidth=0.5)
        ax3.set_xlabel('长度 (mm)', color='white')
        ax3.set_ylabel('宽度 (mm)', color='white')
        ax3.set_title('尺寸散点', color='white', fontsize=12, fontweight='bold')
        self._style_axis(ax3)

        # 4. 高度分布
        ax4 = axes[1, 1]
        ax4.set_facecolor(self.panel_color)
        ax4.hist(self.df['ChipH'], bins=25, color='#08d9d6', alpha=0.7, 
                edgecolor='white')
        ax4.axvline(self.df['ChipH'].mean(), color='#ff2e63', linestyle='--', 
                   linewidth=2, label=f'均值: {self.df["ChipH"].mean():.2f}mm')
        ax4.set_xlabel('高度 (mm)', color='white')
        ax4.set_ylabel('数量', color='white')
        ax4.set_title('高度分布', color='white', fontsize=12, fontweight='bold')
        ax4.legend(facecolor=self.panel_color, labelcolor='white')
        self._style_axis(ax4)

        fig.suptitle('PCB元件数据分析面板', fontsize=18, color='white', 
                    fontweight='bold', y=0.98)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(output_path, dpi=150, facecolor=self.bgcolor, 
                   bbox_inches='tight')
        plt.close()

    def _style_axis(self, ax):
        """统一样式设置"""
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color(self.edge_color)
        ax.grid(True, alpha=0.2, color='white')


def generate_charts(df: pd.DataFrame, output_dir: Path) -> List[Path]:
    """便捷函数：生成所有图表"""
    generator = ChartGenerator(df)
    return generator.generate_all_charts(output_dir)
