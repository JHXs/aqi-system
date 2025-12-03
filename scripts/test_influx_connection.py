#!/usr/bin/env python3
"""
Test script to check InfluxDB connection and data
"""

from influxdb_client import InfluxDBClient
import sys
import os

# Add project path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.config import (
    INFLUXDB_URL,
    INFLUXDB_TOKEN,
    INFLUXDB_ORG,
    INFLUXDB_BUCKET,
    MEASUREMENT_NAME
)

def test_connection():
    print("Testing InfluxDB connection...")
    print(f"URL: {INFLUXDB_URL}")
    print(f"Org: {INFLUXDB_ORG}")
    print(f"Bucket: {INFLUXDB_BUCKET}")
    print(f"Measurement: {MEASUREMENT_NAME}")
    
    try:
        # Create client
        client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        
        # Test connection
        health = client.health()
        print(f"Health status: {health.status}")
        
        # Query API
        query_api = client.query_api()
        
        # Test query to check if bucket exists and has data
        query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -1h) |> limit(n: 1)'
        result = query_api.query(org=INFLUXDB_ORG, query=query)

        print(f"Query result (last 1h): {len(result)} tables")

        if result:
            print("Data found in bucket (last 1h)!")
            for table in result:
                for record in table.records:
                    print(f"Sample record: time={record.get_time()}, field={record.get_field()}, value={record.get_value()}")
                    print(f"Record tags: {record.values}")
                    break  # Only show first record
                break
        else:
            print("No data found in the bucket for the last hour.")
            # Try a wider time range for historical data (2014-2015)
            historical_query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: 2014-01-01T00:00:00Z, stop: 2016-01-01T00:00:00Z) |> limit(n: 1)'
            historical_result = query_api.query(org=INFLUXDB_ORG, query=historical_query)
            if historical_result:
                print("Historical data found (2014-2015)!")
                for table in historical_result:
                    for record in table.records:
                        print(f"Sample historical record: time={record.get_time()}, field={record.get_field()}, value={record.get_value()}")
                        print(f"Record tags: {record.values}")
                        break
                    break
            else:
                print("No historical data found in the bucket (2014-2015).")

                # Try even wider time range
                wider_query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -30d) |> limit(n: 1)'
                result_all = query_api.query(org=INFLUXDB_ORG, query=wider_query)
                if result_all:
                    print("Data found with wider time range!")
                    for table in result_all:
                        for record in table.records:
                            print(f"Sample record: time={record.get_time()}, field={record.get_field()}, value={record.get_value()}")
                            print(f"Record tags: {record.values}")
                            break
                        break
                else:
                    print("No data found in the bucket at all.")
                
        # Check specific measurement
        measurement_query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -30d) |> filter(fn: (r) => r._measurement == "{MEASUREMENT_NAME}") |> limit(n: 1)'
        measurement_result = query_api.query(org=INFLUXDB_ORG, query=measurement_query)
        
        print(f"Measurement '{MEASUREMENT_NAME}' result: {len(measurement_result)} tables")
        if measurement_result:
            print(f"Found data for measurement '{MEASUREMENT_NAME}'")
        else:
            print(f"No data found for measurement '{MEASUREMENT_NAME}'")
        
        client.close()
        
    except Exception as e:
        print(f"Error connecting to InfluxDB: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()