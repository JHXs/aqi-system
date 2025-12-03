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
- **Python 3.12+**
- **conda**
- **Docker**

### 2. 启动 InfluxDB

```bash
# 在项目根目录执行
docker-compose -f scripts/influxdb-docker-compose.yml up -d
```

访问 InfluxDB Web 界面：http://localhost:8086

### 3. 启动后端服务

```bash
# 激活 Conda 环境
conda activate aqi-pre

# 进入项目根目录
cd forcasting-system

# 安装依赖（如果还没有安装）
cd src/backend
pip install -r requirements.txt

# 启动 FastAPI 服务
pip install -e . # 项目根目录
python -m backend.app.main
```

服务启动在：http://localhost:8000

### 4. 导入数据

```bash
# 在 backend 目录执行
python -m backend.init_data
```

### 5. 访问前端页面

打开浏览器访问：http://localhost:8000/index.html

## 📊 功能特性

### 后端 API

- **WebSocket 实时推流**：`ws://localhost:8000/ws/stream`
- **最新数据查询**：`GET /api/latest?limit=...`
- **历史数据查询**：`GET /api/history?start=...&end=...`
- **服务状态**：`GET /api/status`
- **播放控制**：
  - `POST /api/control/play` - 开始播放
  - `POST /api/control/pause` - 暂停播放
  - `POST /api/control/reset` - 重置播放
  - `POST /api/control/speed/{factor}` - 设置播放速度

### 前端功能

- 📊 **实时曲线图**：PM2.5、PM10、CO2 实时数据
- 📋 **数据监控面板**：实时显示各项指标
- ⏯️ **播放控制**：开始/暂停/重置
- ⚡ **速度调节**：0.1x - 2.0x 可调
- 🌐 **响应式设计**：适配移动端

## 📁 项目结构

```
forcasting-system/
├── pyproject.toml            # 项目配置
├── README.md                 # 本文件
├── .gitignore               # Git 忽略配置
├── data/                    # 数据目录
│   ├── hezhou_air_data/     # 贺州空气质量数据
│   ├── microsoft_urban_air_data/  # Microsoft 城市空气质量数据
│   ├── stations_data/       # 北京站点空气质量数据
│   └── stations_data_gz/    # 广州站点空气质量数据
├── doc/                     # 文档
│   └── 技术栈研究.md        # 技术研究文档
├── scripts/                 # 脚本和配置文件
│   ├── influxdb-docker-compose.yml  # InfluxDB 配置
│   ├── test_influx_connection.py    # InfluxDB 连接测试
│   └── test_websocket_connection.py # WebSocket 连接测试
└── src/                     # 源代码目录
    ├── backend/             # 后端代码
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── config.py         # 配置文件
    │   │   ├── influx_client.py  # InfluxDB 客户端
    │   │   ├── data_importer.py  # 数据导入器
    │   │   └── main.py           # FastAPI 主服务
    │   ├── init_data.py          # 数据导入脚本
    │   ├── serve_frontend.py     # 静态文件服务器（可选）
    │   └── requirements.txt      # Python 依赖
    ├── frontend/            # 前端代码
    │   ├── index.html       # 主页面
    │   ├── app.js           # JavaScript 逻辑
    │   ├── style.css        # 样式文件
    │   └── libs/
    │       └── echarts.min.js   # ECharts 库
    └── forcasting_system.egg-info/  # 包信息
```

## 🔧 配置说明

### InfluxDB 配置

- **URL**: `http://localhost:8086`
- 用户名：`admin`
- 密码：`air_quality_2024`
- **Token**: `super-secret-token-for-air-quality-platform`
- **组织**: `air-quality-org`
- **Bucket**: `air_quality_hourly` (注意：与原 README 不同，实际代码中使用此名称)

### FastAPI 配置

- **主机**: `0.0.0.0`
- **端口**: `8000`
- **播放速度**: `0.5`（可调节）
- **批量大小**: `1`（每次推送的数据条数）

## 🎯 使用指南

### 1. 连接服务

1. 启动 InfluxDB: `docker-compose -f scripts/influxdb-docker-compose.yml up -d`
2. 在 backend 目录运行数据导入: `python -m backend.init_data`
3. 启动后端服务: `python -m backend.app.main`
4. 打开前端页面：http://localhost:8000/index.html
5. 点击"连接"按钮，连接状态显示"已连接"

### 2. 开始播放

1. 点击"开始播放"按钮或调用 API: `POST /api/control/play`
2. 实时数据开始推送
3. 图表实时更新

### 3. 调节速度

使用滑块调节播放速度（0.1x - 2.0x）或调用 API: `POST /api/control/speed/{factor}`

### 4. 其他控制

- **暂停**：暂停数据推送，点击暂停按钮或调用 `POST /api/control/pause`
- **重置**：清空图表数据并重置播放位置，点击重置按钮或调用 `POST /api/control/reset`

## 🛠️ 开发指南

### 添加新数据源

1. 将 CSV 文件放入 `data/` 目录下的相应子目录
2. 修改 `src/backend/init_data.py` 中的路径配置以指向新的数据目录
3. 运行 `python -m backend.init_data` 导入数据
4. 数据会自动导入到 InfluxDB

### 修改前端样式

编辑 `src/frontend/style.css` 文件

### 添加新图表

在 `src/frontend/app.js` 中添加新的 ECharts 配置

### 数据字段配置

在 `src/backend/app/config.py` 中可以修改数据字段配置：

```python
# 数据字段配置
FIELDS = ["pm25", "pm10", "co2", "so2", "no2", "o3", "co", "weather", "temperature", "humidity", "pressure", "wind_speed", "wind_direction"]
```

## 🐛 故障排除

### 1. InfluxDB 连接失败

```bash
# 检查容器状态
docker ps

# 重启容器
docker-compose -f scripts/influxdb-docker-compose.yml restart

# 检查容器日志
docker-compose -f scripts/influxdb-docker-compose.yml logs influxdb
```

### 2. 后端服务启动失败

```bash
# 检查端口占用
lsof -i :8000

# 杀死占用进程
kill -9 <PID>

# 检查 Python 环境和依赖
conda list  # 确保 aqi-pre 环境已激活
pip list    # 确保所有依赖已安装
```

### 3. 前端页面无法访问

确保后端服务已启动，前端页面通过后端提供服务，访问 `http://localhost:8000/index.html`

### 4. WebSocket 连接失败

检查后端服务是否正常运行，端口是否正确，以及浏览器控制台是否有错误信息

### 5. 数据导入失败

检查 CSV 文件路径和格式，确保包含正确的时间戳和数据列

## 📊 数据格式

### InfluxDB Measurement

```
measurement: air_quality
tags: station_id, city, station_name
fields: pm25, pm10, co2, so2, no2, o3, co, weather, temperature, humidity, pressure, wind_speed, wind_direction
timestamp: ISO 8601 格式
```

### WebSocket 消息格式

```json
{
  "timestamp": "2015-04-28T01:00:00+00:00",
  "station_id": "4.0",
  "city": "default_city",
  "pm25": 71.0,
  "pm10": 110.0,
  "co": 1.4,
  "so2": 33.0,
  "no2": 36.0,
  "o3": 70.0,
  "weather": 1.0,
  "temperature": 12.0,
  "humidity": 61.0,
  "pressure": 1017.0,
  "wind_speed": 2.0,
  "wind_direction": 140.0
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
- [Python](https://www.python.org/)
- [Docker](https://www.docker.com/)