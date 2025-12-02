#!/usr/bin/env python3
"""
Air Quality Platform - 数据导入脚本
使用方法:
    python init_data.py
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.data_importer import DataImporter


def main():
    print("=== Air Quality Platform - 数据导入工具 ===\n")

    importer = DataImporter()

    # 导入数据集
    data_sets = [
        {
            'name': '北京站点空气质量数据',
            'path': 'data/stations_data',
            'measurement': 'BeiJing_stations_air_quality'
        }
    ]

    for data_set in data_sets:
        print(f"正在导入: {data_set['name']}")
        print(f"数据路径: {data_set['path']}")
        print(f"测量名称: {data_set['measurement']}")

        try:
            if os.path.isdir(data_set['path']):
                importer.import_directory(data_set['path'], data_set['measurement'])
            else:
                importer.import_csv(data_set['path'], data_set['measurement'])

            print(f"✅ {data_set['name']} 导入成功\n")
        except Exception as e:
            print(f"❌ {data_set['name']} 导入失败: {e}\n")
            continue

    importer.close()
    print("=== 数据导入完成 ===")


if __name__ == "__main__":
    main()