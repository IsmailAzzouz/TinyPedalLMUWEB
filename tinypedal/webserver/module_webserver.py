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
Web server manager module for TinyPedal
"""

import logging

from ..module._base import DataModule
from .websocket_server import ws_server
from .http_server import http_server

logger = logging.getLogger(__name__)


class Realtime(DataModule):
    """Web server manager module
    
    This module starts WebSocket and HTTP servers and broadcasts
    telemetry data to connected web clients.
    """

    def __init__(self, config, module_name):
        super().__init__(config, module_name)
        
    def module_start(self):
        """Start web servers"""
        logger.info("Starting web servers...")
        
        # Start HTTP server
        http_server.start()
        
        # Start WebSocket server
        ws_server.start()
        
        logger.info("Web servers started successfully")
        logger.info("Access web interface at: http://localhost:8080")

    def module_stop(self):
        """Stop web servers"""
        logger.info("Stopping web servers...")
        
        # Stop WebSocket server
        ws_server.stop()
        
        # Stop HTTP server
        http_server.stop()
        
        logger.info("Web servers stopped")

    def module_update(self):
        """Update telemetry data and broadcast to clients"""
        # Get telemetry data and broadcast to WebSocket clients
        telemetry_data = ws_server.get_telemetry_data()
        ws_server.broadcast_telemetry(telemetry_data)
