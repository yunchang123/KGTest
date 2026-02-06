"""
PCB元件知识图谱系统 - 主程序
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from config import INPUT_FILE, OUTPUT_DIR
from parsers.pcb_parser import PCBParser
from graph_builder.knowledge_graph import KnowledgeGraphBuilder
from visualization.graph_visualizer import GraphVisualizer, HierarchicalLayout
from visualization.charts import ChartGenerator
from exporters.csv_exporter import CSVExporter
from exporters.graphml_exporter import GraphFormatExporter
from exporters.report_generator import ReportGenerator
from utils.helpers import ProgressLogger


def main():
    """主流程"""
    logger = ProgressLogger(total_steps=7)

    # 1. 解析PCB数据
    logger.log("解析PCB JSON数据...")
    parser = PCBParser(INPUT_FILE)
    parser.parse()
    df = parser.to_dataframe()
    logger.success(f"解析完成: {len(df)}个元件")

    # 2. 构建知识图谱
    logger.log("构建知识图谱...")
    builder = KnowledgeGraphBuilder(df)
    builder.build()
    graph = builder.graph
    stats = builder.get_statistics()
    logger.success(f"图谱构建完成: {stats['total_nodes']}节点, {stats['total_edges']}边")

    # 3. 可视化知识图谱
    logger.log("生成知识图谱可视化...")
    visualizer = GraphVisualizer(graph)
    layout = HierarchicalLayout(graph)
    visualizer.set_layout(layout)
    visualizer.visualize(
        title="PCB Knowledge Graph",
        output_path=OUTPUT_DIR / "knowledge_graph.png",
        show_stats=True
    )
    logger.success("图谱可视化已保存")

    # 4. 生成分析图表
    logger.log("生成数据分析图表...")
    chart_gen = ChartGenerator(df)
    chart_gen.generate_all_charts(OUTPUT_DIR)
    logger.success("分析图表已生成")

    # 5. 导出CSV数据
    logger.log("导出CSV格式数据...")
    csv_exporter = CSVExporter()
    csv_files = csv_exporter.export_from_graph(graph, OUTPUT_DIR)
    logger.success(f"CSV导出完成: {len(csv_files)}个文件")

    # 6. 导出图格式
    logger.log("导出图格式数据...")
    graph_exporter = GraphFormatExporter()
    graph_files = graph_exporter.export_all_formats(graph, OUTPUT_DIR)
    logger.success(f"图格式导出完成: {len(graph_files)}个文件")

    # 7. 生成报告
    logger.log("生成分析报告...")
    report_gen = ReportGenerator(df, stats)
    report_gen.generate_markdown_report(OUTPUT_DIR / "report.md")
    report_gen.generate_json_report(OUTPUT_DIR / "report.json")
    logger.success("分析报告已生成")

    # 完成
    logger.success("所有任务完成!")
    print(f"\n📁 输出目录: {OUTPUT_DIR}")
    print(f"📊 知识图谱统计:")
    print(f"   - 节点: {stats['total_nodes']}个")
    print(f"   - 边: {stats['total_edges']}条")
    print(f"   - 节点类型: {list(stats['node_types'].keys())}")
    print(f"   - 关系类型: {list(stats['relation_types'].keys())}")


if __name__ == "__main__":
    main()
