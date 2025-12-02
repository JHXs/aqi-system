#!/usr/bin/env python3
"""
简单的HTTP服务器用于托管前端文件
"""

import http.server
import socketserver
import os
import webbrowser
import threading
import time

PORT = 8080
DIRECTORY = "frontend"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    """启动HTTP服务器"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"前端服务器启动在 http://localhost:{PORT}")
        print(f"目录: {os.path.abspath(DIRECTORY)}")
        print("按 Ctrl+C 停止服务器")

        # 自动打开浏览器
        def open_browser():
            time.sleep(1)
            webbrowser.open(f'http://localhost:{PORT}/index.html')

        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")

if __name__ == "__main__":
    start_server()