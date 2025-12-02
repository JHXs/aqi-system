# 🌬️ 空气质量实时数据流展示平台

基于 **InfluxDB + FastAPI + WebSocket + ECharts** 的空气质量实时数据流展示平台

## 📋 项目概述

本项目实现了：
- ✅ **数据存储**：InfluxDB 时间序列数据库
- ✅ **后端服务**：FastAPI + WebSocket 实时推流
- ✅ **前端展示**：ECharts 实时可视化
- ✅ **数据导入**：CSV 自动导入到 InfluxDB

## 🚀 快速开始

### 1. 环境准备

确保已安装：
- **Python 3.10+**
- **conda**
- **Docker**

### 2. 启动 InfluxDB

```bash
# 在项目根目录执行
docker-compose up -d
```

访问 InfluxDB Web 界面：http://localhost:8086

### 3. 启动后端服务

```bash
# 激活 Conda 环境
conda activate aqi-pre

# 进入后端目录
cd backend

# 安装依赖（如果还没有安装）
pip install -r requirements.txt

# 启动 FastAPI 服务
python app/main.py
```

服务启动在：http://localhost:8000

### 4. 导入数据

```bash
# 在 backend 目录执行
python init_data.py
```

### 5. 访问前端页面

打开浏览器访问：http://localhost:8000/index.html

## 📊 功能特性

### 后端 API

- **WebSocket 实时推流**：`ws://localhost:8000/ws/stream`
- **最新数据查询**：`GET /api/latest?limit=...`
- **历史数据查询**：`GET /api/history?start=...&end=...`
- **服务状态**：`GET /api/status`

### 前端功能

- 📊 **实时曲线图**：PM2.5、PM10、CO2 实时数据
- 📋 **数据监控面板**：实时显示各项指标
- ⏯️ **播放控制**：开始/暂停/重置
- ⚡ **速度调节**：0.1x - 2.0x 可调
- 🌐 **响应式设计**：适配移动端

## 📁 项目结构

```
forcasting-system/
├── backend/                  # 后端代码
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py         # 配置文件
│   │   ├── influx_client.py  # InfluxDB 客户端
│   │   ├── data_importer.py  # 数据导入器
│   │   └── main.py           # FastAPI 主服务
│   ├── init_data.py          # 数据导入脚本
│   ├── serve_frontend.py     # 静态文件服务器（可选）
│   └── requirements.txt      # Python 依赖
├── frontend/                 # 前端代码
│   ├── index.html            # 主页面
│   ├── app.js               # JavaScript 逻辑
│   ├── style.css            # 样式文件
│   └── libs/
│       └── echarts.min.js   # ECharts 库
├── data/                     # 数据目录
│   ├── hezhou_air_data/     # 贺州空气质量数据
│   ├── microsoft_urban_air_data/  # Microsoft 城市空气质量数据
│   └── stations_data/       # 北京站点空气质量数据
│   └── stations_data_gz/    # 广州站点空气质量数据
├── doc/                      # 文档
└── scripts                  # 存储一些脚本或配置文件
    └── influxdb-docker-compose.yml  # InfluxDB 配置       
```

## 🔧 配置说明

### InfluxDB 配置

- **URL**: `http://localhost:8086`
- **Token**: `super-secret-token-for-air-quality-platform`
- **组织**: `air-quality-org`
- **Bucket**: `air-quality-bucket`

### FastAPI 配置

- **主机**: `0.0.0.0`
- **端口**: `8000`
- **播放速度**: `0.5`（可调节）

## 🎯 使用指南

### 1. 连接服务

1. 打开前端页面：http://localhost:8000/index.html
2. 点击"连接"按钮
3. 连接状态显示"已连接"

### 2. 开始播放

1. 点击"开始播放"按钮
2. 实时数据开始推送
3. 图表实时更新

### 3. 调节速度

使用滑块调节播放速度（0.1x - 2.0x）

### 4. 其他控制

- **暂停**：暂停数据推送
- **重置**：清空图表数据并重置播放位置

## 🛠️ 开发指南

### 添加新数据源

1. 将 CSV 文件放入 `data/` 目录
2. 运行 `python init_data.py` 导入数据
3. 数据会自动导入到 InfluxDB

### 修改前端样式

编辑 `frontend/style.css` 文件

### 添加新图表

在 `frontend/app.js` 中添加新的 ECharts 配置

## 🐛 故障排除

### 1. InfluxDB 连接失败

```bash
# 检查容器状态
docker ps

# 重启容器
docker-compose restart influxdb
```

### 2. 后端服务启动失败

```bash
# 检查端口占用
lsof -i :8000

# 杀死占用进程
kill -9 <PID>
```

### 3. 前端页面无法访问

确保后端服务已启动，前端页面通过后端提供服务

### 4. WebSocket 连接失败

检查后端服务是否正常运行，端口是否正确

## 📊 数据格式

### InfluxDB Measurement

```
measurement: air_quality
tags: station_id, city, station_name
fields: pm25, pm10, co2, so2, no2, o3, aqi, temperature, humidity, pressure, wind_speed, wind_direction
timestamp: ISO 8601 格式
```

### WebSocket 消息格式

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

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [InfluxDB](https://www.influxdata.com/)
- [ECharts](https://echarts.apache.org/)