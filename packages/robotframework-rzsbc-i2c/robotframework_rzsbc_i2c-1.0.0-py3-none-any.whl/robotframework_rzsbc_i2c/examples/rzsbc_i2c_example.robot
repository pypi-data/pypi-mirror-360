*** Settings ***
Documentation    RZ-SBC I2C Library Basic Example
Library          robotframework_rzsbc_i2c.I2CLibrary.I2CLibrary

*** Variables ***
${BOARD_TYPE}    RZ_SBC_Board
${I2C_BUS}       1

*** Test Cases ***
Test I2C Library Initialization
    [Documentation]    Test basic library initialization
    [Tags]             init    basic
    
    Log    Testing RZ-SBC I2C Library initialization
    
    # Mock serial connection for demo
    ${mock_serial}=    Set Variable    mock_serial_connection
    
    # Initialize library with board type
    Init I2C Library    ${mock_serial}    ${BOARD_TYPE}
    Log    I2C Library initialized successfully for ${BOARD_TYPE}

Test I2C Configuration
    [Documentation]    Test I2C parameter configuration
    [Tags]             config    parameters
    
    ${mock_serial}=    Set Variable    mock_serial_connection
    Init I2C Library    ${mock_serial}    ${BOARD_TYPE}
    
    # Set I2C parameters
    Set I2C Parameters    i2c_bus=${I2C_BUS}    expected_addr=0x48    retry_count=3
    Log    I2C parameters configured successfully
    
    # Get board-specific I2C configuration
    TRY
        ${pairs}=    Get I2C Bus Address Pairs    ${BOARD_TYPE}
        Log    I2C Bus/Address pairs for ${BOARD_TYPE}: ${pairs}
    EXCEPT    AS    ${error}
        Log    Configuration not found (expected in demo): ${error}
    END

Test I2C Device Operations
    [Documentation]    Test I2C device detection and scanning
    [Tags]             device    detection
    
    ${mock_serial}=    Set Variable    mock_serial_connection
    Init I2C Library    ${mock_serial}    ${BOARD_TYPE}
    
    # Test adapter detection (will fail gracefully without hardware)
    TRY
        Detect I2C Adapter    delay=1
        Log    I2C adapter detected successfully
    EXCEPT    AS    ${error}
        Log    I2C adapter detection failed (expected without hardware): ${error}
    END
    
    # Test device scanning (will fail gracefully without hardware)
    TRY
        ${devices}=    Scan I2C Device    ${I2C_BUS}    delay=1
        Log    Scan result: ${devices}
    EXCEPT    AS    ${error}
        Log    I2C scan failed (expected without hardware): ${error}
    END
    
    # Test specific device presence check
    TRY
        ${present}=    Verify I2C Address Present    ${I2C_BUS}    0x48    delay=1
        Log    Device at 0x48 present: ${present}
    EXCEPT    AS    ${error}
        Log    Device verification failed (expected without hardware): ${error}
    END
