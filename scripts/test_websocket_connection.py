#!/usr/bin/env python3
"""
WebSocket接口测试脚本
"""

import asyncio
import websockets
import json
import time

async def test_websocket():
    uri = "ws://localhost:8000/ws/stream"
    
    print(f"正在连接到 WebSocket: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功")
            
            # 等待几秒钟以接收数据
            print("等待接收数据...")
            
            # 发送一个播放请求的模拟
            print("请注意：您需要在浏览器中点击'开始播放'按钮")
            print("或者我们可以通过HTTP API发送播放请求...")
            
            import requests
            try:
                response = requests.post("http://localhost:8000/api/control/play")
                print(f"✅ 播放控制API调用结果: {response.status_code} - {response.json()}")
            except Exception as e:
                print(f"❌ 播放控制API调用失败: {e}")
            
            # 现在等待接收数据
            received_messages = 0
            start_time = time.time()
            timeout = 10  # 10秒超时
            
            while time.time() - start_time < timeout:
                try:
                    # 设置较短的超时时间来检查是否有数据
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    print(f"✅ 接收到消息 {received_messages + 1}: {message[:200]}...")
                    
                    # 尝试解析JSON
                    try:
                        data = json.loads(message)
                        print(f"   数据结构: {type(data)}")
                        if isinstance(data, list) and len(data) > 0:
                            print(f"   数据示例: {data[0]}")
                    except json.JSONDecodeError:
                        print(f"   ❌ 消息不是有效的JSON格式")
                    
                    received_messages += 1
                    
                    # 如果接收到了数据，可以提前结束
                    if received_messages >= 5:  # 只接收前5条数据
                        print("已接收到足够的测试数据")
                        break
                        
                except asyncio.TimeoutError:
                    print("⏳ 等待数据中... (可能正在播放暂停状态)")
                    continue
            
            print(f"\n📊 测试结果: 共接收 {received_messages} 条消息")
            
            if received_messages == 0:
                print("❌ 没有接收到任何数据，请检查:")
                print("  1. 前端是否点击了'开始播放'按钮")
                print("  2. 或者确认API控制端点是否正常工作")
            else:
                print("✅ WebSocket数据传输正常")
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket连接已关闭: {e}")
    except Exception as e:
        print(f"❌ WebSocket连接失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("WebSocket接口测试")
    print("=" * 50)
    asyncio.run(test_websocket())