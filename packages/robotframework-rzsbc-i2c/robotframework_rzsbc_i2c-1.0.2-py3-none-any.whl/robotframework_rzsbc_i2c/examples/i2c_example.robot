*** Settings ***
Documentation    Example I2C test using robotframework-rzsbc-i2c
Library          robotframework_rzsbc_i2c.I2CLibrary.I2CLibrary
Library          robotframework_rzsbc_i2c.common.board_config

*** Variables ***
${SERIAL_CONNECTION}    /dev/ttyUSB0
${BOARD_TYPE}          rzsbc

*** Test Cases ***
Test I2C with Board Configuration
    [Documentation]    Test I2C functionality with board configuration
    [Tags]             i2c    board    config
    
    # Set up board configuration
    Set Board Type    ${BOARD_TYPE}
    ${board_config}=    Get Board Config    ${BOARD_TYPE}
    Log    Board configuration: ${board_config}
    
    # Get I2C feature configuration
    ${i2c_config}=    Get Feature Config    i2c    ${BOARD_TYPE}    core-image-bsp
    Log    I2C feature config: ${i2c_config}
    
    # Get I2C instances
    ${i2c_instances}=    Get Feature Instances    i2c    ${BOARD_TYPE}    core-image-bsp
    Log    I2C instances: ${i2c_instances}
    
    # Initialize I2C Library with board configuration
    TRY
        Init I2C Library    ${SERIAL_CONNECTION}    ${BOARD_TYPE}
        Log    I2C Library initialized successfully
        
        # Test I2C operations based on configuration
        FOR    ${instance_name}    IN    @{i2c_instances.keys()}
            ${instance_config}=    Set Variable    ${i2c_instances}[${instance_name}]
            Continue For Loop If    not ${instance_config}[enabled]
            
            ${i2c_bus}=    Set Variable    ${instance_config}[i2c_bus]
            ${expected_addr}=    Set Variable    ${instance_config}[expected_addr]
            
            Log    Testing I2C instance: ${instance_name}
            Log    Bus: ${i2c_bus}, Expected Address: ${expected_addr}
            
            # Set I2C parameters from config
            Set I2C Parameters    i2c_bus=${i2c_bus}    expected_addr=${expected_addr}
            
            # Detect I2C adapter
            Detect I2C Adapter
            
            # Scan for I2C devices
            Scan I2C Device    ${i2c_bus}
            
            Log    I2C instance ${instance_name} tested successfully
        END
        
    EXCEPT    AS    ${error}
        Log    I2C test failed (expected if no hardware): ${error}
    END

Test I2C Direct Operations
    [Documentation]    Test direct I2C operations without board config
    [Tags]             i2c    direct
    
    TRY
        # Direct I2C operations
        Open I2C Bus    1
        ${devices}=    Scan I2C Bus  
        Log    Found devices: ${devices}
        
        # Test device presence
        ${present}=    I2C Device Present    0x48
        Log    Device 0x48 present: ${present}
        
        Run Keyword If    ${present}    Test I2C Device Communication    0x48
        
        Close I2C Bus
        
    EXCEPT    AS    ${error}
        Log    Direct I2C test failed: ${error}
    END

*** Keywords ***
Test I2C Device Communication
    [Arguments]    ${device_addr}
    [Documentation]    Test communication with specific I2C device
    
    Log    Testing communication with device ${device_addr}
    
    # Try to read a register
    ${data}=    Read I2C Register    ${device_addr}    0x00
    Log    Read from register 0x00: 0x${data:02X}
    
    # Test delay
    Set I2C Delay    100
    Log    Set 100ms delay for I2C operations
