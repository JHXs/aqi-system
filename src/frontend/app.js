// WebSocket连接
let socket = null;
let isConnected = false;
let isPlaying = false;

// 图表实例
let pm25Chart = null;
let pm10Chart = null;
let coChart = null;

// 数据缓存
let timeData = [];
let pm25Data = [];
let pm10Data = [];
let coData = [];
let aqiData = [];
let tempData = [];
let humidityData = [];

// 最大显示点数
const MAX_POINTS = 100;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化图表
    initCharts();

    // 绑定事件
    document.getElementById('connectBtn').addEventListener('click', connectWebSocket);
    document.getElementById('playBtn').addEventListener('click', startStreaming);
    document.getElementById('pauseBtn').addEventListener('click', pauseStreaming);
    document.getElementById('resetBtn').addEventListener('click', resetData);

    // 播放速度控制
    const speedRange = document.getElementById('speedRange');
    const speedValue = document.getElementById('speedValue');

    speedRange.addEventListener('input', function() {
        speedValue.textContent = `${this.value}x`;
        setSpeed(parseFloat(this.value));
    });
});

// 初始化ECharts图表
function initCharts() {
    // PM2.5图表
    pm25Chart = echarts.init(document.getElementById('pm25Chart'));
    pm25Chart.setOption({
        title: {
            text: 'PM2.5 (μg/m³)',
            left: 'center',
            textStyle: {
                color: '#667eea'
            }
        },
        tooltip: {
            trigger: 'axis'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: timeData,
            axisLine: {
                lineStyle: {
                    color: '#667eea'
                }
            }
        },
        yAxis: {
            type: 'value',
            name: 'μg/m³',
            axisLine: {
                lineStyle: {
                    color: '#667eea'
                }
            }
        },
        series: [{
            name: 'PM2.5',
            type: 'line',
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {
                color: '#ff6b6b',
                width: 3
            },
            itemStyle: {
                color: '#ff6b6b'
            },
            areaStyle: {
                color: 'rgba(255, 107, 107, 0.1)'
            },
            data: pm25Data
        }]
    });

    // PM10图表
    pm10Chart = echarts.init(document.getElementById('pm10Chart'));
    pm10Chart.setOption({
        title: {
            text: 'PM10 (μg/m³)',
            left: 'center',
            textStyle: {
                color: '#667eea'
            }
        },
        tooltip: {
            trigger: 'axis'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: timeData,
            axisLine: {
                lineStyle: {
                    color: '#667eea'
                }
            }
        },
        yAxis: {
            type: 'value',
            name: 'μg/m³',
            axisLine: {
                lineStyle: {
                    color: '#667eea'
                }
            }
        },
        series: [{
            name: 'PM10',
            type: 'line',
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {
                color: '#4ecdc4',
                width: 3
            },
            itemStyle: {
                color: '#4ecdc4'
            },
            areaStyle: {
                color: 'rgba(78, 205, 196, 0.1)'
            },
            data: pm10Data
        }]
    });

    // CO图表
    coChart = echarts.init(document.getElementById('coChart'));
    coChart.setOption({
        title: {
            text: 'CO (mg/m³)',  // 改为 CO (一氧化碳)
            left: 'center',
            textStyle: {
                color: '#667eea'
            }
        },
        tooltip: {
            trigger: 'axis'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: timeData,
            axisLine: {
                lineStyle: {
                    color: '#667eea'
                }
            }
        },
        yAxis: {
            type: 'value',
            name: 'mg/m³',  // 改为 mg/m³
            axisLine: {
                lineStyle: {
                    color: '#667eea'
                }
            }
        },
        series: [{
            name: 'CO',
            type: 'line',
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {
                color: '#45b7d1',
                width: 3
            },
            itemStyle: {
                color: '#45b7d1'
            },
            areaStyle: {
                color: 'rgba(69, 183, 209, 0.1)'
            },
            data: coData
        }]
    });
}

