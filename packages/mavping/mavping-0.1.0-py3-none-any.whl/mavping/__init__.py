"""
MAVLink Ping Tool

A Python tool for measuring round-trip time (RTT) using the MAVLink TIMESYNC protocol.
"""

__version__ = "0.1.0"
__author__ = "MAVLink Ping Tool"
__email__ = "example@example.com"

from .mavping import MavlinkPingTest, PingResult, ConnectionType

__all__ = ["MavlinkPingTest", "PingResult", "ConnectionType"] 