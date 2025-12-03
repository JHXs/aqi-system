// WebSocket连接
let socket = null;
let isConnected = false;
let isPlaying = false;

// 图表实例
let pm25Chart = null;
let pm10Chart = null;
let co2Chart = null;

// 数据缓存
let timeData = [];
let pm25Data = [];
let pm10Data = [];
let co2Data = [];
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

    // CO2图表
    co2Chart = echarts.init(document.getElementById('co2Chart'));
    co2Chart.setOption({
        title: {
            text: 'CO2 (ppm)',
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
            name: 'ppm',
            axisLine: {
                lineStyle: {
                    color: '#667eea'
                }
            }
        },
        series: [{
            name: 'CO2',
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
            data: co2Data
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
                processData(data);
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
    co2Data.push(data.co2 || 0);
    aqiData.push(data.aqi || 0);
    tempData.push(data.temperature || 0);
    humidityData.push(data.humidity || 0);

    // 限制数据点数量
    if (timeData.length > MAX_POINTS) {
        timeData.shift();
        pm25Data.shift();
        pm10Data.shift();
        co2Data.shift();
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

    co2Chart.setOption({
        xAxis: { data: timeData },
        series: [{ data: co2Data }]
    });
}

// 更新实时数据显示
function updateRealTimeData(data) {
    document.getElementById('pm25Value').textContent = data.pm25 ? data.pm25.toFixed(1) : '--';
    document.getElementById('pm10Value').textContent = data.pm10 ? data.pm10.toFixed(1) : '--';
    document.getElementById('co2Value').textContent = data.co2 ? data.co2.toFixed(0) : '--';
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
    co2Data = [];
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

// 窗口大小改变时重新调整图表大小
window.addEventListener('resize', function() {
    if (pm25Chart) pm25Chart.resize();
    if (pm10Chart) pm10Chart.resize();
    if (co2Chart) co2Chart.resize();
});