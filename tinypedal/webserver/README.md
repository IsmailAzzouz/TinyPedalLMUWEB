# TinyPedal Web Interface

The web interface provides real-time telemetry viewing through a browser with a racing-inspired dashboard.

## Features

- **Real-time Updates**: Telemetry data updates at ~10Hz via WebSocket
- **Racing Dashboard**: Fixed 1920x300px canvas optimized for racing displays
- **Auto-reconnect**: Automatically reconnects if connection is lost
- **No Configuration**: Works out of the box when module is enabled

## Dashboard Elements

The dashboard displays:
- **Center**: Large gear indicator, speedometer, RPM bar, and pedal inputs
- **Left Panel**: Position, lap number, and lap times (current, last, best)
- **Right Panel**: Fuel level, tire temperatures, and session time

## Usage

1. Enable the `module_webserver` in TinyPedal settings
2. Start TinyPedal
3. Open your browser and navigate to: `http://localhost:8080`
4. The dashboard will automatically connect when telemetry data is available

## Technical Details

- **HTTP Server**: Port 8080 (serves static files)
- **WebSocket Server**: Port 8765 (broadcasts telemetry)
- **Update Rate**: ~100ms (10Hz)
- **Canvas Size**: 1920x300 pixels (fixed)

## Requirements

- `websockets>=12.0` (automatically installed with requirements.txt)

## Architecture

```
TinyPedal Application
  ├─ API Control (reads game data)
  ├─ WebServer Module
      ├─ HTTP Server (port 8080)
      │   └─ Serves index.html and assets
      └─ WebSocket Server (port 8765)
          └─ Broadcasts telemetry to connected clients
```

## Troubleshooting

**Dashboard shows "DISCONNECTED"**
- Make sure TinyPedal is running and connected to the game
- Check that the game is actively running with telemetry data

**Can't access web interface**
- Verify port 8080 is not in use by another application
- Try accessing `http://127.0.0.1:8080` instead of `localhost`

**WebSocket connection fails**
- Verify port 8765 is not blocked by firewall
- Check browser console for error messages
