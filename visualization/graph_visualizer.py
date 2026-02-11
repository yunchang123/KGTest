"""
知识图谱可视化器
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

from visualization.layout_engines import LayoutEngine, HierarchicalLayout

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']

# 本地配置
VIS_CONFIG = {
    'figure_size': (20, 16),
    'dpi': 200,
    'bgcolor': '#0d1117',
    'node_colors': {
        'PhysicalClass': '#ff2e63',
        'FunctionClass': '#08d9d6',
        'Package': '#5d9cec',
        'Component': '#f39c12'
    },
    'edge_colors': {
        'hasPhysicalType': '#ff2e63',
        'hasFunction': '#08d9d6',
        'usesPackage': '#5d9cec'
    },
    'font_size': {
        'PhysicalClass': 11,
        'FunctionClass': 10,
        'Package': 9,
        'Component': 7
    },
    'node_sizes': {
        'PhysicalClass': 1000,
        'FunctionClass': 700,
        'Package': 500,
        'Component': 250
    }
}


class GraphVisualizer:
    """知识图谱可视化器"""

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self.positions: Dict[str, Tuple[float, float]] = {}
        self.config = VIS_CONFIG

        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

    def set_layout(self, layout_engine: LayoutEngine) -> 'GraphVisualizer':
        """设置布局引擎"""
        self.positions = layout_engine.calculate_layout()
        return self

    def visualize(self,
                  title: str = "PCB Knowledge Graph",
                  output_path: Optional[Path] = None,
                  show_stats: bool = True,
                  figsize: Optional[Tuple[int, int]] = None):
        """可视化知识图谱"""

        # 创建图形
        fig, ax = plt.subplots(figsize=figsize or self.config['figure_size'])
        ax.set_facecolor(self.config['bgcolor'])
        fig.patch.set_facecolor(self.config['bgcolor'])

        # 过滤可见的边
        visible_edges = self._get_visible_edges()

        # 绘制边
        self._draw_edges(ax, visible_edges)

        # 绘制节点
        self._draw_nodes(ax)

        # 添加层级标签
        self._draw_layer_labels(ax)

        # 设置坐标轴
        ax.set_xlim(-10, 8)
        ax.set_ylim(-12, 14)
        ax.axis('off')

        # 添加标题
        self._draw_title(ax, title)

        # 添加图例
        self._draw_legend(ax)

        # 添加统计信息
        if show_stats:
            self._draw_statistics(ax)

        plt.tight_layout()

        # 保存
        if output_path:
            plt.savefig(output_path, dpi=self.config['dpi'],
                       facecolor=self.config['bgcolor'],
                       edgecolor='none', bbox_inches='tight')
            print(f"✓ 图谱已保存: {output_path}")

        return fig

    def _get_visible_edges(self) -> List[Tuple[str, str, Dict]]:
        """获取可见的边"""
        visible = []
        for edge in self.graph.edges(data=True):
            if edge[0] in self.positions and edge[1] in self.positions:
                visible.append(edge)
        return visible

    def _draw_edges(self, ax, edges: List[Tuple[str, str, Dict]]):
        """绘制边"""
        for src, tgt, data in edges:
            x1, y1 = self.positions[src]
            x2, y2 = self.positions[tgt]

            # 根据关系类型着色
            relation = data.get('relation', '')
            color = self.config['edge_colors'].get(relation, '#aaaaaa')

            ax.plot([x1, x2], [y1, y2], color=color, alpha=0.25,
                   linewidth=1.2, zorder=1)

    def _draw_nodes(self, ax):
        """绘制节点"""
        for node_id, (x, y) in self.positions.items():
            node_data = self.graph.nodes[node_id]
            node_type = node_data.get('type', '')
            color = self.config['node_colors'].get(node_type, '#ffffff')
            size = self.config['node_sizes'].get(node_type, 300)
            fontsize = self.config['font_size'].get(node_type, 8)

            # 绘制发光效果
            for r, alpha in [(np.sqrt(size)/25, 0.2), (np.sqrt(size)/30, 0.4)]:
                circle = plt.Circle((x, y), r, color=color, alpha=alpha, zorder=2)
                ax.add_patch(circle)

            # 绘制主节点
            circle = plt.Circle((x, y), np.sqrt(size)/35, color=color,
                              alpha=0.95, zorder=3, edgecolor='white', linewidth=2)
            ax.add_patch(circle)

            # 添加标签
            label = node_data.get('label', '')
            if len(label) > 15:
                label = label[:12] + '...'

            ax.text(x, y, label, ha='center', va='center',
                   fontsize=fontsize, color='white', fontweight='bold', zorder=4)

    def _draw_layer_labels(self, ax):
        """绘制层级标签"""
        labels = [
            (-8, 12, '物理类别\nPhysicalClass', self.config['node_colors']['PhysicalClass']),
            (-4, 12, '功能类别\nFunctionClass', self.config['node_colors']['FunctionClass']),
            (0, 12, '封装\nPackage', self.config['node_colors']['Package']),
            (5, 12, '元件\nComponent', self.config['node_colors']['Component'])
        ]

        for x, y, label, color in labels:
            ax.text(x, y, label, ha='center', va='center',
                   fontsize=12, color=color, fontweight='bold', alpha=0.8)

    def _draw_title(self, ax, title: str):
        """绘制标题"""
        ax.text(-1, 13.5, title, fontsize=24, color='white',
               ha='center', fontweight='bold')
        ax.text(-1, 12.8, 'Knowledge Graph of PCB Components',
               fontsize=14, color='#888888', ha='center', style='italic')

    def _draw_legend(self, ax):
        """绘制图例"""
        legend_elements = [
            mpatches.Patch(color=self.config['node_colors']['PhysicalClass'],
                          label='PhysicalClass (物理类别)'),
            mpatches.Patch(color=self.config['node_colors']['FunctionClass'],
                          label='FunctionClass (功能类别)'),
            mpatches.Patch(color=self.config['node_colors']['Package'],
                          label='Package (封装)'),
            mpatches.Patch(color=self.config['node_colors']['Component'],
                          label='Component (元件)')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=10,
                 facecolor=self.config['bgcolor'], edgecolor='white',
                 labelcolor='white', framealpha=0.9)

    def _draw_statistics(self, ax):
        """绘制统计面板"""
        stats = self._calculate_stats()

        stats_text = f"""📊 数据统计
