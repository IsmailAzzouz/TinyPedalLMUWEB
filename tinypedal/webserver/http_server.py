#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2025 TinyPedal developers, see contributors.md file
#
#  This file is part of TinyPedal.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
HTTP server for serving web interface
"""

import logging
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

logger = logging.getLogger(__name__)


class HTTPServerHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler"""

    def __init__(self, *args, directory=None, **kwargs):
        """Initialize handler with custom directory"""
        self.custom_directory = directory
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format, *args):
        """Override to use Python logging"""
        logger.debug(f"HTTP: {format % args}")

    def end_headers(self):
        """Add CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()


class HTTPServerWrapper:
    """HTTP server wrapper for serving static files"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080, directory: str = None):
        """Initialize HTTP server
        
        Args:
            host: Server host address
            port: Server port number
            directory: Directory to serve files from
        """
        self.host = host
        self.port = port
        
        # Set directory to static folder
        if directory is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.directory = os.path.join(current_dir, "static")
        else:
            self.directory = directory
            
        self.server = None
        self.thread = None
        self.running = False

    def start(self):
        """Start HTTP server in separate thread"""
        if self.running:
            logger.warning("HTTP server already running")
            return

        # Ensure static directory exists
        os.makedirs(self.directory, exist_ok=True)

        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        logger.info(f"HTTP server starting on http://{self.host}:{self.port}")

    def _run_server(self):
        """Run HTTP server"""
        try:
            # Create handler with custom directory
            handler = lambda *args, **kwargs: HTTPServerHandler(
                *args, directory=self.directory, **kwargs
            )
            
            self.server = HTTPServer((self.host, self.port), handler)
            logger.info(f"HTTP server started on http://{self.host}:{self.port}")
            logger.info(f"Serving files from: {self.directory}")
            self.server.serve_forever()
        except Exception as e:
            logger.error(f"HTTP server error: {e}")
            self.running = False

    def stop(self):
        """Stop HTTP server"""
        if not self.running:
            return

        logger.info("Stopping HTTP server...")
        self.running = False
        
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        
        if self.thread:
            self.thread.join(timeout=2)
        
        logger.info("HTTP server stopped")


# Global HTTP server instance
http_server = HTTPServerWrapper()
