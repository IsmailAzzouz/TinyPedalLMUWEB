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
WebSocket server for real-time telemetry broadcasting
"""

import asyncio
import json
import logging
import threading
from typing import Set

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

from ..api_control import api

logger = logging.getLogger(__name__)


class WebSocketServer:
    """WebSocket server for broadcasting telemetry data"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        """Initialize WebSocket server
        
        Args:
            host: Server host address
            port: Server port number
        """
        if not WEBSOCKETS_AVAILABLE:
            logger.error("websockets library not available. Install with: pip install websockets")
            self.enabled = False
            return
            
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.server = None
        self.loop = None
        self.thread = None
        self.running = False
        self.enabled = True

    def start(self):
        """Start WebSocket server in separate thread"""
        if not self.enabled:
            logger.warning("WebSocket server disabled - websockets library not installed")
            return
            
        if self.running:
            logger.warning("WebSocket server already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        logger.info(f"WebSocket server starting on ws://{self.host}:{self.port}")

    def _run_server(self):
        """Run WebSocket server event loop"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self._start_server())
            self.loop.run_forever()
        except Exception as e:
            logger.error(f"WebSocket server error: {e}")
        finally:
            self.loop.close()

    async def _start_server(self):
        """Start WebSocket server"""
        self.server = await websockets.serve(
            self._handle_client,
            self.host,
            self.port
        )
        logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")

    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle WebSocket client connection
        
        Args:
            websocket: WebSocket connection
            path: Request path
        """
        self.clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}. Total clients: {len(self.clients)}")
        
        try:
            async for message in websocket:
                # Handle incoming messages if needed
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    def broadcast_telemetry(self, data: dict):
        """Broadcast telemetry data to all connected clients
        
        Args:
            data: Telemetry data dictionary
        """
        if not self.enabled or not self.running or not self.clients:
            return

        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._send_to_all_clients(data),
                self.loop
            )

    async def _send_to_all_clients(self, data: dict):
        """Send data to all connected clients
        
        Args:
            data: Data to send
        """
        if not self.clients:
            return

        message = json.dumps(data)
        disconnected = set()
        
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.add(client)
        
        # Remove disconnected clients
        for client in disconnected:
            self.clients.discard(client)

    def stop(self):
        """Stop WebSocket server"""
        if not self.enabled:
            return
            
        if not self.running:
            return

        logger.info("Stopping WebSocket server...")
        self.running = False
        
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        if self.thread:
            self.thread.join(timeout=2)
        
        logger.info("WebSocket server stopped")

    def get_telemetry_data(self) -> dict:
        """Get current telemetry data from API
        
        Returns:
            Dictionary with telemetry data
        """
        try:
            if not api.state:
                return {"connected": False}

            # Extract key telemetry data
            data = {
                "connected": True,
                "speed": round(api.read.vehicle.speed(), 1),
                "rpm": round(api.read.engine.rpm(), 0),
                "gear": api.read.engine.gear(),
                "throttle": round(api.read.inputs.throttle() * 100, 1),
                "brake": round(api.read.inputs.brake() * 100, 1),
                "clutch": round(api.read.inputs.clutch() * 100, 1),
                "steering": round(api.read.inputs.steering_range(), 1),
                "fuel": round(api.read.engine.fuel(), 2),
                "lap_time_current": api.read.timing.current_laptime(),
                "lap_time_last": api.read.timing.last_laptime(),
                "lap_time_best": api.read.timing.best_laptime(),
                "lap_number": api.read.lap.number(),
                "position": api.read.vehicle.position(),
                "in_pits": api.read.vehicle.in_pit(),
                "session_time_remaining": api.read.session.remaining(),
            }
            
            # Add tire data
            tire_temps = []
            tire_press = []
            for idx in range(4):
                tire_temps.append(round(api.read.tyre.temperature(idx), 1))
                tire_press.append(round(api.read.tyre.pressure(idx), 1))
            
            data["tire_temps"] = tire_temps
            data["tire_pressure"] = tire_press
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting telemetry data: {e}")
            return {"connected": False, "error": str(e)}


# Global WebSocket server instance
ws_server = WebSocketServer()
