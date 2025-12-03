#!/usr/bin/env python3
"""
Air Quality Platform - 数据导入脚本
使用方法:
    python init_data.py
"""

import pandas as pd
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import glob
import os
from datetime import datetime
import logging
from app.config import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET, PROJECT_DIR

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AirQualityImporter:
    def __init__(self, influx_url, influx_token, influx_org, influx_bucket):
        self.client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.bucket = influx_bucket
        self.success_count = 0
        self.fail_count = 0
        
    def process_csv_file(self, file_path):
        """处理单个CSV文件，包含错误处理和格式自动检测"""
        file_name = os.path.basename(file_path)
        station_id = file_name.replace('.csv', '').replace('df_station_', '')
        
        try:
            logging.info(f"开始处理 {file_name}...")
            
            # 读取CSV文件
            df = pd.read_csv(file_path)
            
            # 自动检测并转换时间格式（最健壮的方式）
            df['time'] = pd.to_datetime(df['time'], errors='coerce')
            
            # 检查是否有无效时间
            if df['time'].isnull().any():
                logging.warning(f"{file_name} 中有 {df['time'].isnull().sum()} 条无效时间记录，将被跳过")
                df = df.dropna(subset=['time'])
            
            # 构建InfluxDB数据点
            points = []
            for _, row in df.iterrows():
                try:
                    point = Point("air_quality") \
                        .tag("station_id", str(row['station_id'])) \
                        .field("pm25", float(row['PM25_Concentration'])) \
                        .field("pm10", float(row['PM10_Concentration'])) \
                        .field("no2", float(row['NO2_Concentration'])) \
                        .field("co", float(row['CO_Concentration'])) \
                        .field("o3", float(row['O3_Concentration'])) \
                        .field("so2", float(row['SO2_Concentration'])) \
                        .field("weather", int(row['weather'])) \
                        .field("temperature", float(row['temperature'])) \
                        .field("pressure", float(row['pressure'])) \
                        .field("humidity", float(row['humidity'])) \
                        .field("wind_speed", float(row['wind_speed'])) \
                        .field("wind_direction", int(row['wind_direction'])) \
                        .time(row['time'])
                    points.append(point)
                except Exception as e:
                    logging.error(f"处理数据行失败: {e}, row: {row.to_dict()}")
                    continue
            
            # 批量写入
            if points:
                self.write_api.write(bucket=self.bucket, record=points)
                self.success_count += 1
                logging.info(f"✅ 成功导入 {station_id}: {len(points)} 条数据")
            else:
                logging.warning(f"{file_name} 没有有效数据")
                
        except Exception as e:
            self.fail_count += 1
            logging.error(f"❌ 处理 {file_name} 失败: {e}")
            return False
        
        return True
    
    def batch_import(self, csv_directory):
        """批量处理所有CSV文件"""
        csv_files = glob.glob(f"{csv_directory}/df_station_*.csv")
        logging.info(f"发现 {len(csv_files)} 个监测站数据文件")
        
        for file_path in csv_files:
            self.process_csv_file(file_path)
        
        # 总结
        logging.info(f"\n{'='*50}")
        logging.info(f"导入完成！成功: {self.success_count}, 失败: {self.fail_count}")
        logging.info(f"{'='*50}")
    
    def __del__(self):
        """关闭连接"""
        if hasattr(self, 'client'):
            self.client.close()

# 使用示例
if __name__ == "__main__":
    importer = AirQualityImporter(
        influx_url=INFLUXDB_URL,
        influx_token=INFLUXDB_TOKEN,
        influx_org=INFLUXDB_ORG,
        influx_bucket=INFLUXDB_BUCKET
    )
    try:
        importer.batch_import(f"{PROJECT_DIR}/data/stations_data")
    except KeyboardInterrupt:
        logging.info("\n用户中断，正在退出...")
    finally:
        del importer