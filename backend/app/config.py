# Air Quality Forecasting Platform Configuration

# InfluxDB 配置
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "super-secret-token-for-air-quality-platform"
INFLUXDB_ORG = "air-quality-org"
INFLUXDB_BUCKET = "air-quality-bucket"

# FastAPI 配置
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# WebSocket 推流配置
ACCELERATION_FACTOR = 0.5  # 播放加速因子，数值越小越快
BATCH_SIZE = 1  # 每次推送的数据条数

# 数据字段配置
MEASUREMENT_NAME = "air_quality"
TAGS = ["station_id", "city", "station_name"]
FIELDS = ["pm25", "pm10", "co2", "so2", "no2", "o3", "aqi", "temperature", "humidity", "pressure", "wind_speed", "wind_direction"]
TIME_COLUMN = "timestamp"

# 日志配置
LOG_LEVEL = "INFO"