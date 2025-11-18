#!/usr/bin/env python3
"""
Web server with reverse proxy for API
Serves HTML interface and proxies API requests to backend
"""
import http.server
import socketserver
import urllib.request
import urllib.error
import json
import os
from config import Config

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with API reverse proxy"""

    def do_GET(self):
        # Proxy API requests to backend
        if self.path.startswith('/api/') or self.path.startswith('/health'):
            self.proxy_request('GET')
        elif self.path == '/' or self.path == '/index.html':
            # Serve index.html with relative API URLs
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            with open('index.html', 'r') as f:
                html_content = f.read()

            # Use relative URLs (same host/port) instead of separate API port
            html_content = html_content.replace(
                "const API_URL = window.location.protocol + '//' + window.location.hostname + ':' + apiPort;",
                "const API_URL = window.location.protocol + '//' + window.location.hostname + ':' + window.location.port;"
            )

            self.wfile.write(html_content.encode())
        else:
            # Serve other static files normally
            super().do_GET()

    def do_POST(self):
        # Proxy API POST requests to backend
        if self.path.startswith('/api/'):
            self.proxy_request('POST')
        else:
            self.send_error(404)

    def proxy_request(self, method):
        """Proxy request to API backend"""
        try:
            # Get API backend URL from environment or use default
            api_host = os.environ.get('API_HOST', 'chatbot-api')
            api_port = os.environ.get('FLASK_PORT', '5000')
            api_url = f"http://{api_host}:{api_port}{self.path}"

            # Prepare request
            if method == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                req = urllib.request.Request(
                    api_url,
                    data=body,
                    headers={'Content-Type': 'application/json'}
                )
            else:
                req = urllib.request.Request(api_url)

            # Forward request to API (600s = 10min timeout for slow LLM inference)
            with urllib.request.urlopen(req, timeout=600) as response:
                # Send response back to client
                self.send_response(response.status)

                # Forward headers
                for header, value in response.headers.items():
                    if header.lower() not in ['transfer-encoding', 'connection']:
                        self.send_header(header, value)
                self.end_headers()

                # Forward body
                self.wfile.write(response.read())

        except urllib.error.HTTPError as e:
            # Forward error response
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(e.read())

        except Exception as e:
            # Server error
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({'error': f'Proxy error: {str(e)}'})
            self.wfile.write(error_response.encode())

def main():
    config = Config()
    port = config.WEB_SERVER_PORT

    handler = ProxyHTTPRequestHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"=" * 60)
        print(f"Web Server with API Proxy Starting")
        print(f"=" * 60)
        print(f"Serving at: http://0.0.0.0:{port}")
        print(f"API proxied from: http://chatbot-api:{config.FLASK_PORT}")
        print(f"Single port access - API and Web on same port!")
        print(f"\nPress Ctrl+C to stop")
        print(f"=" * 60)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down web server...")
            httpd.shutdown()

if __name__ == "__main__":
    main()
