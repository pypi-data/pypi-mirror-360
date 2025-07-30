# MAVPing

[![Test and Build](https://github.com/krausemann/mavping/actions/workflows/test.yml/badge.svg)](https://github.com/krausemann/mavping/actions/workflows/test.yml)  
[![Publish to PyPI](https://github.com/krausemann/mavping/actions/workflows/publish.yml/badge.svg)](https://github.com/krausemann/mavping/actions/workflows/publish.yml)


A Python tool for measuring round-trip time (RTT) using the MAVLink [TIMESYNC](https://mavlink.io/en/services/timesync.html) protocol. This tool uses sends TIMESYNC messages and calculates the latency between your system and a MAVLink-compatible device. It is built using the [pymavlink](https://github.com/ArduPilot/pymavlink) library.

## Features

- **TIMESYNC Protocol**: Uses MAVLink's built-in timesync protocol for accurate timing
- **Multiple Connection Types**: Support for both serial and UDP connections
- **Comprehensive Statistics**: Provides min, max, mean, median, and standard deviation of RTT
- **Configurable Parameters**: Adjustable ping count, interval, and timeout
- **Error Handling**: Robust error handling with detailed failure reporting

## Installation
```bash
pip install mavping
```

## Manual installation

1. **Clone this repro**
   ```bash
   git clone https://github.com/krausemann/mavping.git
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify .MAVLink installation**:
   ```bash
   python -c "import pymavlink; print('MAVLink installed successfully')"
   ```

4. **Run mavping**
   ```bash
   python src/mavping/mavping.py -h
   ```

## Usage

### Serial Connection

Connect to a device via serial port:

```bash
mavping --port /dev/ttyUSB0
```

### UDP Connection

Connect to a device via UDP (e.g., for SITL or network-connected devices):

```bash
mavping --udp 192.168.1.100:14550
```

### Command Line Options

- `--port`: Serial port (e.g., `/dev/ttyUSB0`, `COM3`)
- `--baud`: Baud rate for serial connection (default: 115200, optional)
- `--udp`: UDP address:port (e.g., `192.168.1.100:14550`)
- `--target-system`: Target system ID (default: auto-detect)
- `--target-component`: Target component ID (default: auto-detect)
- `--count`: Number of pings to send (default: 10)
- `--interval`: Interval between pings in seconds (default: 1.0)
- `--timeout`: Timeout for each ping in seconds (default: 5.0)
- `--verbose`: Enable verbose output for debugging


## Output Example

```
Connected to system 1, component 1 (Fixed wing aircraft.)
Starting 10 pings with 1.0s interval...
Ping #1: 3.96ms
Ping #2: 7.47ms
...

==================================================
PING STATISTICS
==================================================
Total pings: 10
Successful: 10
Failed: 0
Success rate: 100.0%

RTT Statistics (ms):
  Min: 3.96
  Max: 7.67
  Mean: 6.56
  Median: 6.58
  Std Dev: 1.15
==================================================
```

## Requirements

- Python 3.7+
- pymavlink >= 2.4.37
- pyserial >= 3.5

## License

mavping is released under MIT License. It was created with assistance from Cursor IDE, using an unspecified reasoning model. Parts of it might resemble other software which was used to train the model. It was not possible to verify possible copyright violations. Kindly contact the author in case you think your copyright is violated.

## Repository

- **GitHub**: [https://github.com/krausemann/mavping](https://github.com/krausemann/mavping)