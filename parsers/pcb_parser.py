"""
PCB JSON数据解析器
"""
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..utils.helpers import load_json, get_function_class_name, get_physical_class_name
from ..config import FUNCTION_CLASS_MAP, PHYSICAL_CLASS_MAP


class PCBParser:
    """PCB数据解析器"""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.raw_data = None
        self.parts = []
        self.df = None

    def parse(self) -> 'PCBParser':
        """解析JSON文件"""
        self.raw_data = load_json(self.filepath)
        self.parts = self.raw_data.get('Part', [])
        return self

    def extract_entities(self) -> List[Dict[str, Any]]:
        """提取实体信息"""
        entities = []

        for part in self.parts:
            entity = self._extract_part_data(part)
            if entity:
                entities.append(entity)

        return entities

    def _extract_part_data(self, part: Dict) -> Optional[Dict[str, Any]]:
        """提取单个元件数据"""
        try:
            general = part.get('General', {})
            shape = part.get('Shape', {})
            outline = shape.get('Outline', {})
            smt = part.get('SMT', {})
            supply = part.get('Supply', {})

            # 安全获取Feeder数据
            feeder_data = supply.get('Feeder', {})

            return {
                'IDNUM': part.get('IDNUM'),
                'NAME': part.get('NAME', ''),
                'LNAME': part.get('LNAME', ''),
                'PhysicalClass': general.get('PhysicalClass'),
                'FunctionClass': general.get('FunctionClass'),
                'C': general.get('C', ''),  # 封装类型
                'MFR': general.get('MFR', ''),
                'MPN': general.get('MPN', ''),
                'ChipL': outline.get('ChipL', 0),
                'ChipW': outline.get('ChipW', 0),
                'ChipH': outline.get('ChipH', 0),
                'Nozzle': ','.join(smt.get('Nozzle', [])),
                'NR': feeder_data.get('NR', 0) if isinstance(feeder_data, dict) else 0
            }
        except Exception as e:
            print(f"解析元件 {part.get('IDNUM', 'unknown')} 时出错: {e}")
            return None

    def to_dataframe(self) -> pd.DataFrame:
        """转换为DataFrame"""
        if self.df is None:
            entities = self.extract_entities()
            self.df = pd.DataFrame(entities)
        return self.df

    def get_statistics(self) -> Dict[str, Any]:
        """获取数据统计信息"""
        df = self.to_dataframe()

        return {
            'total_components': len(df),
            'unique_packages': df['C'].nunique(),
            'unique_functions': df['FunctionClass'].nunique(),
            'unique_physical': df['PhysicalClass'].nunique(),
            'top_packages': df['C'].value_counts().head(10).to_dict(),
            'function_distribution': df['FunctionClass'].value_counts().to_dict(),
            'size_stats': {
                'avg_length': df['ChipL'].mean(),
                'avg_width': df['ChipW'].mean(),
                'avg_height': df['ChipH'].mean(),
                'max_length': df['ChipL'].max(),
                'max_width': df['ChipW'].max(),
                'max_height': df['ChipH'].max()
            }
        }


def parse_pcb_data(filepath: Path) -> pd.DataFrame:
    """便捷函数：解析PCB数据"""
    parser = PCBParser(filepath)
    parser.parse()
    return parser.to_dataframe()
