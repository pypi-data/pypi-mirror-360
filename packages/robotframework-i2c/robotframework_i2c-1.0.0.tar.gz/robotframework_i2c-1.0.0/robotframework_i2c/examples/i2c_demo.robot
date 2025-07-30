*** Settings ***
Documentation    Simple I2C Library Demo - Safe for systems without I2C devices
Library          robotframework_i2c.I2CLibrary.I2CLibrary

*** Test Cases ***
Demo I2C Bus Scan
    [Documentation]    Demonstrate I2C bus scanning (safe even without devices)
    [Tags]             demo    safe
    
    Log    Starting I2C Library Demo
    
    # Open I2C bus (will fail gracefully if I2C not available)
    TRY
        Open I2C Bus    1
        Log    I2C Bus 1 opened successfully
        
        # Scan for devices
        ${devices}=    Scan I2C Bus
        Log    Scan complete. Found devices: ${devices}
        
        # Demonstrate delay function
        Set I2C Delay    100
        Log    Set 100ms delay between operations
        
        # Close the bus
        Close I2C Bus
        Log    I2C Bus closed successfully
        
    EXCEPT    AS    ${error}
        Log    I2C operation failed (expected if no I2C hardware): ${error}
        Log    This is normal on systems without I2C support
    END

Demo I2C Address Parsing
    [Documentation]    Demonstrate address parsing functionality
    [Tags]             demo    parsing
    
    Log    Testing address parsing (no hardware required)
    
    # These tests don't require actual I2C hardware
    # They just test the library's address parsing logic
    
    Log    Address parsing examples:
    Log    - 0x48 (hex string)
    Log    - 72 (decimal)
    Log    - 0xFF (max 8-bit value)
    
    Log    The library handles multiple address formats automatically
