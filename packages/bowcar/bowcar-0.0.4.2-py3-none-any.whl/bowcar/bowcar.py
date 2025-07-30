import serial
import serial.tools.list_ports
import time

class BowCar:
    """
    BowCar class for controlling a bowcar via serial communication.
    바우카를 제어하기 위한 BowCar 클래스입니다.
    """
    def __init__(self):
        self.port = self._find_arduino_port()
        self.connection = None

        if self.port:
            try:
                self.connection = serial.Serial(self.port, 9600, timeout=1)
                print(f'connected! 연결 성공! (port : {self.port}')
                time.sleep(2)
            except serial.SerialException :
                print(f'Failed to connect! 연결 실패! (port : {self.port})')

    def _find_arduino_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Arduino' in port.description or 'CH340' in port.description:
                return port.device
        print('No Arduino found! 아두이노를 찾을 수 없습니다.')
        return None
    
    def send_command(self, command: str):
        """
        Send a command to the bowcar.
        바우카에 명령을 전송합니다.
        """
        if self.connection and self.connection.is_open:
            full_command = command + '\n'
            self.connection.write(full_command.encode('utf-8'))
        else:
            print('Connection is not open! 연결 되지 않아 명령을 보낼 수 없습니다.')

    def close(self):
        """
        Close the serial connection.
        시리얼 연결을 닫습니다.
        """
        if self.connection:
            self.connection.close()
            print('Connection closed! 연결이 닫혔습니다.')
        else:
            print('No connection to close! 닫을 연결이 없습니다.')
        
    def red_on(self):
        self.send_command('lrn')

    def red_off(self):
        self.send_command('lrf')

    def blue_on(self):
        self.send_command('lbn')

    def blue_off(self):
        self.send_command('lbf')

    def all_light_on(self):
        self.send_command('lan')
