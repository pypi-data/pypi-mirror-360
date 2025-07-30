# EM05 SMS Library

A Python library for communicating with Quectel EM05 cellular modules via AT commands, specifically designed for SMS operations.

## Features

- Send SMS messages via cellular network
- List and read SMS messages
- Delete SMS messages
- Support for UCS2 encoding for international characters
- Debug logging for troubleshooting
- Factory reset functionality

## Requirements

- Python 3.7+
- pyserial
- Quectel EM05 module connected via USB/serial

## Installation

```bash
pip install pyserial
```

## Quick Start

```python
import em05

# Initialize the EM05 module
dev = em05.EM05(port='/dev/ttyUSB2', debug=True)

# List all SMS messages
messages = dev.sms_list_all()
print(f"Found {len(messages)} SMS messages")

# Send an SMS
response = dev.sms_send(phone_number='10086', text='Hello World!')
print(f"SMS sent: {response.status}")

# Delete all SMS messages
dev.sms_delete_all()

# Close the connection
dev.close()
```

## API Reference

### EM05 Class

#### Constructor
```python
EM05(port='/dev/ttyUSB2', baudrate=115200, timeout=1, debug=False)
```

- `port`: Serial port path (default: '/dev/ttyUSB2')
- `baudrate`: Communication speed (default: 115200)
- `timeout`: Response timeout in seconds (default: 1)
- `debug`: Enable debug logging (default: False)

#### Methods

##### SMS Operations

- `sms_list_all()` → `List[SMSMessage]`
  - Returns all SMS messages from the module
  - Each message includes: store_index, status, sender, timestamp, text

- `sms_send(phone_number: str, text: str)` → `EM05Resp`
  - Sends an SMS message
  - Supports international characters via UCS2 encoding

- `sms_delete_all()` → `EM05Resp`
  - Deletes all SMS messages from storage

##### AT Commands

- `at_write(command: str, params: list)` → `EM05Resp`
  - Execute AT command with parameters
  
- `at_read(command: str)` → `EM05Resp`
  - Query AT command value
  
- `at_exe(command: str)` → `EM05Resp`
  - Execute AT command without parameters

##### Utility

- `info()` → `EM05Resp`
  - Get module information
  
- `reset()` → `List[EM05Resp]`
  - Reset module to factory defaults
  
- `close()`
  - Close serial connection

### Data Classes

#### SMSMessage
```python
@dataclass
class SMSMessage:
    store_index: int    # Message index in storage
    status: str         # Message status (e.g., "REC UNREAD")
    sender: str         # Sender phone number
    timestamp: datetime # Message timestamp with timezone
    text: str          # Message content
```

#### EM05Resp
```python
@dataclass
class EM05Resp:
    status: str      # Response status ("OK", "ERROR", or "")
    raw: str         # Raw response from module
    lines: list[str] # Parsed response lines
```

## AT Commands Reference

This library uses standard AT commands for SMS operations:

- `AT+CMGF=1` - Set SMS text mode
- `AT+CSCS="UCS2"` - Set character set to UCS2
- `AT+CMGL="ALL"` - List all SMS messages
- `AT+CMGS` - Send SMS message
- `AT+CMGD` - Delete SMS messages

For detailed AT command documentation, refer to the [Quectel EM05 AT Commands Manual](https://forums.quectel.com/uploads/short-url/cBnrTmjnCg7OGnqRsk8dIpbHuVX.pdf).

## Configuration

The module automatically configures itself on initialization:
- Sets factory defaults (`AT&F`)
- Enables text mode (`AT+CMGF=1`)
- Disables echo (`ATE0`)
- Sets UCS2 character encoding (`AT+CSCS="UCS2"`)

## Error Handling

The library includes comprehensive error handling:
- Serial communication timeouts
- UCS2 encoding/decoding errors
- AT command response parsing
- Debug logging for troubleshooting

## Example Usage

See `main.py` for a complete example of listing and sending SMS messages.

## License

This project is open source. Please refer to the license file for details.