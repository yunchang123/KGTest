# PCB元件知识图谱系统

基于PCB JSON数据构建的知识图谱分析与可视化系统。

## 📁 项目结构

```
pcb_knowledge_graph/
├── config.py                  # 配置文件
├── main.py                    # 主程序入口
├── requirements.txt           # 依赖文件
├── README.md                  # 项目说明
├── data/                      # 数据目录
│   └── __init__.py
├── parsers/                   # 数据解析模块
│   ├── __init__.py
│   └── pcb_parser.py         # PCB JSON解析器
├── graph_builder/            # 知识图谱构建模块
│   ├── __init__.py
│   ├── entity_relations.py   # 实体和关系定义
│   └── knowledge_graph.py    # 知识图谱构建器
├── visualization/            # 可视化模块
│   ├── __init__.py
│   ├── graph_visualizer.py   # 图谱可视化器
│   ├── layout_engines.py     # 布局引擎
│   └── charts.py             # 数据分析图表
├── exporters/                # 导出模块
│   ├── __init__.py
│   ├── csv_exporter.py       # CSV导出器
│   ├── graphml_exporter.py   # 图格式导出器
│   └── report_generator.py   # 报告生成器
├── utils/                    # 工具模块
│   ├── __init__.py
│   └── helpers.py            # 辅助函数
└── output/                   # 输出目录
    └── .gitkeep
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备数据

将PCB JSON文件放入 `data/` 目录，命名为 `Vayo.json`

### 3. 运行程序

```bash
python main.py
```

## 📊 输出文件

运行后会在 `output/` 目录生成以下文件：

### 可视化图表
- `knowledge_graph.png` - 知识图谱可视化图
- `chart_package_distribution.png` - 封装类型分布
- `chart_function_pie.png` - 功能类别饼图
- `chart_size_scatter.png` - 尺寸散点图
- `chart_height_distribution.png` - 高度分布
- `chart_analysis_dashboard.png` - 综合分析面板

### 数据导出
- `nodes.csv` - 节点数据 (Neo4j导入)
- `edges.csv` - 关系数据 (Neo4j导入)
- `knowledge_graph.graphml` - Gephi格式
- `knowledge_graph.gml` - GML格式
- `knowledge_graph.gexf` - GEXF格式

### 分析报告
- `report.md` - Markdown格式报告
- `report.json` - JSON格式报告

## 🔧 配置说明

修改 `config.py` 可以自定义：

- 输入文件路径
- 可视化颜色方案
- 节点大小和字体
- 类别名称映射
- 导出格式选项

## 📈 知识图谱结构

### 节点类型 (4种)
1. **Component** (元件) - 154个
2. **Package** (封装) - 32种类型
3. **FunctionClass** (功能类别) - 12类
4. **PhysicalClass** (物理类别) - 3类

### 关系类型 (3种)
1. **usesPackage** - 元件使用封装
2. **hasFunction** - 元件具有功能
3. **hasPhysicalType** - 元件具有物理类型

## 🎯 使用示例

### 单独使用解析器
```python
from parsers.pcb_parser import PCBParser

parser = PCBParser("data/Vayo.json")
parser.parse()
df = parser.to_dataframe()
print(parser.get_statistics())
```

### 单独构建知识图谱
```python
from graph_builder.knowledge_graph import KnowledgeGraphBuilder

builder = KnowledgeGraphBuilder(df)
builder.build()
stats = builder.get_statistics()
graph = builder.graph
```

### 自定义可视化
```python
from visualization.graph_visualizer import GraphVisualizer
from visualization.layout_engines import SpringLayout

visualizer = GraphVisualizer(graph)
layout = SpringLayout(graph)
visualizer.set_layout(layout)
visualizer.visualize(title="My Graph", output_path="output/my_graph.png")
```

## 📚 技术栈

- **Python 3.8+**
- **pandas** - 数据处理
- **networkx** - 图论分析
- **matplotlib** - 可视化

## 🔗 Neo4j导入

使用生成的CSV文件导入Neo4j：

```cypher
// 导入节点
LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
CREATE (n:Node {id: row.node_id, name: row.name, type: row.type});

// 导入关系
LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row
MATCH (a:Node {id: row.source}), (b:Node {id: row.target})
CREATE (a)-[:RELATION {type: row.relation}]->(b);
```

## 📄 许可证

MIT License
