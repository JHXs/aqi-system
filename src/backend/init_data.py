#!/usr/bin/env python3
"""
Air Quality Platform - 数据导入脚本
使用方法:
    python init_data.py
"""
import os
from backend.app.data_importer import DataImporter
from backend.app.config import PROJECT_DIR

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    importer = DataImporter()

    data_paths = [
        {
            'path': PROJECT_DIR / "data" / "stations_data_gz",
            'measurement': "air_quality"
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