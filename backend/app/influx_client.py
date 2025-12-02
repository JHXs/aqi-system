from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    INFLUXDB_URL,
    INFLUXDB_TOKEN,
    INFLUXDB_ORG,
    INFLUXDB_BUCKET,
    MEASUREMENT_NAME,
    TAGS,
    FIELDS,
    TIME_COLUMN
)
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class InfluxDBManager:
    def __init__(self):
        self.client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.bucket = INFLUXDB_BUCKET
        self.org = INFLUXDB_ORG

    def write_data(self, data: List[Dict[str, Any]], measurement_name: str = None):
        """
        写入数据到InfluxDB

        Args:
            data: 数据列表，每个字典包含标签、字段和时间戳
            measurement_name: 测量名称
        """
        if not data:
            return

        measurement = measurement_name or MEASUREMENT_NAME

        try:
            points = []
            for record in data:
                point = Point(measurement)

                # 添加标签
                for tag in TAGS:
                    if tag in record and record[tag] is not None:
                        point = point.tag(tag, str(record[tag]))

                # 添加字段
                for field in FIELDS:
                    if field in record and record[field] is not None:
                        point = point.field(field, record[field])

                # 添加时间戳
                if TIME_COLUMN in record:
                    point = point.time(record[TIME_COLUMN])

                points.append(point)

            self.write_api.write(bucket=self.bucket, org=self.org, record=points)
            logger.info(f"成功写入 {len(points)} 条记录到 {measurement}")

        except Exception as e:
            logger.error(f"写入数据失败: {e}")
            raise

    def query_data(self, query: str):
        """
        执行Flux查询

        Args:
            query: Flux查询语句

        Returns:
            查询结果
        """
        try:
            result = self.query_api.query(org=self.org, query=query)
            return result
        except Exception as e:
            logger.error(f"查询失败: {e}")
            raise

    def get_latest_data(self, station_id: str = None, limit: int = 100, measurement_name: str = None):
        """
        获取最新数据

        Args:
            station_id: 站点ID，如果为None则获取所有站点
            limit: 限制返回的记录数
            measurement_name: 测量名称，如果为None则使用默认值

        Returns:
            查询结果
        """
        measurement = measurement_name or MEASUREMENT_NAME
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: -30d)
          |> filter(fn: (r) => r._measurement == "{measurement}")
        '''

        if station_id:
            query += f'  |> filter(fn: (r) => r.station_id == "{station_id}")'

        query += f'''
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: {limit})
        '''

        return self.query_data(query)

    def get_data_by_time_range(self, start_time: str, end_time: str, station_id: str = None):
        """
        根据时间范围获取数据

        Args:
            start_time: 开始时间，如 "-1h", "-1d", "2024-01-01T00:00:00Z"
            end_time: 结束时间，如 "now()", "2024-01-01T23:59:59Z"
            station_id: 站点ID

        Returns:
            查询结果
        """
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {start_time}, stop: {end_time})
          |> filter(fn: (r) => r._measurement == "{MEASUREMENT_NAME}")
        '''

        if station_id:
            query += f'  |> filter(fn: (r) => r.station_id == "{station_id}")'

        query += '''
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''

        return self.query_data(query)

    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()