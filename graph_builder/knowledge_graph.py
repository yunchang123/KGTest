"""
知识图谱构建器
"""
import pandas as pd
import networkx as nx
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
from enum import Enum
from dataclasses import dataclass, field


# ========== 实体和关系定义（从entity_relations.py复制）==========

class NodeType(Enum):
    """节点类型枚举"""
    COMPONENT = "Component"
    PACKAGE = "Package"
    FUNCTION_CLASS = "FunctionClass"
    PHYSICAL_CLASS = "PhysicalClass"


class RelationType(Enum):
    """关系类型枚举"""
    USES_PACKAGE = "usesPackage"
    HAS_FUNCTION = "hasFunction"
    HAS_PHYSICAL_TYPE = "hasPhysicalType"


@dataclass
class Node:
    """知识图谱节点"""
    id: str
    name: str
    node_type: NodeType
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.node_type.value,
            'label': self.label,
            **self.properties
        }


@dataclass
class Edge:
    """知识图谱边"""
    source: str
    target: str
    relation: RelationType
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'source': self.source,
            'target': self.target,
            'relation': self.relation.value,
            'weight': self.weight,
            **self.properties
        }


class EntityFactory:
    """实体工厂类"""

    @staticmethod
    def create_component_node(idnum: int, name: str, lname: str,
                             chip_l: float, chip_w: float, chip_h: float,
                             mfr: str = '', mpn: str = '') -> Node:
        """创建元件节点"""
        return Node(
            id=f"COMP_{idnum}",
            name=name,
            node_type=NodeType.COMPONENT,
            label=name[:15] if len(name) > 15 else name,
            properties={
                'idnum': idnum,
                'lname': lname,
                'chip_l': chip_l,
                'chip_w': chip_w,
                'chip_h': chip_h,
                'mfr': mfr,
                'mpn': mpn,
                'size': 20 + chip_l * 5
            }
        )

    @staticmethod
    def create_package_node(package_name: str) -> Node:
        """创建封装节点"""
        return Node(
            id=f"PKG_{package_name}",
            name=package_name,
            node_type=NodeType.PACKAGE,
            label=package_name,
            properties={'size': 30}
        )

    @staticmethod
    def create_function_class_node(func_class: int, class_name: str) -> Node:
        """创建功能类别节点"""
        return Node(
            id=f"FUNC_{func_class}",
            name=class_name,
            node_type=NodeType.FUNCTION_CLASS,
            label=class_name,
            properties={'class_code': func_class, 'size': 40}
        )

    @staticmethod
    def create_physical_class_node(phy_class: int, class_name: str) -> Node:
        """创建物理类别节点"""
        return Node(
            id=f"PHY_{phy_class}",
            name=class_name,
            node_type=NodeType.PHYSICAL_CLASS,
            label=class_name,
            properties={'class_code': phy_class, 'size': 40}
        )

    @staticmethod
    def create_edge(source: str, target: str, relation: RelationType,
                   weight: float = 1.0) -> Edge:
        """创建边"""
        return Edge(
            source=source,
            target=target,
            relation=relation,
            weight=weight
        )


# ========== 配置（从config.py复制）==========

FUNCTION_CLASS_MAP = {
    1: 'Resistor',
    2: 'Capacitor',
    7: 'Inductor',
    11: 'LED',
    12: 'Diode',
    14: 'IC/Transistor'
}

PHYSICAL_CLASS_MAP = {
    1: 'Passive',
    2: 'Active',
    3: 'Connector'
}


# ========== 知识图谱构建器 ==========

