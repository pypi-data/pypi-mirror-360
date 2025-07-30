#!/usr/bin/env python3
"""
MAVLink Ping Test Tool using TIMESYNC Protocol

This tool sends TIMESYNC messages and measures round-trip time (RTT)
using the MAVLink timesync protocol.

Usage:
    python mavlink_ping_test.py --port /dev/ttyUSB0 --baud 115200 --count 10
    python mavlink_ping_test.py --udp 192.168.1.100:14550 --count 10
"""

import argparse
import time
import statistics
import sys
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from pymavlink import mavutil
    from pymavlink.dialects.v10 import common as mavlink
except ImportError:
    print("Error: pymavlink not installed. Install with: pip install pymavlink")
    sys.exit(1)


class ConnectionType(Enum):
    SERIAL = "serial"
    UDP = "udp"


@dataclass
class PingResult:
    """Represents a single ping result"""
    sequence: int
    sent_time: float
    received_time: float
    rtt_ms: float
    success: bool
    error_msg: Optional[str] = None


class MavlinkPingTest:
    """MAVLink ping test using TIMESYNC protocol"""
    
    def __init__(self, connection_string: str, connection_type: ConnectionType, 
                 target_system: Optional[int] = None, target_component: Optional[int] = None,
                 verbose: bool = False):
        self.connection_string = connection_string
        self.connection_type = connection_type
        self.target_system = target_system
        self.target_component = target_component
        self.verbose = verbose
        self.mav = None
        self.sequence = 0
        self.pending_pings = {}  # sequence -> sent_time
        self.results: List[PingResult] = []
        
    def connect(self) -> bool:
        """Establish connection to MAVLink device"""
        try:
            if self.connection_type == ConnectionType.SERIAL:
                # Parse connection string to get device and baudrate
                if ':' in self.connection_string:
                    device, baudrate = self.connection_string.split(':', 1)
                    baudrate = int(baudrate)
                else:
                    device = self.connection_string
                    baudrate = 115200  # Default baudrate
                self.mav = mavutil.mavlink_connection(device, baudrate)
            else:  # UDP
                self.mav = mavutil.mavlink_connection(f"udpin:{self.connection_string}")
            
            # Set target system and component if specified
            if self.target_system is not None:
                self.mav.target_system = self.target_system
                if self.verbose:
                    print(f"Target system set to: {self.target_system}")
            
            if self.target_component is not None:
                self.mav.target_component = self.target_component
                if self.verbose:
                    print(f"Target component set to: {self.target_component}")
            
            # Wait for heartbeat from target system/component
            if self.verbose:
                print("Waiting for heartbeat...")
            
            start_time = time.time()
            while time.time() - start_time < 10:  # 10 second timeout
                try:
                    msg = self.mav.recv_match(type='HEARTBEAT', blocking=False, timeout=0.1)
                    if msg is not None:
                        src_system = msg.get_srcSystem()
                        src_component = msg.get_srcComponent()
                        
                        # Check if this is from our target system/component
                        system_match = self.target_system is None or src_system == self.target_system
                        component_match = self.target_component is None or src_component == self.target_component
                        
                        if system_match and component_match:
                            if self.verbose:
                                print(f"Received heartbeat from system {src_system}, component {src_component} ({mavutil.mavlink.enums['MAV_TYPE'][msg.type].description})")
                            print(f"Connected to system {src_system}, component {src_component} ({mavutil.mavlink.enums['MAV_TYPE'][msg.type].description})")
                            return True
                        elif self.verbose:
                            print(f"Ignoring heartbeat from system {src_system}, component {src_component} ({mavutil.mavlink.enums['MAV_TYPE'][msg.type].description})")
                            
                except Exception as e:
                    if self.verbose:
                        print(f"Error receiving heartbeat: {e}")
                    continue
            
            print("Timeout waiting for heartbeat from target system/component")
            return False
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def send_timesync(self) -> int:
        """Send a TIMESYNC message and return sequence number"""
        self.sequence += 1
        current_time = time.time()
        
        # Convert to nanoseconds (MAVLink timesync uses nanoseconds)
        ts1 = int(current_time * 1e9)
        
        # Send TIMESYNC message
        self.mav.mav.timesync_send(
            tc1=0,  # Will be filled by the receiving system
            ts1=ts1
        )
        
        self.pending_pings[self.sequence] = current_time
        return self.sequence
    
    def receive_timesync_reply(self, timeout: float = 5.0) -> Optional[PingResult]:
        """Receive TIMESYNC reply and calculate RTT"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                msg = self.mav.recv_match(type='TIMESYNC', blocking=False, timeout=0.1)
                if msg is not None:
                    result = self._process_timesync_reply(msg)
                    if result is not None:
                        return result
                    # If result is None, continue looking for the correct response
            except Exception as e:
                print(f"Error receiving message: {e}")
                continue
        
        return None
    
    def _process_timesync_reply(self, msg) -> Optional[PingResult]:
        """Process received TIMESYNC message and calculate RTT"""
        try:
            # Check if the reply is from the target system/component
            src_system = msg.get_srcSystem()
            src_component = msg.get_srcComponent()
            
            # If target system is specified, check it matches
            if self.target_system is not None and src_system != self.target_system:
                if self.verbose:
                    print(f"Ignoring reply from system {src_system}, expecting {self.target_system}")
                return None
            
            # If target component is specified, check it matches
            if self.target_component is not None and src_component != self.target_component:
                if self.verbose:
                    print(f"Ignoring reply from component {src_component}, expecting {self.target_component}")
                return None
            
            # Find the corresponding sent ping
            for seq, sent_time in self.pending_pings.items():
                # Check if this is a reply to our ping (ts1 should match our sent time)
                if abs(msg.ts1 - int(sent_time * 1e9)) < 1e6:  # Within 1ms tolerance
                    received_time = time.time()
                    rtt_ms = (received_time - sent_time) * 1000
                    
                    # Remove from pending
                    del self.pending_pings[seq]
                    
                    return PingResult(
                        sequence=seq,
                        sent_time=sent_time,
                        received_time=received_time,
                        rtt_ms=rtt_ms,
                        success=True
                    )
            return None
            
        except Exception as e:
            return PingResult(
                sequence=0,
                sent_time=0,
                received_time=0,
                rtt_ms=0,
                success=False,
                error_msg=str(e)
            )
    
    def ping_once(self, timeout: float = 5.0) -> PingResult:
        """Perform a single ping"""
        seq = self.send_timesync()
        if self.verbose:
            print(f"Sent TIMESYNC ping #{seq}")
        
        result = self.receive_timesync_reply(timeout)
        if result is None:
            # Timeout
            sent_time = self.pending_pings.get(seq, 0)
            del self.pending_pings[seq]
            return PingResult(
                sequence=seq,
                sent_time=sent_time,
                received_time=0,
                rtt_ms=0,
                success=False,
                error_msg="Timeout"
            )
        
        return result
    
    def ping_multiple(self, count: int, interval: float = 1.0) -> List[PingResult]:
        """Perform multiple pings"""
        print(f"Starting {count} pings with {interval}s interval...")
        
        for i in range(count):
            result = self.ping_once()
            self.results.append(result)
            
            if result.success:
                print(f"Ping #{result.sequence}: {result.rtt_ms:.2f}ms")
            else:
                print(f"Ping #{result.sequence}: FAILED - {result.error_msg}")
            
            if i < count - 1:  # Don't sleep after last ping
                time.sleep(interval)
        
        return self.results
    
    def print_statistics(self):
        """Print ping statistics"""
        successful_pings = [r for r in self.results if r.success]
        
        if not successful_pings:
            print("No successful pings!")
            return
        
        rtts = [r.rtt_ms for r in successful_pings]
        
        print("\n" + "="*50)
        print("PING STATISTICS")
        print("="*50)
        print(f"Total pings: {len(self.results)}")
        print(f"Successful: {len(successful_pings)}")
        print(f"Failed: {len(self.results) - len(successful_pings)}")
        print(f"Success rate: {len(successful_pings)/len(self.results)*100:.1f}%")
        print()
        print(f"RTT Statistics (ms):")
        print(f"  Min: {min(rtts):.2f}")
        print(f"  Max: {max(rtts):.2f}")
        print(f"  Mean: {statistics.mean(rtts):.2f}")
        print(f"  Median: {statistics.median(rtts):.2f}")
        if len(rtts) > 1:
            print(f"  Std Dev: {statistics.stdev(rtts):.2f}")
        print("="*50)
    
    def close(self):
        """Close the connection"""
        if self.mav:
            self.mav.close()


def main():
    parser = argparse.ArgumentParser(description="MAVLink Ping Test using TIMESYNC protocol")
    parser.add_argument("--port", help="Serial port (e.g., /dev/ttyUSB0)")
    parser.add_argument("--baud", type=int, default=None, help="Baud rate for serial connection (default: 115200)")
    parser.add_argument("--udp", help="UDP address:port (e.g., 192.168.1.100:14550)")
    parser.add_argument("--target-system", type=int, help="Target system ID (default: auto-detect)")
    parser.add_argument("--target-component", type=int, help="Target component ID (default: auto-detect)")
    parser.add_argument("--count", type=int, default=10, help="Number of pings to send")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between pings (seconds)")
    parser.add_argument("--timeout", type=float, default=5.0, help="Timeout for each ping (seconds)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Determine connection type and string
    if args.port:
        connection_type = ConnectionType.SERIAL
        # Use default baud rate of 115200 if not specified
        baud_rate = args.baud if args.baud is not None else 115200
        connection_string = f"{args.port}:{baud_rate}"
    elif args.udp:
        connection_type = ConnectionType.UDP
        connection_string = args.udp
    else:
        print("Error: Must specify either --port or --udp")
        parser.print_help()
        return
    
    # Create ping test instance with target system and component
    ping_test = MavlinkPingTest(
        connection_string, 
        connection_type,
        target_system=args.target_system,
        target_component=args.target_component,
        verbose=args.verbose
    )
    
    try:
        # Connect
        if not ping_test.connect():
            print("Failed to connect. Exiting.")
            return
        
        # Perform pings
        ping_test.ping_multiple(args.count, args.interval)
        
        # Print statistics
        ping_test.print_statistics()
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ping_test.close()


if __name__ == "__main__":
    main() 