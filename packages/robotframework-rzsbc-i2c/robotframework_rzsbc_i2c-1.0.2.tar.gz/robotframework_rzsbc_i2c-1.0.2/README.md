# Robot Framework RZ-SBC I2C Library

[![PyPI version](https://badge.fury.io/py/robotframework-rzsbc-i2c.svg)](https://badge.fury.io/py/robotframework-rzsbc-i2c)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Robot Framework library for RZ-SBC I2C communication with dynamic board configuration support.

## Features

- **I2C Communication**: Full I2C support with hardware abstraction
- **Board Configuration**: Dynamic board configuration via YAML
- **Multiple Board Support**: Support for different RZ-SBC variants
- **Configuration Management**: Centralized configuration for boards, features, and instances
- **Example Test Cases**: Ready-to-use Robot Framework examples

## Installation

```bash
pip install robotframework-rzsbc-i2c
```

## Quick Start

### Basic I2C Operations

```robot
*** Settings ***
Library    robotframework_rzsbc_i2c.I2CLibrary

*** Test Cases ***
Simple I2C Test
    Open I2C Bus    1
    ${devices}=    Scan I2C Bus
    Log    Found devices: ${devices}
    Close I2C Bus
```

### With Board Configuration

```robot
*** Settings ***
Library    robotframework_rzsbc_i2c.I2CLibrary.I2CLibrary
Library    robotframework_rzsbc_i2c.common.board_config

*** Variables ***
${BOARD_TYPE}    rzsbc

*** Test Cases ***
I2C Test with Board Config
    # Set up board configuration
    Set Board Type    ${BOARD_TYPE}
    ${board_config}=    Get Board Config
    
    # Get I2C configuration from YAML
    ${i2c_config}=    Get Feature Config    i2c    ${BOARD_TYPE}    core-image-bsp
    ${i2c_instances}=    Get Feature Instances    i2c    ${BOARD_TYPE}    core-image-bsp
    
    # Initialize I2C with board config
    Init I2C Library    /dev/ttyUSB0    ${BOARD_TYPE}
    
    # Test each configured I2C instance
    FOR    ${instance_name}    IN    @{i2c_instances.keys()}
        ${instance}=    Set Variable    ${i2c_instances}[${instance_name}]
        Continue For Loop If    not ${instance}[enabled]
        
        Set I2C Parameters    i2c_bus=${instance}[i2c_bus]    expected_addr=${instance}[expected_addr]
        Detect I2C Adapter
        Scan I2C Device    ${instance}[i2c_bus]
    END
```

## Configuration Structure

The library uses YAML configuration files to define board-specific settings:

```yaml
board_configs:
  rzsbc:
    enabled: true
    board_type: "rzsbc"
    serial_port: "/dev/ttyUSB0"
    baud_rate: 115200
    platform: "rzg2l-sbc"
    
    usb_relay_config:
      name: "usbrelay"
      port: "0_1"
      
      core-image-bsp:
        enabled: true
        features:
          i2c:
            enabled: true
            instances:
              i2c_0:
                enabled: true
                i2c_bus: 0
                expected_addr: "12"
              i2c_3:
                enabled: true
                i2c_bus: 3
                expected_addr: "50"
```

## Library Components

### I2CLibrary Keywords

#### Hardware Operations
- `Init I2C Library` - Initialize with serial connection and board type
- `Open I2C Bus` - Open I2C bus for communication
- `Close I2C Bus` - Close I2C bus
- `Scan I2C Bus` - Scan for I2C devices
- `Detect I2C Adapter` - Detect I2C adapter on board

#### Device Communication
- `Read I2C Register` - Read from device register
- `Write I2C Register` - Write to device register
- `Read I2C Block` - Read block of data
- `Write I2C Block` - Write block of data
- `I2C Device Present` - Check device presence

#### Configuration
- `Set I2C Parameters` - Set I2C bus and address parameters
- `Set I2C Delay` - Set delay between operations

### Board Configuration Keywords

- `Set Board Type` - Set current board type
- `Get Board Config` - Get board configuration
- `Get Feature Config` - Get feature-specific configuration
- `Get Feature Instances` - Get feature instances
- `Get USB Relay Config` - Get USB relay configuration

## Examples

### Hardware-Independent Test

```robot
*** Settings ***
Library    robotframework_rzsbc_i2c.I2CLibrary

*** Test Cases ***
Safe I2C Operations
    TRY
        Open I2C Bus    1
        ${devices}=    Scan I2C Bus
        Log    Found ${devices.__len__()} devices
        
        FOR    ${device}    IN    @{devices}
            Log    Device: ${device}
            ${present}=    I2C Device Present    ${device}
            Should Be True    ${present}
        END
        
        Close I2C Bus
    EXCEPT    AS    ${error}
        Log    I2C operations failed: ${error}
        Log    This is expected without proper I2C hardware
    END
```

### Board-Specific Test

```robot
*** Settings ***
Library    robotframework_rzsbc_i2c.I2CLibrary.I2CLibrary
Library    robotframework_rzsbc_i2c.common.board_config

*** Test Cases ***
Board Specific I2C Test
    Set Board Type    rzsbc
    
    ${i2c_instances}=    Get Feature Instances    i2c    rzsbc    core-image-bsp
    
    Init I2C Library    /dev/ttyUSB0    rzsbc
    
    FOR    ${instance_name}    ${instance_config}    IN    &{i2c_instances}
        Continue For Loop If    not ${instance_config.enabled}
        
        Log    Testing ${instance_name}: Bus ${instance_config.i2c_bus}
        Set I2C Parameters    i2c_bus=${instance_config.i2c_bus}    expected_addr=${instance_config.expected_addr}
        
        Detect I2C Adapter
        Scan I2C Device    ${instance_config.i2c_bus}
    END
```

## Package Structure

```
robotframework_rzsbc_i2c/
├── __init__.py                 # Package initialization
├── I2CLibrary/                 # I2C Library implementation
│   ├── __init__.py
│   └── I2CLibrary.py          # Main I2C library
├── common/                     # Common utilities
│   ├── __init__.py
│   └── board_config.py        # Board configuration management
├── config/                     # Configuration files
│   └── config.yml             # Default board configurations
└── examples/                   # Example test files
    └── i2c_example.robot       # Complete usage example
```

## Supported Platforms

- Renesas RZ-SBC boards
- Systems with I2C support and `/dev/i2c-*` devices
- Linux-based embedded systems

## Hardware Requirements

- I2C-enabled hardware
- Serial connection for board communication (optional)
- Proper I2C device permissions

## Troubleshooting

### Permission Issues
```bash
# Add user to i2c group
sudo usermod -a -G i2c $USER

# Set device permissions
sudo chmod 666 /dev/i2c-*
```

### Missing I2C Tools
```bash
# Install i2c-tools (Ubuntu/Debian)
sudo apt-get install i2c-tools

# Install smbus2 (Python)
pip install smbus2
```

### Configuration Issues
- Ensure `config.yml` is properly formatted
- Check board type matches configuration
- Verify serial port permissions and availability

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please submit pull requests or issues on GitHub.t Framework RZ-SBC I2C Library

[![PyPI version](https://badge.fury.io/py/robotframework-rzsbc-i2c.svg)](https://badge.fury.io/py/robotframework-rzsbc-i2c)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Robot Framework library for RZ-SBC I2C communication with dynamic board configuration support for Renesas RZ-SBC systems.

## Features

-   **Dynamic Board Configuration**: Automatically loads I2C settings based on board type
-   **Serial Integration**: Works with serial connections for remote I2C operations
-   **Configuration Management**: Uses YAML-based configuration files for different board types
-   **Comprehensive I2C Operations**: Supports device detection, scanning, and communication
-   **Error Handling**: Robust error handling and logging for debugging

## Installation

```bash
pip install robotframework-rzsbc-i2c
```

## Requirements

-   Robot Framework (>=3.2.2)
-   pyserial (>=3.5)
-   pyyaml (>=5.4.0)

## Quick Start

```robot
*** Settings ***
Library    robotframework_rzsbc_i2c.I2CLibrary.I2CLibrary

*** Test Cases ***
Test I2C Communication
    Init I2C Library    ${serial_connection}    RZ_SBC_Board
    Set I2C Parameters    i2c_bus=1    expected_addr=0x48
    Detect I2C Adapter
    ${devices}=    Scan I2C Device    1
    Log    Found devices: ${devices}
```

## Keywords

### Initialization and Configuration

-   `Init I2C Library` - Initialize the library with serial connection and board type
-   `Set I2C Parameters` - Configure I2C bus, addresses, and timing parameters

### Device Operations

-   `Detect I2C Adapter` - Detect and validate I2C adapter presence
-   `Scan I2C Device` - Scan for devices on specified I2C bus
-   `Verify I2C Address Present` - Check if a specific device address is present
-   `Get I2C Bus Address Pairs` - Retrieve configured I2C bus/address pairs for board type

## Board Configuration

The library uses YAML configuration files to define board-specific I2C settings:

```yaml
boards:
    RZ_SBC_Board:
        images:
            linux_image:
                features:
                    i2c:
                        enabled: true
                        instances:
                            temp_sensor:
                                i2c_bus: 1
                                expected_addr: "0x48"
                            rtc:
                                i2c_bus: 1
                                expected_addr: "0x68"
```

## Examples

### Basic I2C Device Detection

```robot
*** Settings ***
Library    robotframework_rzsbc_i2c.I2CLibrary.I2CLibrary

*** Test Cases ***
Detect I2C Devices
    Init I2C Library    ${SERIAL}    RZ_SBC_Board
    Detect I2C Adapter    delay=2

    ${pairs}=    Get I2C Bus Address Pairs    RZ_SBC_Board
    FOR    ${bus}    ${addr}    IN    @{pairs}
        ${present}=    Verify I2C Address Present    ${bus}    ${addr}
        Should Be True    ${present}    Device ${addr} not found on bus ${bus}
    END
```

### Advanced I2C Scanning

```robot
*** Settings ***
Library    robotframework_rzsbc_i2c.I2CLibrary.I2CLibrary

*** Test Cases ***
Comprehensive I2C Test
    Init I2C Library    ${SERIAL}    RZ_SBC_Board
    Set I2C Parameters    retry_count=3    delay_between_commands=1

    # Scan multiple buses
    FOR    ${bus}    IN RANGE    0    3
        TRY
            ${devices}=    Scan I2C Device    ${bus}    delay=2
            Log    Bus ${bus} devices: ${devices}
        EXCEPT
            Log    Bus ${bus} not available or no devices found
        END
    END
```

### Board-Specific Configuration

```robot
*** Settings ***
Library    robotframework_rzsbc_i2c.I2CLibrary.I2CLibrary

*** Test Cases ***
Test Multiple Board Types
    @{board_types}=    Create List    RZ_SBC_Board    RZ_G2L_Board    RZ_V2L_Board

    FOR    ${board}    IN    @{board_types}
        TRY
            Init I2C Library    ${SERIAL}    ${board}
            ${pairs}=    Get I2C Bus Address Pairs    ${board}
            Log    ${board} I2C configuration: ${pairs}
        EXCEPT    AS    ${error}
            Log    Board ${board} not configured: ${error}
        END
    END
```

## Configuration File Structure

The library expects a `config.yml` file with the following structure:

```yaml
boards:
    BOARD_TYPE:
        images:
            IMAGE_NAME:
                features:
                    i2c:
                        enabled: true/false
                        instances:
                            INSTANCE_NAME:
                                i2c_bus: BUS_NUMBER
                                expected_addr: "DEVICE_ADDRESS"
```

## Error Handling

The library provides comprehensive error handling:

-   **Missing Configuration**: Graceful handling when board configs are not found
-   **Serial Communication**: Robust serial connection error handling
-   **I2C Hardware**: Proper error reporting for I2C hardware issues
-   **Device Detection**: Clear feedback when devices are not present

## Supported Platforms

-   Renesas RZ-SBC systems
-   Any Linux system with I2C support
-   Remote systems via serial connection

## Hardware Requirements

-   I2C-enabled system or board
-   Serial connection for remote operations
-   Proper I2C device permissions

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Permission Denied**: Check I2C device permissions (`/dev/i2c-*`)
3. **Configuration Not Found**: Verify `config.yml` file location and format
4. **Serial Connection**: Ensure proper serial connection and baud rate

### Debug Mode

Enable detailed logging by setting the Robot Framework log level:

```robot
*** Settings ***
Library    robotframework_rzsbc_i2c.I2CLibrary.I2CLibrary    WITH NAME    I2C
```

## License

MIT License. See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the GitHub issue tracker.
