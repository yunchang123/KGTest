"""
图布局引擎
"""
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from ..graph_builder.entity_relations import NodeType


class LayoutEngine:
    """布局引擎基类"""

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self.positions: Dict[str, Tuple[float, float]] = {}

    def calculate_layout(self) -> Dict[str, Tuple[float, float]]:
        """计算布局 - 子类实现"""
        raise NotImplementedError


class HierarchicalLayout(LayoutEngine):
    """分层树状布局"""

    def __init__(self, graph: nx.DiGraph, 
                 layer_spacing: float = 4.0,
                 node_spacing: float = 1.8):
        super().__init__(graph)
        self.layer_spacing = layer_spacing
        self.node_spacing = node_spacing

    def calculate_layout(self) -> Dict[str, Tuple[float, float]]:
        """计算分层布局"""
        # 按类型分组
        nodes_by_type = self._group_nodes_by_type()

        # 第0层: 物理类别 (最左)
        self._place_layer(nodes_by_type[NodeType.PHYSICAL_CLASS], -8, 4.0)

        # 第1层: 功能类别
        self._place_layer(nodes_by_type[NodeType.FUNCTION_CLASS], -4, 2.5)

        # 第2层: 封装 (按连接数排序)
        pkg_nodes = nodes_by_type[NodeType.PACKAGE]
        pkg_nodes_sorted = self._sort_by_connection_count(pkg_nodes)
        self._place_layer(pkg_nodes_sorted, 0, 1.8)

        # 第3层: 元件 (只显示部分)
        comp_nodes = self._select_representative_components(nodes_by_type[NodeType.COMPONENT])
        self._place_components_by_package(comp_nodes, 5)

        return self.positions

    def _group_nodes_by_type(self) -> Dict[NodeType, List[str]]:
        """按类型分组节点"""
        groups = defaultdict(list)
        for node_id, data in self.graph.nodes(data=True):
            node_type = NodeType(data.get('type'))
            groups[node_type].append(node_id)
        return groups

    def _place_layer(self, nodes: List[str], x: float, spacing: float):
        """放置单层节点"""
        nodes_sorted = sorted(nodes)
        n = len(nodes_sorted)
        for i, node in enumerate(nodes_sorted):
            y = (i - n / 2 + 0.5) * spacing
            self.positions[node] = (x, y)

    def _sort_by_connection_count(self, nodes: List[str]) -> List[str]:
        """按连接数排序节点"""
        counts = {}
        for node in nodes:
            counts[node] = self.graph.in_degree(node) + self.graph.out_degree(node)
        return sorted(nodes, key=lambda x: counts[x], reverse=True)

    def _select_representative_components(self, all_components: List[str], 
                                         max_components: int = 80) -> List[str]:
        """选择代表性元件（每个封装最多2个）"""
        selected = set()
        pkg_components = defaultdict(list)

        # 按封装分组
        for comp in all_components:
            for neighbor in self.graph.neighbors(comp):
                neighbor_data = self.graph.nodes[neighbor]
                if neighbor_data.get('type') == NodeType.PACKAGE.value:
                    pkg_components[neighbor].append(comp)
                    break

        # 每个封装选择最多2个
        for pkg, comps in pkg_components.items():
            selected.update(comps[:2])
            if len(selected) >= max_components:
                break

        return sorted(list(selected))[:max_components]

    def _place_components_by_package(self, components: List[str], x: float):
        """根据所属封装放置元件"""
        pkg_y_positions = {}

        for comp in components:
            # 找到所属的封装
            pkg = None
            for neighbor in self.graph.neighbors(comp):
                neighbor_data = self.graph.nodes[neighbor]
                if neighbor_data.get('type') == NodeType.PACKAGE.value:
                    pkg = neighbor
                    break

            if pkg and pkg in self.positions:
                pkg_y = self.positions[pkg][1]
                if pkg not in pkg_y_positions:
                    pkg_y_positions[pkg] = []
                pkg_y_positions[pkg].append(comp)

        # 分配位置
        for pkg, comps in pkg_y_positions.items():
            pkg_y = self.positions[pkg][1]
            for i, comp in enumerate(comps):
                y = pkg_y + (i - len(comps) / 2 + 0.5) * 0.6
                self.positions[comp] = (x, y)


class SpringLayout(LayoutEngine):
    """弹簧力导向布局"""

    def __init__(self, graph: nx.DiGraph, k: float = 2.0, iterations: int = 50):
        super().__init__(graph)
        self.k = k
        self.iterations = iterations

    def calculate_layout(self) -> Dict[str, Tuple[float, float]]:
        """计算弹簧布局"""
        pos = nx.spring_layout(
            self.graph, 
            k=self.k, 
            iterations=self.iterations,
            seed=42
        )

        # 调整布局 - 让类别节点分布在四周
        for node_id, (x, y) in pos.items():
            node_type = self.graph.nodes[node_id].get('type')

            if node_type == NodeType.PHYSICAL_CLASS.value:
                # 物理类别放左侧
                self.positions[node_id] = (x * 0.5 - 4, y * 3)
            elif node_type == NodeType.FUNCTION_CLASS.value:
                # 功能类别放右侧
                self.positions[node_id] = (x * 0.5 + 4, y * 2)
            elif node_type == NodeType.PACKAGE.value:
                # 封装放中间
                self.positions[node_id] = (x * 2, y * 1.5)
            else:
                # 元件放内层
                self.positions[node_id] = (x * 3, y * 1.2)

        return self.positions


class RadialLayout(LayoutEngine):
    """径向布局"""

    def __init__(self, graph: nx.DiGraph):
        super().__init__(graph)

    def calculate_layout(self) -> Dict[str, Tuple[float, float]]:
        """计算径向布局"""
        # 使用层次聚类布局
        pos = {}

        # 中心放置最常用的封装
        center_node = max(
            [n for n, d in self.graph.nodes(data=True) 
             if d.get('type') == NodeType.PACKAGE.value],
            key=lambda x: self.graph.degree(x),
            default=None
        )

        if center_node:
            pos[center_node] = (0, 0)

            # 第一层: 元件
            components = list(self.graph.predecessors(center_node))
            self._place_in_circle(components, 3, 0, pos)

            # 第二层: 类别
            categories = list(self.graph.successors(center_node))
            self._place_in_circle(categories, 6, np.pi/4, pos)

        self.positions = pos
        return pos

    def _place_in_circle(self, nodes: List[str], radius: float, 
                        start_angle: float, pos: Dict):
        """在圆周上放置节点"""
        n = len(nodes)
        for i, node in enumerate(nodes):
            angle = start_angle + 2 * np.pi * i / n
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            pos[node] = (x, y)
