#!/usr/bin/env python3
"""
I2CLibrary for Robot Framework

A Robot Framework library for interfacing I2C devices on Raspberry Pi
and other embedded systems.
"""

import time
from robot.api.deco import keyword, library
from robot.api import logger

try:
    import smbus2
    HAS_SMBUS = True
except ImportError:
    HAS_SMBUS = False
    logger.warn("smbus2 not available. Some I2C functions may not work.")

@library(scope='GLOBAL', version='1.0.0')
class I2CLibrary:
    """
    Robot Framework library for I2C communication with devices.
    
    This library provides keywords for I2C communication on Raspberry Pi
    and other embedded systems using the smbus2 library.
    
    = Requirements =
    - Robot Framework (>=3.2.2)
    - smbus2 (>=0.4.0)
    - I2C enabled on the system
    
    = Installation =
    | pip install robotframework-i2c
    
    = Examples =
    | *** Settings ***
    | Library    robotframework_i2c.I2CLibrary.I2CLibrary
    |
    | *** Test Cases ***
    | Test I2C Communication
    |     Open I2C Bus    1
    |     ${data}=    Read I2C Register    0x48    0x00
    |     Write I2C Register    0x48    0x01    0xFF
    |     Close I2C Bus
    """

    def __init__(self):
        """Initialize the I2CLibrary."""
        self._bus = None
        self._bus_number = None
        logger.info("I2CLibrary: Initialized")
        
        if not HAS_SMBUS:
            logger.warn("smbus2 not available. Install with: pip install smbus2")

    @keyword("Open I2C Bus")
    def open_i2c_bus(self, bus_number=1):
        """
        Opens an I2C bus for communication.
        
        Args:
            bus_number (int): I2C bus number (default: 1)
            
        Example:
            | Open I2C Bus    1 |
        """
        if not HAS_SMBUS:
            raise RuntimeError("smbus2 not available. Install with: pip install smbus2")
            
        try:
            bus_number = int(bus_number)
            self._bus = smbus2.SMBus(bus_number)
            self._bus_number = bus_number
            logger.info(f"Opened I2C bus {bus_number}")
        except Exception as e:
            raise RuntimeError(f"Failed to open I2C bus {bus_number}: {str(e)}")

    @keyword("Close I2C Bus")
    def close_i2c_bus(self):
        """
        Closes the currently open I2C bus.
        
        Example:
            | Close I2C Bus |
        """
        if self._bus:
            try:
                self._bus.close()
                logger.info(f"Closed I2C bus {self._bus_number}")
                self._bus = None
                self._bus_number = None
            except Exception as e:
                logger.warn(f"Error closing I2C bus: {str(e)}")

    @keyword("Read I2C Register")
    def read_i2c_register(self, device_address, register_address):
        """
        Reads data from an I2C device register.
        
        Args:
            device_address (int/str): I2C device address (e.g., 0x48)
            register_address (int/str): Register address to read from
            
        Returns:
            int: Data read from the register
            
        Example:
            | ${data}=    Read I2C Register    0x48    0x00 |
        """
        self._ensure_bus_open()
        
        try:
            device_addr = self._parse_address(device_address)
            register_addr = self._parse_address(register_address)
            
            data = self._bus.read_byte_data(device_addr, register_addr)
            logger.info(f"Read 0x{data:02X} from device 0x{device_addr:02X} register 0x{register_addr:02X}")
            return data
            
        except Exception as e:
            raise RuntimeError(f"Failed to read from I2C device 0x{device_addr:02X}: {str(e)}")

    @keyword("Write I2C Register")
    def write_i2c_register(self, device_address, register_address, data):
        """
        Writes data to an I2C device register.
        
        Args:
            device_address (int/str): I2C device address (e.g., 0x48)
            register_address (int/str): Register address to write to
            data (int/str): Data to write
            
        Example:
            | Write I2C Register    0x48    0x01    0xFF |
        """
        self._ensure_bus_open()
        
        try:
            device_addr = self._parse_address(device_address)
            register_addr = self._parse_address(register_address)
            data_value = self._parse_address(data)
            
            self._bus.write_byte_data(device_addr, register_addr, data_value)
            logger.info(f"Wrote 0x{data_value:02X} to device 0x{device_addr:02X} register 0x{register_addr:02X}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to write to I2C device 0x{device_addr:02X}: {str(e)}")

    @keyword("Scan I2C Bus")
    def scan_i2c_bus(self):
        """
        Scans the I2C bus for connected devices.
        
        Returns:
            list: List of device addresses found on the bus
            
        Example:
            | ${devices}=    Scan I2C Bus |
            | Log    Found devices: ${devices} |
        """
        self._ensure_bus_open()
        
        devices = []
        logger.info("Scanning I2C bus for devices...")
        
        for address in range(0x03, 0x78):  # Valid I2C address range
            try:
                self._bus.read_byte(address)
                devices.append(f"0x{address:02X}")
                logger.info(f"Found device at address 0x{address:02X}")
            except:
                pass  # Device not present
                
        logger.info(f"I2C scan complete. Found {len(devices)} devices: {devices}")
        return devices

    @keyword("Read I2C Block")
    def read_i2c_block(self, device_address, register_address, length):
        """
        Reads a block of data from an I2C device.
        
        Args:
            device_address (int/str): I2C device address
            register_address (int/str): Starting register address
            length (int): Number of bytes to read
            
        Returns:
            list: List of bytes read from the device
            
        Example:
            | ${data}=    Read I2C Block    0x48    0x00    4 |
        """
        self._ensure_bus_open()
        
        try:
            device_addr = self._parse_address(device_address)
            register_addr = self._parse_address(register_address)
            length = int(length)
            
            data = self._bus.read_i2c_block_data(device_addr, register_addr, length)
            logger.info(f"Read {len(data)} bytes from device 0x{device_addr:02X}: {[f'0x{b:02X}' for b in data]}")
            return data
            
        except Exception as e:
            raise RuntimeError(f"Failed to read block from I2C device 0x{device_addr:02X}: {str(e)}")

    @keyword("Write I2C Block")
    def write_i2c_block(self, device_address, register_address, data_list):
        """
        Writes a block of data to an I2C device.
        
        Args:
            device_address (int/str): I2C device address
            register_address (int/str): Starting register address
            data_list (list): List of bytes to write
            
        Example:
            | ${data}=    Create List    0x01    0x02    0x03    0x04 |
            | Write I2C Block    0x48    0x00    ${data} |
        """
        self._ensure_bus_open()
        
        try:
            device_addr = self._parse_address(device_address)
            register_addr = self._parse_address(register_address)
            
            # Convert data to list of integers
            if isinstance(data_list, str):
                data_list = data_list.split()
            
            data_bytes = [self._parse_address(d) for d in data_list]
            
            self._bus.write_i2c_block_data(device_addr, register_addr, data_bytes)
            logger.info(f"Wrote {len(data_bytes)} bytes to device 0x{device_addr:02X}: {[f'0x{b:02X}' for b in data_bytes]}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to write block to I2C device 0x{device_addr:02X}: {str(e)}")

    @keyword("I2C Device Present")
    def i2c_device_present(self, device_address):
        """
        Checks if a device is present at the given I2C address.
        
        Args:
            device_address (int/str): I2C device address to check
            
        Returns:
            bool: True if device is present, False otherwise
            
        Example:
            | ${present}=    I2C Device Present    0x48 |
            | Should Be True    ${present} |
        """
        self._ensure_bus_open()
        
        try:
            device_addr = self._parse_address(device_address)
            self._bus.read_byte(device_addr)
            logger.info(f"Device present at address 0x{device_addr:02X}")
            return True
        except:
            logger.info(f"No device found at address 0x{device_addr:02X}")
            return False

    @keyword("Set I2C Delay")
    def set_i2c_delay(self, delay_ms):
        """
        Sets a delay between I2C operations.
        
        Args:
            delay_ms (float): Delay in milliseconds
            
        Example:
            | Set I2C Delay    10 |
        """
        delay_seconds = float(delay_ms) / 1000.0
        time.sleep(delay_seconds)
        logger.info(f"I2C delay: {delay_ms}ms")

    def _ensure_bus_open(self):
        """Ensures that an I2C bus is open."""
        if self._bus is None:
            raise RuntimeError("I2C bus not open. Use 'Open I2C Bus' keyword first.")

    def _parse_address(self, address):
        """Parses an address string/int to integer."""
        if isinstance(address, str):
            if address.lower().startswith('0x'):
                return int(address, 16)
            else:
                return int(address)
        return int(address)

    def __del__(self):
        """Cleanup when library is destroyed."""
        if self._bus:
            self.close_i2c_bus()
