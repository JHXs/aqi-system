from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from influx_client import InfluxDBManager
from config import ACCELERATION_FACTOR, BATCH_SIZE, FRONTEND_DIR, INFLUXDB_BUCKET, INFLUXDB_ORG, INFLUXDB_TOKEN, INFLUXDB_URL
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Air Quality Real-time Streaming API",
    description="空气质量实时数据流展示平台后端API",
    version="1.0.0"
)

# 允许跨域请求（前端页面在不同端口时需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
# frontend_path = FRONTEND_DIR
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
    logger.info(f"已挂载静态文件目录: {FRONTEND_DIR}")

# 全局变量
influx_manager = InfluxDBManager(
    influx_url=INFLUXDB_URL,
    influx_bucket=INFLUXDB_BUCKET,
    influx_org=INFLUXDB_ORG,
    influx_token=INFLUXDB_TOKEN
)
data_cache = []
current_index = 0
is_playing = False
clients = set()


@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("启动空气质量实时数据流服务...")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    influx_manager.close()
    logger.info("关闭服务...")


@app.get("/")
async def root():
    """根路径返回简单的API信息"""
    return {
        "message": "Air Quality Real-time Streaming API",
        "version": "1.0.0",
        "endpoints": {
            "WebSocket": "/ws/stream",
            "History": "/api/history?start=...&end=...",
            "Latest": "/api/latest?limit=...",
            "Status": "/api/status"
        },
        "frontend": "/index.html"
    }


@app.get("/index.html")
async def serve_frontend():
    """提供前端页面"""
    # 获取frontend目录
    frontend_path = os.path.join(FRONTEND_DIR, "index.html")

    logger.info(f"尝试加载前端文件: {frontend_path}")

    if os.path.exists(frontend_path):
        with open(frontend_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        logger.error(f"前端文件未找到: {frontend_path}")
        return {"error": "前端文件未找到", "path": frontend_path}


@app.get("/api/status")
async def get_status():
    """获取服务状态"""
    return {
        "status": "running",
        "influxdb_connected": True,
        "clients": len(clients),
        "is_playing": is_playing,
        "current_index": current_index,
        "data_cache_size": len(data_cache)
    }


@app.get("/api/latest")
async def get_latest_data(limit: int = 100):
    """获取最新的空气质量数据"""
    try:
        # 由于数据是2014-2015年的历史数据，查询较早的时间范围
        # 查询最近的历史数据并限制返回数量，然后使用pivot将字段转为列
        result = influx_manager.get_data(start_time="2014-01-01T00:00:00Z", limit=limit, sort_desc=True, pivot_data=True)
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
async def get_history_data(start: str, end: str = "now()", station_id: str = None):
    """获取历史数据"""
    try:
        # The original get_data_by_time_range did pivot the data
        result = influx_manager.get_data(start_time=start, end_time=end, station_id=station_id, pivot_data=True)
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/control/play")
async def control_play():
    """开始播放数据流"""
    global is_playing
    is_playing = True
    return {"message": "开始播放数据流"}


@app.post("/api/control/pause")
async def control_pause():
    """暂停播放数据流"""
    global is_playing
    is_playing = False
    return {"message": "暂停播放数据流"}


@app.post("/api/control/reset")
async def control_reset():
    """重置播放位置"""
    global current_index, is_playing
    current_index = 0
    is_playing = False
    return {"message": "重置播放位置"}


@app.post("/api/control/speed/{factor}")
async def control_speed(factor: float):
    """设置播放速度"""
    global ACCELERATION_FACTOR
    ACCELERATION_FACTOR = factor
    return {"message": f"播放速度设置为 {factor}"}


@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时数据流端点"""
    global clients, is_playing, current_index, data_cache

    await websocket.accept()
    clients.add(websocket)
    logger.info(f"新客户端连接，当前连接数: {len(clients)}")

    try:
        # 如果缓存为空，加载数据
        if not data_cache:
            await load_data_cache()

        # 开始推送数据
        is_playing = True
        while True:
            if is_playing and data_cache:
                # 获取下一批数据
                batch_data = get_next_batch()
                if batch_data:
                    # 推送给客户端
                    await websocket.send_text(json.dumps(batch_data))

                # 控制播放速度
                await asyncio.sleep(ACCELERATION_FACTOR)
            else:
                # 暂停状态，等待1秒后重试
                await asyncio.sleep(1)

    except WebSocketDisconnect:
        clients.remove(websocket)
        logger.info(f"客户端断开连接，当前连接数: {len(clients)}")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        clients.remove(websocket)


def get_next_batch() -> List[Dict[str, Any]]:
    """获取下一批数据"""
    global current_index, data_cache

    if not data_cache:
        return []

    batch = []
    for _ in range(BATCH_SIZE):
        if current_index >= len(data_cache):
            # 循环播放
            current_index = 0
            logger.info("数据播放完成，重新开始")

        record = data_cache[current_index]
        batch.append(record)
        current_index += 1

    return batch


async def load_data_cache():
    """加载数据到缓存"""
    global data_cache, current_index

    try:
        logger.info("正在加载数据到缓存...")
        # 获取最近的数据，format_query_result 需要未透视的数据
        # 对于历史数据，需要指定足够早的开始时间
        result = influx_manager.get_data(start_time="2014-01-01T00:00:00Z", limit=10000, sort_desc=False)  # 使用升序，以便按时间顺序播放
        data_cache = format_query_result(result)
        current_index = 0
        logger.info(f"成功加载 {len(data_cache)} 条数据到缓存")
    except Exception as e:
        logger.error(f"加载数据失败: {e}")
        data_cache = []


def format_query_result(result) -> List[Dict[str, Any]]:
    """格式化查询结果"""
    formatted_data = []

    try:
        # 按时间戳和station_id分组
        data_by_timestamp = {}

        for table in result:
            for record in table.records:

                timestamp = record.get_time().isoformat()
                station_id = record.values.get("station_id") or "unknown"
                city = record.values.get("city") or "unknown"

                key = (timestamp, station_id)
                if key not in data_by_timestamp:
                    data_by_timestamp[key] = {
                        "timestamp": timestamp,
                        "station_id": station_id,
                        "city": city
                    }

                # 添加字段值
                field_name = record.get_field()
                field_value = record.get_value()
                if field_value is not None:
                    data_by_timestamp[key][field_name] = field_value

        # 转换为列表并按时间排序
        formatted_data = list(data_by_timestamp.values())
        formatted_data.sort(key=lambda x: x["timestamp"])

    except Exception as e:
        logger.error(f"格式化查询结果失败: {e}")

    return formatted_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )