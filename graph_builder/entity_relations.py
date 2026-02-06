"""
实体和关系定义
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


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
