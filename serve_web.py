#!/usr/bin/env python3
"""
Web server for serving the HTML interface
Automatically reads port from .env and injects API port into HTML
"""
import http.server
import socketserver
import os
from config import Config

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler that injects API port into index.html"""
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            # Serve index.html with API port injected
            config = Config()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Read index.html and inject API port
            with open('index.html', 'r') as f:
                html_content = f.read()
            
            # Replace the API port line
            html_content = html_content.replace(
                "const apiPort = urlParams.get('api_port') || '5000';",
                f"const apiPort = urlParams.get('api_port') || '{config.FLASK_PORT}';"
            )
            
            self.wfile.write(html_content.encode())
        else:
            # Serve other files normally
            super().do_GET()

def main():
    config = Config()
    port = config.WEB_SERVER_PORT
    
    handler = CustomHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"=" * 60)
        print(f"Web Server Starting")
        print(f"=" * 60)
        print(f"Serving at: http://0.0.0.0:{port}")
        print(f"API configured for port: {config.FLASK_PORT}")
        print(f"\nPress Ctrl+C to stop")
        print(f"=" * 60)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down web server...")
            httpd.shutdown()

if __name__ == "__main__":
    main()
