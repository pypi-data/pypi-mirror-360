*** Settings ***
Documentation    Basic I2C Library Test
Library          robotframework_i2c.I2CLibrary.I2CLibrary

*** Variables ***
${I2C_BUS}       1
${TEST_DEVICE}   0x48

*** Test Cases ***
Test I2C Bus Operations
    [Documentation]    Test basic I2C bus operations
    [Tags]             basic    i2c
    
    # Open I2C bus
    Open I2C Bus    ${I2C_BUS}
    
    # Scan for devices
    ${devices}=    Scan I2C Bus
    Log    Found devices on I2C bus: ${devices}
    
    # Check if our test device is present (optional - may not exist)
    ${present}=    I2C Device Present    ${TEST_DEVICE}
    Log    Device ${TEST_DEVICE} present: ${present}
    
    # Close the bus
    Close I2C Bus

Test I2C Device Communication
    [Documentation]    Test I2C device read/write operations
    [Tags]             device    communication
    
    Open I2C Bus    ${I2C_BUS}
    
    # Check if device is present before testing
    ${present}=    I2C Device Present    ${TEST_DEVICE}
    
    Run Keyword If    ${present}    Test Device Read Write
    ...    ELSE       Log    Device ${TEST_DEVICE} not present, skipping communication tests
    
    Close I2C Bus

Test I2C Block Operations
    [Documentation]    Test I2C block read/write operations
    [Tags]             block    advanced
    
    Open I2C Bus    ${I2C_BUS}
    
    ${present}=    I2C Device Present    ${TEST_DEVICE}
    
    Run Keyword If    ${present}    Test Block Read Write
    ...    ELSE       Log    Device ${TEST_DEVICE} not present, skipping block tests
    
    Close I2C Bus

Test I2C Error Handling
    [Documentation]    Test error handling scenarios
    [Tags]             error    handling
    
    # Test operations without opening bus first
    Run Keyword And Expect Error    RuntimeError: I2C bus not open*
    ...    Read I2C Register    0x48    0x00
    
    Run Keyword And Expect Error    RuntimeError: I2C bus not open*
    ...    Scan I2C Bus
    
    # Test with invalid device address
    Open I2C Bus    ${I2C_BUS}
    
    Run Keyword And Expect Error    RuntimeError: Failed to read from I2C device*
    ...    Read I2C Register    0x00    0x00    # Address 0x00 is typically invalid
    
    Close I2C Bus

*** Keywords ***
Test Device Read Write
    [Documentation]    Test reading and writing to a real device
    
    # Try to read a register (register 0x00 is common)
    ${data}=    Read I2C Register    ${TEST_DEVICE}    0x00
    Log    Read data from register 0x00: 0x${data:02X}
    
    # Test writing (be careful with real devices!)
    # This example uses a safe register that typically doesn't harm devices
    ${original}=    Read I2C Register    ${TEST_DEVICE}    0x01
    Write I2C Register    ${TEST_DEVICE}    0x01    ${original}
    ${readback}=    Read I2C Register    ${TEST_DEVICE}    0x01
    Should Be Equal As Integers    ${original}    ${readback}

Test Block Read Write
    [Documentation]    Test block operations on a real device
    
    # Read a block of data
    ${block_data}=    Read I2C Block    ${TEST_DEVICE}    0x00    4
    Log    Block data: ${block_data}
    Length Should Be    ${block_data}    4
    
    # Test block write (careful with real devices)
    ${test_data}=    Create List    0x01    0x02    0x03    0x04
    Write I2C Block    ${TEST_DEVICE}    0x10    ${test_data}
    
    # Read back and verify (if device supports it)
    ${readback}=    Read I2C Block    ${TEST_DEVICE}    0x10    4
    Log    Written: ${test_data}, Read back: ${readback}
