# Air Quality Real-time Streaming Platform

空气质量实时数据流展示平台

## 🚀 环境搭建完成

### 已创建的文件结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # 配置文件
│   ├── influx_client.py       # InfluxDB客户端
│   ├── data_importer.py       # 数据导入器
│   └── main.py                # FastAPI主服务
├── init_data.py               # 数据导入脚本
├── requirements.txt           # Python依赖
└── README.md                  # 本文件

frontend/
└── (待创建)

docker-compose.yml             # InfluxDB配置
environment.yml                # Conda环境配置
```

## 📋 已完成的步骤

### ✅ 1. 项目目录结构
- 已创建完整的后端目录结构

### ✅ 2. Conda环境
- 环境名称: `aqi-pre`
- 已安装FastAPI、InfluxDB客户端、Pandas等依赖

### ✅ 3. InfluxDB
- 已通过Docker Compose部署
- 端口: 8086
- 用户名: admin
- 密码: air_quality_2024
- 组织: air-quality-org
- Bucket: air-quality-bucket

### ✅ 4. 基础配置文件
- `config.py`: 包含所有配置项
- `influx_client.py`: InfluxDB操作封装
- `data_importer.py`: CSV数据导入工具
- `main.py`: FastAPI WebSocket服务

## 🚧 下一步：启动应用

### 1. 激活Conda环境
```bash
conda activate aqi-pre
```

### 2. 安装Python依赖
```bash
cd backend
uv pip install -r requirements.txt
```

### 3. 导入数据到InfluxDB
```bash
cd backend
python init_data.py
```

### 4. 启动FastAPI服务
```bash
cd backend
python app/main.py
```
或
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔧 服务信息

### API端点
- **根路径**: http://localhost:8000/
- **WebSocket流**: ws://localhost:8000/ws/stream
- **最新数据**: GET /api/latest?limit=100
- **历史数据**: GET /api/history?start=-1h&end=now()
- **服务状态**: GET /api/status

### 控制接口
- **开始播放**: POST /api/control/play
- **暂停播放**: POST /api/control/pause
- **重置位置**: POST /api/control/reset
- **设置速度**: POST /api/control/speed/0.5

## 📊 数据结构

### InfluxDB Measurement
```
measurement: air_quality
tags: station_id, city, station_name
fields: pm25, pm10, co2, so2, no2, o3, aqi, temperature, humidity, pressure, wind_speed, wind_direction
timestamp: ISO 8601格式
```

### WebSocket消息格式
```json
{
  "timestamp": "2024-01-01T01:00:00Z",
  "station_id": "001",
  "city": "贺州",
  "station_name": "市中心站",
  "pm25": 35,
  "pm10": 48,
  "co2": 430,
  "aqi": 85
}
```

## 🎯 接下来需要做什么

1. ✅ **导入数据** - 运行 `python init_data.py`
2. ✅ **启动后端** - 运行 `python app/main.py`
3. 🚧 **创建前端页面** - 实现ECharts实时图表
4. 🔄 **测试数据流** - 连接WebSocket查看数据

## 🔍 常见问题

### InfluxDB连接失败
- 确保Docker容器运行: `docker ps`
- 检查端口是否被占用: `netstat -an | grep 8086`

### 数据导入失败
- 检查CSV文件路径是否正确
- 确认CSV文件格式是否包含时间列和数据列

### WebSocket连接失败
- 确认FastAPI服务已启动
- 检查防火墙设置

## 📞 支持

如有问题，请查看：
- InfluxDB Web界面: http://localhost:8086
- FastAPI文档: http://localhost:8000/docs