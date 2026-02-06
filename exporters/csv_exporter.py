"""
CSV格式导出器 (用于Neo4j等图数据库导入)
"""
import pandas as pd
import networkx as nx
from pathlib import Path
from typing import Dict, List

from ..config import EXPORT_CONFIG


class CSVExporter:
    """CSV导出器"""

    def __init__(self, encoding: str = 'utf-8-sig'):
        self.encoding = encoding

    def export_nodes(self, nodes: List[Dict], output_path: Path) -> Path:
        """导出节点为CSV"""
        df = pd.DataFrame(nodes)
        df.to_csv(output_path, index=False, encoding=self.encoding)
        return output_path

    def export_edges(self, edges: List[Dict], output_path: Path) -> Path:
        """导出边为CSV"""
        df = pd.DataFrame(edges)
        df.to_csv(output_path, index=False, encoding=self.encoding)
        return output_path

    def export_from_graph(self, graph: nx.DiGraph, output_dir: Path) -> Dict[str, Path]:
        """从NetworkX图导出CSV"""
        output_dir.mkdir(exist_ok=True)

        # 导出节点
        nodes_data = []
        for node_id, data in graph.nodes(data=True):
            nodes_data.append({
                'node_id': node_id,
                'name': data.get('name', ''),
                'type': data.get('type', ''),
                'label': data.get('label', ''),
                'properties': str({k: v for k, v in data.items() 
                                 if k not in ['name', 'type', 'label']})
            })

        nodes_path = output_dir / "nodes.csv"
        self.export_nodes(nodes_data, nodes_path)

        # 导出边
        edges_data = []
        for src, tgt, data in graph.edges(data=True):
            edges_data.append({
                'source': src,
                'target': tgt,
                'relation': data.get('relation', ''),
                'weight': data.get('weight', 1.0)
            })

        edges_path = output_dir / "edges.csv"
        self.export_edges(edges_data, edges_path)

        return {
            'nodes': nodes_path,
            'edges': edges_path
        }

    def export_components_detail(self, df: pd.DataFrame, output_path: Path) -> Path:
        """导出元件详细数据"""
        df.to_csv(output_path, index=False, encoding=self.encoding)
        return output_path


def export_to_csv(graph: nx.DiGraph, output_dir: Path) -> Dict[str, Path]:
    """便捷函数：导出为CSV"""
    exporter = CSVExporter()
    return exporter.export_from_graph(graph, output_dir)
