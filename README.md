# CanKits
CAN signal tool(python) based on vector's driver.

## 2021/3/23
Steps update:
5. transmit messages
5.1 one defined message test function -- done
5.2 fill message in lineEdit and transmit it --done
5.3 series messages with different time interval  -- done
6. mask bit29 messages  -- when connect to vehicle, CAN messages too much to fresh UI, need to be fixed next.

## 2021/3/18
Steps update:
1. init a python program  with PyQt's QThread.      ---- done
2. use Ctype to translate structure to Python's class and adapt DLL.    ----done
3. Connect to vehicle CAN.        ----done.
4. receive messages and filter by QThread.        ----done.

## 2021/3/15
1. learn how to use github.
2. translate C++ program into python with PyQt5 GUI.
3. Based on Vector's driver. And DLL file is "vxlapi.dll".

### Target
This program is a CAN message tool(CAN 2.0B - support 29bits). Which would be able to connect to vehicle's CAN from OBD port, receive messages from CAN, transmit messages, clear DTC codes, record signals, read and show PIDs, even config CCP\ read and show internal data of ECU.

Plan to seperate into several steps:
1. init a python program  with PyQt's QThread.
2. use Ctype to translate structure to Python's class and adapt DLL.
3. Connect to vehicle CAN.
4. receive messages and filter by QThread.
5. transmit messages.
6. import file to transmit group of messages.
7. PID read , varible show and record.
8. CCP config, varible show and record.
9. TBD...
