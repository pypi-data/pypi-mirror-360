import time
from datetime import datetime, timezone, timedelta
import serial
from typing import Union, List
import logging
from dataclasses import dataclass

@dataclass
class EM05Resp:
    status: str
    raw: str
    lines: list[str]

@dataclass
class SMSMessage:
    store_index: int
    status: str
    sender: str
    timestamp: datetime
    text: str

class EM05:
    def __init__(self, port='/dev/ttyUSB2', baudrate=115200, timeout=1, debug=False):
        self.serial = serial.Serial(port, baudrate)
        self.serial.flush()
        self.timeout = timeout

        # Set up logging
        self.logger = logging.getLogger('EM05')
        
        # Only configure logger if it doesn't have handlers already (avoid duplicate handlers)
        if not self.logger.handlers:
            self.logger.setLevel(logging.DEBUG if debug else logging.WARNING)
            # Create console handler and set level
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG if debug else logging.WARNING)
            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            # Add formatter to ch
            ch.setFormatter(formatter)
            
            # Add ch to logger
            self.logger.addHandler(ch)
        self.logger.info(f"Initializing EM05 on port {port} with baudrate {baudrate}")

        # Reset the module to factory defaults
        self.reset()
       

    def reset(self) -> list[EM05Resp]:
        """Reset the EM05 module to factory defaults."""
        self.logger.info("Resetting EM05 module to factory defaults")
        resp_list = []
        # Set to factory defaults
        resp_list.append(self.at_exe('AT&F'))
        # Set to TEXT mode
        resp_list.append(self.at_write('AT+CMGF', [1]))
        # Disable echo
        resp_list.append(self.at_exe('ATE0'))
        # Set charset to UCS2
        resp_list.append(self.at_write('AT+CSCS', ['UCS2']))
        # Clear any existing buffer
        self._clear_buffer()
        self.logger.info("EM05 reset completed")
        return resp_list

    def _ucs2hex_to_str(self, ucs2hex: str) -> str:
        """Convert UCS2 hex string to a regular string."""
        try:
            bytes_data = bytes.fromhex(ucs2hex)
            return bytes_data.decode('utf-16-be', errors='ignore')
        except Exception as e:
            self.logger.error(f"Failed to decode UCS2 hex: {ucs2hex} with error: {e}")
            return ''
    def _str_to_ucs2hex(self, text: str) -> str:
        """Convert a regular string to UCS2 hex string."""
        try:
            bytes_data = text.encode('utf-16-be')
            return bytes_data.hex().upper()
        except Exception as e:
            self.logger.error(f"Failed to encode string to UCS2 hex: {text} with error: {e}")
            return ''

    def _send_raw_command(self, command: str) -> EM05Resp:
        command = command.strip()
        if not command.endswith('\r'):
            command += '\r'
        self.logger.debug(f"Sending command: {command.strip()}")
        self.serial.flush()
        self.serial.write(command.encode('ascii'))
        return self._read_response()

    def at_write(self, command: str, params: Union[list[Union[int, str, bytes]], None] = None) -> EM05Resp:
        param_str = ''
        if params is not None:
            for i in range(len(params)):
                param = params[i]
                if isinstance(param, str):
                    param_str += '"' + param + '"'
                elif isinstance(param, bytes):
                    param_str += '"' + param.hex().upper() + '"'
                elif isinstance(param, int):
                    param_str += str(param)

                if i < len(params) - 1:
                    param_str += ','
                    
        return self._send_raw_command(f"{command}={param_str}")

    def at_read(self, command: str) -> EM05Resp:
        return self._send_raw_command(f"{command}?")

    def at_test(self, command: str) -> EM05Resp:
        return self._send_raw_command(f"{command}=?")

    def at_exe(self, command: str) -> EM05Resp:
        return self._send_raw_command(f"{command}")

    def _clear_buffer(self):
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

    def _read_response(self, timeout: float = -1) -> EM05Resp:
        if timeout < 0:
            timeout = self.timeout

        response = bytearray()
        timeout_end = time.time() + timeout
        while True:
            if self.serial.in_waiting > 0:
                data = self.serial.read(self.serial.in_waiting)
                response.extend(data)
                self.logger.debug(f"Read {len(data)} bytes from serial")
                # if read, extend the timeout
                timeout_end = time.time() + timeout
            else:
                time.sleep(0.01)

            # if ends with \r\n{OK,ERROR}\r\n, we can stop reading
            if response.endswith(b'\r\nOK\r\n') or response.endswith(b'\r\nERROR\r\n'):
                break

            if time.time() > timeout_end:
                break
        
        self.logger.debug(f"Response received: {response}")
        if not response:
            return EM05Resp(status='', raw='', lines=[])

        response = response.decode('ascii', errors='ignore')
        # extract \r\nSTATUS\r\n in the end of the response
        status = ''
        lines = response.strip().split('\r\n')
        if lines:
            last_line = lines[-1]
            if last_line.startswith('OK'):
                status = 'OK'
            elif last_line.startswith('ERROR'):
                status = 'ERROR'
        if status:
            lines = lines[:-1]
            if len(lines) > 0 and lines[-1] == '':
                lines = lines[:-1]

        resp = EM05Resp(status=status, raw=response, lines=lines)
        self.logger.debug(f"Parsed response status: {status}, lines: {len(lines)}")
        return resp

    def close(self):
        self.serial.close()

    def info(self) -> EM05Resp:
        return self.at_exe('ATI')

    def sms_list_all(self) -> List[SMSMessage]:
        self.logger.info("Listing all SMS messages")
        resp = self.at_write('AT+CMGL', ['ALL'])

        if resp.status != 'OK':
            self.logger.error(f"Failed to list SMS messages: {resp.raw}")
            return []

        cur = 0
        sms_messages = []
        while cur < len(resp.lines):
            line = resp.lines[cur]
            if line.startswith('+CMGL:'):
                # remove the +CMGL: part
                line = line[len('+CMGL:'):].strip()
                parts = line.split(',')
                if len(parts) >= 6:
                    index = int(parts[0].strip())
                    status = parts[1].strip().strip('"')
                    sender = self._ucs2hex_to_str(parts[2].strip('"'))
                    timestamp_str = (parts[4]+','+parts[5]).strip('"')
                    if len(timestamp_str) != len('YY/MM/DD,HH:MM:SS+TZ'):
                        self.logger.error(f"Invalid timestamp format: {timestamp_str}")
                        cur += 1
                        continue

                    tz = int(timestamp_str[-3:])
                    timestamp_str = timestamp_str[:-3]  # remove the timezone part
                    timestamp = datetime.strptime(timestamp_str, '%y/%m/%d,%H:%M:%S')
                    timestamp = timestamp.replace(tzinfo=timezone(timedelta(hours=tz/4)))

                    cur += 1
                    if cur >= len(resp.lines):
                        self.logger.error("Unexpected end of response while reading SMS messages")
                        break
                    text = resp.lines[cur].strip()
                    # parse as UCS2
                    text = self._ucs2hex_to_str(text)
                    sms_message = SMSMessage(
                        store_index=index,
                        status=status,
                        sender=sender,
                        timestamp=timestamp,
                        text=text
                    )
                    sms_messages.append(sms_message)
            cur += 1
        return sms_messages

    def sms_delete_all(self) -> EM05Resp:
        self.logger.info("Deleting all SMS messages")
        return self.at_write('AT+CMGD', [1, 4])

    def sms_send(self, phone_number: str, text: str) -> EM05Resp:
        self.logger.info(f"Sending SMS to {phone_number}: {text}")
        phone_ucs2 = self._str_to_ucs2hex(phone_number)
        text_ucs2 = self._str_to_ucs2hex(text)
        cmd = f'AT+CMGS="{phone_ucs2}"'
        self.serial.write(cmd.encode('ascii') + b'\r')
        time.sleep(0.1)  # Wait for the command to be processed
        self.serial.write(text_ucs2.encode('ascii'))
        self._clear_buffer()
        self.serial.write(b'\x1A')  # Send Ctrl+Z to indicate end
        resp = self._read_response(timeout=5)
        return resp