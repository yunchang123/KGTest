"""
图格式导出器 (GraphML, GML, GEXF等)
"""
import networkx as nx
from pathlib import Path
from typing import Dict, List

from ..config import EXPORT_CONFIG


class GraphFormatExporter:
    """图格式导出器"""

    def __init__(self):
        self.supported_formats = EXPORT_CONFIG['graph_formats']

    def export_graphml(self, graph: nx.DiGraph, output_path: Path) -> Path:
        """导出为GraphML格式 (Gephi兼容)"""
        G = self._prepare_graph_for_export(graph)
        nx.write_graphml(G, output_path)
        return output_path

    def export_gml(self, graph: nx.DiGraph, output_path: Path) -> Path:
        """导出为GML格式"""
        G = self._prepare_graph_for_export(graph)
        nx.write_gml(G, output_path)
        return output_path

    def export_gexf(self, graph: nx.DiGraph, output_path: Path) -> Path:
        """导出为GEXF格式 (Sigma.js兼容)"""
        G = self._prepare_graph_for_export(graph)
        nx.write_gexf(G, output_path)
        return output_path

    def export_all_formats(self, graph: nx.DiGraph, output_dir: Path) -> Dict[str, Path]:
        """导出所有支持的格式"""
        output_dir.mkdir(exist_ok=True)
        exported = {}

        if 'graphml' in self.supported_formats:
            path = output_dir / "knowledge_graph.graphml"
            self.export_graphml(graph, path)
            exported['graphml'] = path

        if 'gml' in self.supported_formats:
            path = output_dir / "knowledge_graph.gml"
            self.export_gml(graph, path)
            exported['gml'] = path

        if 'gexf' in self.supported_formats:
            path = output_dir / "knowledge_graph.gexf"
            self.export_gexf(graph, path)
            exported['gexf'] = path

        return exported

    def _prepare_graph_for_export(self, graph: nx.DiGraph) -> nx.DiGraph:
        """准备图用于导出 - 转换属性类型"""
        G = nx.DiGraph()

        for node_id, data in graph.nodes(data=True):
            str_data = {k: str(v) if not isinstance(v, (int, float, bool)) else v 
                       for k, v in data.items()}
            G.add_node(node_id, **str_data)

        for src, tgt, data in graph.edges(data=True):
            str_data = {k: str(v) if not isinstance(v, (int, float, bool)) else v 
                       for k, v in data.items()}
            G.add_edge(src, tgt, **str_data)

        return G


def export_graph_formats(graph: nx.DiGraph, output_dir: Path) -> Dict[str, Path]:
    """便捷函数：导出所有图格式"""
    exporter = GraphFormatExporter()
    return exporter.export_all_formats(graph, output_dir)