// 连接WebSocket
function connectWebSocket() {
    const connectBtn = document.getElementById('connectBtn');
    const connectionStatus = document.getElementById('connectionStatus');

    if (!isConnected) {
        try {
            socket = new WebSocket('ws://localhost:8000/ws/stream');

            socket.onopen = function() {
                isConnected = true;
                connectionStatus.textContent = '已连接';
                connectionStatus.className = 'status-value connected';
                connectBtn.textContent = '断开连接';

                document.getElementById('playBtn').disabled = false;
                document.getElementById('pauseBtn').disabled = false;
                document.getElementById('resetBtn').disabled = false;

                updateStatus();
            };

            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                // 数据是数组格式，需要处理每个记录
                if (data && Array.isArray(data)) {
                    data.forEach(record => {
                        processData(record);
                    });
                } else if (data) {
                    processData(data);
                }
            };

            socket.onclose = function() {
                isConnected = false;
                connectionStatus.textContent = '已断开';
                connectionStatus.className = 'status-value disconnected';
                connectBtn.textContent = '连接';
                isPlaying = false;
                document.getElementById('playBtn').disabled = true;
                document.getElementById('pauseBtn').disabled = true;
                document.getElementById('resetBtn').disabled = true;
                document.getElementById('playStatus').textContent = '停止';

                updateStatus();
            };

            socket.onerror = function(error) {
                console.error('WebSocket错误:', error);
                alert('WebSocket连接失败，请检查后端服务是否正常运行');
            };

        } catch (error) {
            console.error('连接错误:', error);
            alert('连接失败: ' + error.message);
        }
    } else {
        // 断开连接
        if (socket) {
            socket.close();
        }
    }
}

// 处理接收到的数据
function processData(data) {
    if (!data || !data.timestamp) return;

    // 添加数据到数组
    timeData.push(formatTime(data.timestamp));
    pm25Data.push(data.pm25 || 0);
    pm10Data.push(data.pm10 || 0);
    coData.push(data.co || 0);  // 使用 co 字段（一氧化碳）
    aqiData.push(calculateAQI(data) || 0);  // 计算AQI
    tempData.push(data.temperature || 0);
    humidityData.push(data.humidity || 0);

    // 限制数据点数量
    if (timeData.length > MAX_POINTS) {
        timeData.shift();
        pm25Data.shift();
        pm10Data.shift();
        coData.shift();
        aqiData.shift();
        tempData.shift();
        humidityData.shift();
    }

    // 更新图表
    updateCharts();

    // 更新实时数据显示
    updateRealTimeData(data);

    // 更新状态
    updateStatus();
}

// 更新图表
function updateCharts() {
    pm25Chart.setOption({
        xAxis: { data: timeData },
        series: [{ data: pm25Data }]
    });

    pm10Chart.setOption({
        xAxis: { data: timeData },
        series: [{ data: pm10Data }]
    });

    coChart.setOption({
        xAxis: { data: timeData },
        series: [{ data: coData }]
    });
}

// 更新实时数据显示
function updateRealTimeData(data) {
    document.getElementById('pm25Value').textContent = data.pm25 ? data.pm25.toFixed(1) : '--';
    document.getElementById('pm10Value').textContent = data.pm10 ? data.pm10.toFixed(1) : '--';
    document.getElementById('coValue').textContent = data.co ? data.co.toFixed(1) : '--';  // 显示 CO (一氧化碳)
    document.getElementById('aqiValue').textContent = data.aqi ? data.aqi.toFixed(0) : '--';
    document.getElementById('tempValue').textContent = data.temperature ? data.temperature.toFixed(1) : '--';
    document.getElementById('humidityValue').textContent = data.humidity ? data.humidity.toFixed(0) : '--';
}

// 更新状态显示
function updateStatus() {
    document.getElementById('dataCount').textContent = timeData.length.toString();
    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
    document.getElementById('playStatus').textContent = isPlaying ? '播放中' : '停止';
}

// 开始播放
function startStreaming() {
    if (!isConnected) return;

    isPlaying = true;
    fetch('/api/control/play', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log('开始播放:', data);
            updateStatus();
        })
        .catch(error => {
            console.error('播放错误:', error);
        });
}

// 暂停播放
function pauseStreaming() {
    if (!isConnected) return;

    isPlaying = false;
    fetch('/api/control/pause', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log('暂停播放:', data);
            updateStatus();
        })
        .catch(error => {
            console.error('暂停错误:', error);
        });
}

// 重置数据
function resetData() {
    if (!isConnected) return;

    timeData = [];
    pm25Data = [];
    pm10Data = [];
    coData = [];
    aqiData = [];
    tempData = [];
    humidityData = [];

    updateCharts();
    updateRealTimeData({});
    updateStatus();

    fetch('/api/control/reset', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log('重置数据:', data);
        })
        .catch(error => {
            console.error('重置错误:', error);
        });
}