━━━━━━━━━━━━━━━
总节点数: {stats['total_nodes']}
显示节点: {stats['visible_nodes']}
显示关系: {stats['visible_edges']}
封装类型: {stats['package_count']}
功能类别: {stats['function_count']}
物理类别: {stats['physical_count']}
"""
        ax.text(-9.5, 10, stats_text, fontsize=10, color='white', va='top',
               family='monospace',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='#161b22',
                        edgecolor='#30363d', linewidth=2))

    def _calculate_stats(self) -> Dict:
        """计算统计信息"""
        total_nodes = len(self.graph.nodes())
        visible_nodes = len(self.positions)
        visible_edges = len(self._get_visible_edges())

        type_counts = {}
        for node_id, data in self.graph.nodes(data=True):
            node_type = data.get('type', 'unknown')
            type_counts[node_type] = type_counts.get(node_type, 0) + 1

        return {
            'total_nodes': total_nodes,
            'visible_nodes': visible_nodes,
            'visible_edges': visible_edges,
            'package_count': type_counts.get('Package', 0),
            'function_count': type_counts.get('FunctionClass', 0),
            'physical_count': type_counts.get('PhysicalClass', 0)
        }


def visualize_knowledge_graph(graph: nx.DiGraph,
                              output_path: Path,
                              title: str = "PCB Knowledge Graph"):
    """便捷函数：可视化知识图谱"""
    visualizer = GraphVisualizer(graph)
    layout = HierarchicalLayout(graph)
    visualizer.set_layout(layout)
    return visualizer.visualize(title=title, output_path=output_path)