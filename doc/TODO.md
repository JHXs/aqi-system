1. 环境搭建：安装Python、InfluxDB、FastAPI、ECharts
2. 数据导入：编写CSV到InfluxDB的导入脚本
3. 后端API：实现WebSocket推流服务
4. 前端页面：创建基础的ECharts图表页面
5. 联调测试：连接前后端，验证数据流
6. 优化完善：添加UI美化、错误处理等

# 环境搭建

## 安装 python 依赖环境

```shell
uv pip install fastapi uvicorn[standard] influxdb-client python-multipart jinja2 httpx
```

## docker 部署 InfluxDB 数据库

### compose 文件

```yaml
version: '3.8'

services:
  influxdb:
    image: influxdb:2.7
    container_name: influxdb-air-quality
    restart: unless-stopped
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=air_quality_2024
      - DOCKER_INFLUXDB_INIT_ORG=air-quality-org
      - DOCKER_INFLUXDB_INIT_BUCKET=air-quality-bucket
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=super-secret-token-for-air-quality-platform
    volumes:
      - influxdb-data:/var/lib/influxdb2
      - ./influxdb/config:/etc/influxdb2
    networks:
      - air-quality-network

  # 可选：添加Grafana用于可视化（如果您想对比）
  # grafana:
  #   image: grafana/grafana:latest
  #   container_name: grafana-air-quality
  #   restart: unless-stopped
  #   ports:
  #     - "3000:3000"
  #   environment:
  #     - GF_SECURITY_ADMIN_PASSWORD=admin
  #   volumes:
  #     - grafana-data:/var/lib/grafana
  #   networks:
  #     - air-quality-network
  #   depends_on:
  #     - influxdb

volumes:
  influxdb-data:
    driver: local
  # grafana-data:
  #   driver: local

networks:
  air-quality-network:
    driver: bridge
```

关键配置项：

1. 端口映射：8086:8086 - InfluxDB的API端口
2. 数据持久化：influxdb-data 卷存储数据库数据
3. 初始化配置：
   - 用户名：admin
   - 密码：air_quality_2024
   - 组织：air-quality-org
   - Bucket：air-quality-bucket
   - Token：super-secret-token-for-air-quality-platform

```text
  启动命令：

  # 在项目根目录执行
  cd /home/hansel/Documents/ITProject/Python/forcasting-system
  docker-compose up -d

  验证启动：

  # 查看容器状态
  docker ps

  # 查看日志
  docker logs influxdb-air-quality

  # 访问InfluxDB Web界面
  # 浏览器打开: http://localhost:8086
```
