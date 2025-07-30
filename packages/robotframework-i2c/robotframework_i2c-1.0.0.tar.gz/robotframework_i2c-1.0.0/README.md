# Robot Framework I2C Library

[![PyPI version](https://badge.fury.io/py/robotframework-i2c.svg)](https://badge.fury.io/py/robotframework-i2c)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Robot Framework library for interfacing I2C devices on Raspberry Pi and other embedded systems.

## Installation

```bash
pip install robotframework-i2c
```

## Requirements

- Robot Framework (>=3.2.2)
- smbus2 (>=0.4.0)
- I2C enabled on the system

## Quick Start

```robot
*** Settings ***
Library    robotframework_i2c.I2CLibrary.I2CLibrary

*** Test Cases ***
Test I2C Communication
    Open I2C Bus    1
    ${devices}=    Scan I2C Bus
    Log    Found devices: ${devices}
    Close I2C Bus
```

## Keywords

### Bus Management
- `Open I2C Bus` - Opens an I2C bus for communication
- `Close I2C Bus` - Closes the currently open I2C bus
- `Scan I2C Bus` - Scans the I2C bus for connected devices

### Device Communication
- `Read I2C Register` - Reads data from a device register
- `Write I2C Register` - Writes data to a device register
- `Read I2C Block` - Reads a block of data from a device
- `Write I2C Block` - Writes a block of data to a device
- `I2C Device Present` - Checks if a device is present at an address

### Utility
- `Set I2C Delay` - Sets a delay between I2C operations

## Examples

### Basic Device Communication

```robot
*** Settings ***
Library    robotframework_i2c.I2CLibrary.I2CLibrary

*** Test Cases ***
Read Temperature Sensor
    Open I2C Bus    1
    ${present}=    I2C Device Present    0x48
    Should Be True    ${present}
    ${temp_raw}=    Read I2C Register    0x48    0x00
    Log    Raw temperature: ${temp_raw}
    Close I2C Bus
```

### Block Data Operations

```robot
*** Settings ***
Library    robotframework_i2c.I2CLibrary.I2CLibrary

*** Test Cases ***
Read Configuration Block
    Open I2C Bus    1
    ${config_data}=    Read I2C Block    0x48    0x10    4
    Log    Configuration: ${config_data}
    
    ${new_config}=    Create List    0x01    0x02    0x03    0x04
    Write I2C Block    0x48    0x10    ${new_config}
    Close I2C Bus
```

### Device Discovery

```robot
*** Settings ***
Library    robotframework_i2c.I2CLibrary.I2CLibrary

*** Test Cases ***
Discover I2C Devices
    Open I2C Bus    1
    ${devices}=    Scan I2C Bus
    Log    Found ${devices.__len__()} devices
    FOR    ${device}    IN    @{devices}
        Log    Device found at: ${device}
    END
    Close I2C Bus
```

## Supported Platforms

- Raspberry Pi (all models)
- Other Linux-based embedded systems with I2C support
- Any system with `/dev/i2c-*` device files

## Hardware Setup

Before using this library, ensure I2C is enabled on your system:

### Raspberry Pi
1. Enable I2C via `raspi-config` or add `dtparam=i2c_arm=on` to `/boot/config.txt`
2. Reboot the system
3. Verify I2C is working: `ls /dev/i2c-*`

### General Linux
1. Load I2C kernel modules: `modprobe i2c-dev`
2. Ensure your user has access to I2C devices (usually in `i2c` group)

## Error Handling

The library provides detailed error messages for common issues:

- **Bus not open**: Ensure you call `Open I2C Bus` before other operations
- **Device not found**: Check wiring and device address
- **Permission denied**: Ensure proper user permissions for I2C devices
- **smbus2 not available**: Install with `pip install smbus2`

## License

MIT License. See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the GitHub issue tracker.