class KnowledgeGraphBuilder:
    """知识图谱构建器"""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.graph: Optional[nx.DiGraph] = None

    def build(self) -> 'KnowledgeGraphBuilder':
        """构建知识图谱"""
        self._create_component_nodes()
        self._create_package_nodes()
        self._create_function_class_nodes()
        self._create_physical_class_nodes()
        self._create_relationships()
        self._build_networkx_graph()
        return self

    def _create_component_nodes(self):
        """创建所有元件节点"""
        for _, row in self.df.iterrows():
            node = EntityFactory.create_component_node(
                idnum=row['IDNUM'],
                name=row['NAME'],
                lname=row['LNAME'],
                chip_l=row['ChipL'],
                chip_w=row['ChipW'],
                chip_h=row['ChipH'],
                mfr=row['MFR'],
                mpn=row['MPN']
            )
            self.nodes[node.id] = node

    def _create_package_nodes(self):
        """创建所有封装节点"""
        packages = self.df['C'].unique()
        for pkg in packages:
            if pkg:
                node = EntityFactory.create_package_node(pkg)
                self.nodes[node.id] = node

    def _create_function_class_nodes(self):
        """创建所有功能类别节点"""
        func_classes = self.df['FunctionClass'].unique()
        for fc in func_classes:
            fc_name = FUNCTION_CLASS_MAP.get(fc, f'Class_{fc}')
            node = EntityFactory.create_function_class_node(fc, fc_name)
            self.nodes[node.id] = node

    def _create_physical_class_nodes(self):
        """创建所有物理类别节点"""
        phy_classes = self.df['PhysicalClass'].unique()
        for pc in phy_classes:
            pc_name = PHYSICAL_CLASS_MAP.get(pc, f'Physical_{pc}')
            node = EntityFactory.create_physical_class_node(pc, pc_name)
            self.nodes[node.id] = node

    def _create_relationships(self):
        """创建所有关系边"""
        for _, row in self.df.iterrows():
            comp_id = f"COMP_{row['IDNUM']}"

            # 1. 元件 -> 封装
            if row['C']:
                edge = EntityFactory.create_edge(
                    source=comp_id,
                    target=f"PKG_{row['C']}",
                    relation=RelationType.USES_PACKAGE
                )
                self.edges.append(edge)

            # 2. 元件 -> 功能类别
            edge = EntityFactory.create_edge(
                source=comp_id,
                target=f"FUNC_{row['FunctionClass']}",
                relation=RelationType.HAS_FUNCTION
            )
            self.edges.append(edge)

            # 3. 元件 -> 物理类别
            edge = EntityFactory.create_edge(
                source=comp_id,
                target=f"PHY_{row['PhysicalClass']}",
                relation=RelationType.HAS_PHYSICAL_TYPE
            )
            self.edges.append(edge)

    def _build_networkx_graph(self):
        """构建NetworkX图"""
        self.graph = nx.DiGraph()

        # 添加节点
        for node_id, node in self.nodes.items():
            self.graph.add_node(node_id, **node.to_dict())

        # 添加边
        for edge in self.edges:
            self.graph.add_edge(
                edge.source,
                edge.target,
                relation=edge.relation.value,
                weight=edge.weight
            )

    def get_nodes_by_type(self, node_type: NodeType) -> List[Node]:
        """获取指定类型的所有节点"""
        return [n for n in self.nodes.values() if n.node_type == node_type]

    def get_edges_by_relation(self, relation: RelationType) -> List[Edge]:
        """获取指定关系的所有边"""
        return [e for e in self.edges if e.relation == relation]

    def get_statistics(self) -> Dict:
        """获取图谱统计信息"""
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'node_types': {
                nt.value: len(self.get_nodes_by_type(nt))
                for nt in NodeType
            },
            'relation_types': {
                rt.value: len(self.get_edges_by_relation(rt))
                for rt in RelationType
            },
            'network_metrics': {
                'density': nx.density(self.graph),
                'is_connected': nx.is_weakly_connected(self.graph),
                'connected_components': nx.number_weakly_connected_components(self.graph)
            } if self.graph else {}
        }

    def get_subgraph_by_package(self, package_name: str) -> List[str]:
        """获取指定封装下的所有元件"""
        pkg_id = f"PKG_{package_name}"
        if pkg_id not in self.nodes:
            return []

        # 找到所有指向该封装的元件
        components = [
            e.source for e in self.edges
            if e.target == pkg_id and e.relation == RelationType.USES_PACKAGE
        ]
        return components

    def get_component_details(self, component_id: str) -> Optional[Dict]:
        """获取元件详细信息"""
        if component_id not in self.nodes:
            return None

        node = self.nodes[component_id]

        # 找到所有相关边
        related_edges = [
            e for e in self.edges
            if e.source == component_id or e.target == component_id
        ]

        return {
            'node': node.to_dict(),
            'relationships': [e.to_dict() for e in related_edges]
        }