# RZ-CI Robot Framework

A comprehensive Robot Framework-based testing framework for Renesas RZ boards.

[![PyPI version](https://badge.fury.io/py/rz-ci-robot-framework.svg)](https://badge.fury.io/py/rz-ci-robot-framework)
[![Python versions](https://img.shields.io/pypi/pyversions/rz-ci-robot-framework.svg)](https://pypi.org/project/rz-ci-robot-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

### From PyPI (Recommended)

```bash
pip install rz-ci-robot-framework
```

### From Source

```bash
git clone https://github.com/renesas/rz-ci-robot-framework.git
cd rz-ci-robot-framework
pip install -e .
```

## Quick Start

```bash
# Run tests for rzsbc board
rz-ci-test rzsbc

# Run with custom configuration
python main.py rzsbc --config my_config.yml

# List available features
python -c "from framework.test_handler import TestHandler; TestHandler('rzsbc').list_features()"
```

## Features

-   **Dynamic Configuration**: YAML-based configuration for easy customization
-   **Multiple Board Support**: Support for various RZ board types (rzsbc, rzv2h, etc.)
-   **Feature Libraries**: Pre-built libraries for I2C, SPI, GPIO, CAN, etc.
-   **Serial Communication**: Automated board login and command execution
-   **Comprehensive Reporting**: HTML and XML reports with detailed logs
-   **Template-based Testing**: Parameterized tests for multiple configurations

## Supported Features

-   **I2C**: Device detection and communication testing
-   **SPI**: Interface testing and data transfer validation
-   **GPIO**: Pin control and state verification
-   **CAN**: Bus communication testing
-   **Ethernet**: Network connectivity validation
-   **USB**: Device detection and enumeration
-   **Overlay**: Device tree overlay testing

## Configuration

Create a `config.yml` file to define your board configurations:

```yaml
board_configs:
    rzsbc:
        enabled: true
        serial_port: "/dev/ttyUSB0"
        baud_rate: 115200
        images:
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
```

## Usage Examples

### Basic Testing

```bash
# Test specific board
python main.py rzsbc

# Test with dry run
python main.py rzsbc --dry-run

# Test with custom config
python main.py rzsbc --config custom_config.yml
```

### Python API

```python
from framework.test_handler import TestHandler

# Initialize test handler
handler = TestHandler(board_type='rzsbc')

# List available features
handler.list_features()

# Run tests
result = handler.run_board()
```

### Robot Framework Integration

```robotframework
*** Settings ***
Library    libraries/I2CLibrary.py
Library    libraries/LoginLibrary.py

*** Test Cases ***
Test I2C Communication
    ${conn}=    Login To Board    rzsbc
    Init I2C Library    ${conn}
    ${result}=    Verify I2C Address Present    0    12
    Should Be True    ${result}
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/renesas/rz-ci-robot-framework.git
cd rz-ci-robot-framework

# Install in development mode
pip install -e .

# Run tests
python main.py rzsbc
```

### Running Tests

```bash
# Run individual test
robot test.robot

# Run I2C tests
robot test/i2c/i2c.robot

# Run with specific board type
robot --variable BOARD_TYPE:rzsbc test/i2c/i2c.robot
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:

-   GitHub Issues: https://github.com/renesas/rz-ci-robot-framework/issues
-   Documentation: https://github.com/renesas/rz-ci-robot-framework/wiki

## Changelog

### 1.0.0 (2024-01-XX)

-   Initial release
-   Support for I2C, SPI, GPIO, CAN, Ethernet, USB testing
-   Dynamic YAML configuration system
-   Multiple board support (rzsbc, rzv2h)
-   Comprehensive reporting and logging
-   Command-line interface
-   Robot Framework integration
