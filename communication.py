import serial
import time
arduinoData=serial.Serial('COM3',115200)
def led_on():
    arduinoData.write('1'.encode())
    
def led_off():
    arduinoData.write('0'.encode())
time.sleep(2) 