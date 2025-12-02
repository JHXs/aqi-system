import pandas as pd
import os
from datetime import datetime
import logging
from typing import Dict, Any, List
from .influx_client import InfluxDBManager
from .config import MEASUREMENT_NAME, TAGS, FIELDS

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataImporter:
    def __init__(self):
        self.influx_manager = InfluxDBManager()

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗DataFrame，转换数据类型

        Args:
            df: 原始DataFrame

        Returns:
            清洗后的DataFrame
        """
        # 转换时间列为datetime
        time_columns = ['timestamp', 'time', 'date', 'datetime']
        for col in time_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                break

        # 转换数值列为float
        numeric_columns = ['pm25', 'pm10', 'co2', 'so2', 'no2', 'o3', 'aqi',
                          'temperature', 'humidity', 'pressure', 'wind_speed', 'wind_direction']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 删除包含无效时间的行
        df = df.dropna(subset=[col for col in time_columns if col in df.columns])

        return df

    def detect_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        检测DataFrame中的列并映射到标准字段

        Args:
            df: DataFrame

        Returns:
            列名映射字典
        """
        column_mapping = {}

        # 标签列映射
        tag_mappings = {
            'station_id': ['station_id', 'stationid', 'station', 'id', '监测站编号'],
            'city': ['city', 'city_name', '城市', '监测城市'],
            'station_name': ['station_name', 'name', '站点名称', '监测站名称']
        }

        # 字段列映射
        field_mappings = {
            'pm25': ['pm25', 'pm2.5', 'pm_25', 'PM2.5', 'PM25'],
            'pm10': ['pm10', 'pm_10', 'PM10', 'PM_10'],
            'co2': ['co2', 'CO2', '二氧化碳'],
            'so2': ['so2', 'SO2', '二氧化硫'],
            'no2': ['no2', 'NO2', '二氧化氮'],
            'o3': ['o3', 'O3', '臭氧'],
            'aqi': ['aqi', 'AQI', '空气质量指数'],
            'temperature': ['temperature', 'temp', 'temperature_c', '温度'],
            'humidity': ['humidity', 'humidity_percent', '相对湿度'],
            'pressure': ['pressure', 'atmospheric_pressure', '气压'],
            'wind_speed': ['wind_speed', 'wind_speed_m_s', '风速'],
            'wind_direction': ['wind_direction', 'wind_dir', '风向']
        }

        # 检测时间列
        time_candidates = ['timestamp', 'time', 'date', 'datetime', '时间', '采样时间']
        for col in df.columns:
            if col.lower() in [c.lower() for c in time_candidates]:
                column_mapping['time'] = col
                break

        # 检测标签列
        for target, candidates in tag_mappings.items():
            for col in df.columns:
                if col.lower() in [c.lower() for c in candidates]:
                    column_mapping[target] = col
                    break

        # 检测字段列
        for target, candidates in field_mappings.items():
            for col in df.columns:
                if col.lower() in [c.lower() for c in candidates]:
                    column_mapping[target] = col
                    break

        return column_mapping

    def convert_to_standard_format(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        将DataFrame转换为标准格式

        Args:
            df: DataFrame
            column_mapping: 列名映射

        Returns:
            标准格式的数据列表
        """
        records = []

        for _, row in df.iterrows():
            record = {}

            # 处理时间戳
            time_col = column_mapping.get('time')
            if time_col and pd.notna(row[time_col]):
                record['timestamp'] = row[time_col]
            else:
                continue

            # 处理标签
            for tag in ['station_id', 'city', 'station_name']:
                col = column_mapping.get(tag)
                if col and pd.notna(row[col]):
                    record[tag] = str(row[col])
                else:
                    # 设置默认值
                    if tag == 'station_id':
                        record[tag] = 'default_station'
                    elif tag == 'city':
                        record[tag] = 'default_city'
                    elif tag == 'station_name':
                        record[tag] = 'default_station'

            # 处理字段
            for field in FIELDS:
                col = column_mapping.get(field)
                if col and pd.notna(row[col]):
                    record[field] = float(row[col])
                else:
                    record[field] = None

            records.append(record)

        return records

    def import_csv(self, file_path: str, measurement_name: str = None):
        """
        导入CSV文件到InfluxDB

        Args:
            file_path: CSV文件路径
            measurement_name: 测量名称
        """
        try:
            logger.info(f"开始导入文件: {file_path}")

            # 读取CSV
            df = pd.read_csv(file_path)
            logger.info(f"读取到 {len(df)} 行数据")

            # 清洗数据
            df = self.clean_dataframe(df)
            logger.info(f"清洗后剩余 {len(df)} 行数据")

            # 检测列
            column_mapping = self.detect_columns(df)
            logger.info(f"检测到的列映射: {column_mapping}")

            # 转换格式
            records = self.convert_to_standard_format(df, column_mapping)
            logger.info(f"转换为标准格式: {len(records)} 条记录")

            # 写入InfluxDB
            self.influx_manager.write_data(records, measurement_name)

            logger.info(f"成功导入 {len(records)} 条记录到 {measurement_name}")

        except Exception as e:
            logger.error(f"导入失败: {e}")
            raise

    def import_directory(self, directory_path: str, measurement_name: str = None):
        """
        导入目录中的所有CSV文件

        Args:
            directory_path: 目录路径
            measurement_name: 测量名称
        """
        csv_files = []
        for file in os.listdir(directory_path):
            if file.endswith('.csv'):
                csv_files.append(os.path.join(directory_path, file))

        logger.info(f"找到 {len(csv_files)} 个CSV文件")

        for csv_file in csv_files:
            try:
                self.import_csv(csv_file, measurement_name)
            except Exception as e:
                logger.error(f"导入文件 {csv_file} 失败: {e}")
                continue

    def close(self):
        """关闭连接"""
        self.influx_manager.close()


def main():
    """主函数：导入所有数据"""
    importer = DataImporter()

    # 导入不同数据集
    data_paths = [
        {
            'path': '/home/hansel/Documents/ITProject/Python/forcasting-system/data/stations_data',
            'measurement': 'BeiJing_stations_air_quality'
        }
    ]

    for data_info in data_paths:
        if os.path.exists(data_info['path']):
            logger.info(f"开始导入数据集: {data_info['path']}")
            if os.path.isdir(data_info['path']):
                importer.import_directory(data_info['path'], data_info['measurement'])
            else:
                importer.import_csv(data_info['path'], data_info['measurement'])
        else:
            logger.warning(f"数据路径不存在: {data_info['path']}")

    importer.close()
    logger.info("所有数据导入完成！")


if __name__ == "__main__":
    main()