// 设置播放速度
function setSpeed(factor) {
    if (!isConnected) return;

    fetch(`/api/control/speed/${factor}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log('设置速度:', data);
        })
        .catch(error => {
            console.error('设置速度错误:', error);
        });
}

// 格式化时间显示
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
}

// 计算AQI（简化版本，主要基于PM2.5）
function calculateAQI(data) {
    const pm25 = data.pm25 || 0;
    const pm10 = data.pm10 || 0;
    const co = data.co || 0;
    const no2 = data.no2 || 0;
    const so2 = data.so2 || 0;
    const o3 = data.o3 || 0;

    // PM2.5 AQI 计算（简化）
    let aqi = 0;

    // PM2.5 AQI 计算（基于中国标准）
    if (pm25 <= 35) {
        aqi = Math.round((50 / 35) * pm25);
    } else if (pm25 <= 75) {
        aqi = Math.round(50 + (50 / 40) * (pm25 - 35));
    } else if (pm25 <= 115) {
        aqi = Math.round(100 + (50 / 40) * (pm25 - 75));
    } else if (pm25 <= 150) {
        aqi = Math.round(150 + (50 / 35) * (pm25 - 115));
    } else if (pm25 <= 250) {
        aqi = Math.round(200 + (100 / 100) * (pm25 - 150));
    } else if (pm25 <= 350) {
        aqi = Math.round(300 + (100 / 100) * (pm25 - 250));
    } else {
        aqi = Math.round(400 + (100 / 100) * (pm25 - 350));
    }

    // 基于其他污染物调整AQI
    // CO (mg/m³)
    let co_aqi = 0;
    if (co <= 2) {
        co_aqi = Math.round((50 / 2) * co);
    } else if (co <= 4) {
        co_aqi = Math.round(50 + (50 / 2) * (co - 2));
    } else if (co <= 14) {
        co_aqi = Math.round(100 + (50 / 10) * (co - 4));
    } else if (co <= 24) {
        co_aqi = Math.round(150 + (50 / 10) * (co - 14));
    } else if (co <= 36) {
        co_aqi = Math.round(200 + (100 / 12) * (co - 24));
    } else if (co <= 48) {
        co_aqi = Math.round(300 + (100 / 12) * (co - 36));
    } else {
        co_aqi = Math.round(400 + (100 / 12) * (co - 48));
    }

    // NO2 (µg/m³)
    let no2_aqi = 0;
    if (no2 <= 40) {
        no2_aqi = Math.round((50 / 40) * no2);
    } else if (no2 <= 80) {
        no2_aqi = Math.round(50 + (50 / 40) * (no2 - 40));
    } else if (no2 <= 180) {
        no2_aqi = Math.round(100 + (50 / 100) * (no2 - 80));
    } else if (no2 <= 280) {
        no2_aqi = Math.round(150 + (50 / 100) * (no2 - 180));
    } else if (no2 <= 565) {
        no2_aqi = Math.round(200 + (100 / 285) * (no2 - 280));
    } else if (no2 <= 750) {
        no2_aqi = Math.round(300 + (100 / 185) * (no2 - 565));
    } else {
        no2_aqi = Math.round(400 + (100 / 185) * (no2 - 750));
    }

    // SO2 (µg/m³)
    let so2_aqi = 0;
    if (so2 <= 20) {
        so2_aqi = Math.round((50 / 20) * so2);
    } else if (so2 <= 150) {
        so2_aqi = Math.round(50 + (50 / 130) * (so2 - 20));
    } else if (so2 <= 475) {
        so2_aqi = Math.round(100 + (50 / 325) * (so2 - 150));
    } else if (so2 <= 800) {
        so2_aqi = Math.round(150 + (50 / 325) * (so2 - 475));
    } else if (so2 <= 1600) {
        so2_aqi = Math.round(200 + (100 / 800) * (so2 - 800));
    } else if (so2 <= 2100) {
        so2_aqi = Math.round(300 + (100 / 500) * (so2 - 1600));
    } else {
        so2_aqi = Math.round(400 + (100 / 500) * (so2 - 2100));
    }

    // O3 (µg/m³)
    let o3_aqi = 0;
    if (o3 <= 100) {
        o3_aqi = Math.round((50 / 100) * o3);
    } else if (o3 <= 160) {
        o3_aqi = Math.round(50 + (50 / 60) * (o3 - 100));
    } else if (o3 <= 215) {
        o3_aqi = Math.round(100 + (50 / 55) * (o3 - 160));
    } else if (o3 <= 265) {
        o3_aqi = Math.round(150 + (50 / 50) * (o3 - 215));
    } else if (o3 <= 800) {
        o3_aqi = Math.round(200 + (100 / 535) * (o3 - 265));
    } else if (o3 <= 1000) {
        o3_aqi = Math.round(300 + (100 / 200) * (o3 - 800));
    } else {
        o3_aqi = Math.round(400 + (100 / 200) * (o3 - 1000));
    }

    // 取最大值作为最终AQI
    return Math.max(aqi, co_aqi, no2_aqi, so2_aqi, o3_aqi);
}

// 窗口大小改变时重新调整图表大小
window.addEventListener('resize', function() {
    if (pm25Chart) pm25Chart.resize();
    if (pm10Chart) pm10Chart.resize();
    if (coChart) coChart.resize();
});