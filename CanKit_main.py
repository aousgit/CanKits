'''
Created on 2021-3-12

@author: aousgit
'''
#coding=utf-8
import sys
from UI2 import Ui_Form
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import *
import time

from ctypes import *
import os

##################### Vector structure from C++ ##########################
##########################################################################
##########################################################################
class s_xl_lin_crc_info(Structure):
    _fields_ = [('id', c_ubyte),
                ('flags', c_ubyte)]
class s_xl_lin_sleep(Structure):
    _fields_ = [('flag', c_ubyte)]
class s_xl_lin_wake_up(Structure):
    _fields_ = [('flag', c_ubyte),
                ('unused', c_ubyte*3),
                ('startOffs', c_uint),
                ('width', c_uint)]
class s_xl_lin_no_ans(Structure):
    _fields_ = [('id', c_ubyte)]
class s_xl_lin_msg(Structure):
    _fields_ = [('id', c_ubyte),
                ('dlc', c_ubyte),
                ('flags', c_ushort),
                ('data', c_ubyte*8),
               ('crc', c_ubyte)  ]
class s_xl_lin_msg_api(Structure):
    _fields_ = [('linMsg', s_xl_lin_msg),
                ('linNoAns', s_xl_lin_no_ans),
                ('linWakeUp', s_xl_lin_wake_up),
                ('linSleep', s_xl_lin_sleep),
               ('linCRCinfo', s_xl_lin_crc_info)  ]
class s_xl_chip_state(Structure):
    _fields_ = [('busStatus', c_ubyte),
                ('txErrorCounter', c_ubyte),
               ('rxErrorCounter', c_ubyte)  ]
class s_xl_can_msg(Structure):
    _fields_ = [('id', c_ulong),
                ('flags', c_ushort),
                ('dlc', c_ushort),
                ('res1', c_ulonglong),
                ('data', c_ubyte*8),
               ('res2', c_ulonglong)  ]
class s_xl_sync_pulse(Structure):
    _fields_ = [('pulseCode', c_ubyte),
                ('time', c_ulong) ]
class s_xl_daio_data(Structure):
    _fields_ = [('flags', c_ushort),
                ('timestamp_correction', c_uint),
                ('mask_digital', c_ubyte),
                ('value_digital', c_ubyte),
                ('mask_analog', c_ubyte),
                ('reserved0', c_ubyte),
                ('value_analog', c_ushort*4),
                ('pwm_frequency', c_uint),
                ('pwm_value', c_ushort),
                ('reserved1', c_uint),
                ('reserved2', c_uint) ]
class s_xl_transceiver(Structure):
    _fields_ = [('event_reason', c_ubyte),
                ('is_present', c_ubyte)] 
class s_xl_daio_piggy_data(Structure):
    _fields_ = [('daioEvtTag', c_uint),
                ('triggerType', c_uint),
                ('digitalInputData', c_uint),
                ('measuredAnalogData0', c_uint),
                ('measuredAnalogData1', c_uint),
                ('measuredAnalogData2', c_uint),
                ('measuredAnalogData3', c_uint)]    
class s_xl_tag_data(Structure):  # 32 bytes , here is union structure ,not a simple struct
    _fields_ = [('msg', s_xl_can_msg),
                ('chipState', s_xl_chip_state),
                ('linMsgApi', s_xl_lin_msg_api),
                ('syncPulse', s_xl_sync_pulse),
                ('daioData', s_xl_daio_data),
                ('transceiver', s_xl_transceiver),
               ('daioPiggyData', s_xl_daio_piggy_data)  ]
class s_xl_tag_data_1(Structure):  # 32 bytes , here is union structure ,not a simple struct
    _fields_ = [('msg', s_xl_can_msg)]
class XL_EVENT(Structure):  
    _fields_ = [('tag', c_ubyte),
               ('chanIndex', c_ubyte),
               ('transId',c_ushort),
               ('portHandle',c_ushort),
               ('flags', c_ubyte),
               ('reserved', c_ubyte),
               ('timeStamp', c_ulonglong),
               ('tagData', s_xl_tag_data_1)]   #s_xl_tag_data
##########################################################################
##########################################################################    

##------------------Class Cankit begin--------------------##

class CanKit ():
    def __init__(self,parent):
        
        dll = WinDLL("vxlapi64.dll")
        if dll== None:
            #print("load Dll error!")
            window.logs("load Dll error!")
        else:
            #print("Dll loaded!")
            window.logs("load Dll OK! Welcome to use CAN_Kit...")
        self.dll = dll
        
        #dll.function init
        self.xlOpen = dll.xlOpenDriver
        self.xlClose = dll.xlCloseDriver
        self.xlGetApp = dll.xlGetApplConfig
        self.xlSetApp = dll.xlSetApplConfig
        self.xlGetChannelMask = dll.xlGetChannelMask
        self.xlOpenPort = dll.xlOpenPort
        self.xlCanSetChannelBitrate = dll.xlCanSetChannelBitrate
        self.xlActivateChannel = dll.xlActivateChannel
        self.xlSetNotification = dll.xlSetNotification
        self.xlDeactivate = dll.xlDeactivateChannel
        self.xlCanTransmit = dll.xlCanTransmit
        self.xlClosePort = dll.xlClosePort
        
        
        self.appName = "CANK1"
        ret = self.xlOpen()
        window.logs("xlOpenDriver return " + str(ret))
        
        self.hwType = [c_ulong(0),c_ulong(1),c_ulong(55),c_ulong(57),c_ulong(59)]    
                    #{0:"None", 1:"Virtual", 55:"VN1610", 57:"VN1630", 59:"VN1640"}
        self.appChannel=[c_ulong(0),c_ulong(1),c_ulong(2),c_ulong(3)]
        self.hwIndex = [c_ulong(0),c_ulong(1),c_ulong(2),c_ulong(3)]
        self.hwChannel = [c_ulong(0),c_ulong(1),c_ulong(2),c_ulong(3)]
        self.busType = c_ulong(1)   #XL_BUS_TYPE_CAN
        
    def __del__(self):
        self.xlClose()      #close driver
        pass    
    
    def OpenPorts(self):
        #3 steps
        #1st, GetChannelMask
        #2nd, Permission
        #3rd, OpenPort
        pass
    
    def SetAppConfig(self,iIndex=1):
        
        #1st, get hwType from comboBox
        dict_num = {0:0, 1:2, 2:2, 3:2, 4:2} # use 2 channel for all device firstly- 2021/3/17
        iChannel_num = dict_num[iIndex]
        window.logs("this device has "+ str(iChannel_num) + " channels")
      
        
        #2nd, get hwType
        hwType = self.hwType[iIndex]
        
        #3rd, set channels 
        for i in range(iChannel_num):
            xlStatus = self.xlSetApp(self.appName,self.appChannel[i],hwType,self.hwIndex[0],self.hwChannel[i],self.busType)
            #print(self.appName,"xlstatus_setApp = ",str(xlStatus),str(self.appChannel[i]))
            if xlStatus != 0: break
        
        self.GetAppConfig()
        pass
    
    def GetAppConfig(self):
        appChannel = [c_ulong(0),c_ulong(1),c_ulong(2),c_ulong(3)]
        hwType = c_ulong(1)
        hwIndex = c_ulong(0)
        hwChannel = c_ulong(0)
        busType = c_ulong(1)
        
        pAppChannel = pointer(appChannel[0])
        pHwType = pointer(hwType)
        pHwIndex = pointer(hwIndex)
        pHwChannel = pointer(hwChannel)
        
        #{0:"None", 1:"Virtual", 55:"VN1610", 57:"VN1630", 59:"VN1640"}   
        dict_HW = {0:"None", 1:"Virtual", 55:"VN1610", 57:"VN1630", 59:"VN1640"}        
        dict_hwIndex = {0:0,1:1,55:2,57:3,59:4}
        xlStatus = self.xlGetApp(self.appName,appChannel[0],pHwType,pHwIndex,pHwChannel,busType)
        print (self.appName,appChannel[0],hwType.value, hwIndex.value, hwChannel.value, busType)
        if xlStatus==255:
            self.SetAppConfig()
            return xlStatus
        i=0
        window.comboBox_hwType.setCurrentIndex(dict_hwIndex[hwType.value])
        while xlStatus == 0:
            window.logs("CAN"+str(appChannel[i].value)+" "+str(dict_HW[hwType.value])+" "+str(hwIndex.value)+" channel "+str(hwChannel.value))
            i+=1
            xlStatus = self.xlGetApp(self.appName,appChannel[i],pHwType,pHwIndex,pHwChannel,busType)
            if xlStatus != 0: break
            print (xlStatus,self.appName,appChannel[i],hwType.value, hwIndex.value, hwChannel.value, busType)
        
        return xlStatus    

##------------------Class Cankit end--------------------##



class CanKitMain(QWidget,Ui_Form):
    def __init__(self):
        super(CanKitMain, self).__init__()
        self.setupUi(self)  
        self.init_ui()  

    def init_ui(self):
        self.pushButton.clicked.connect(self.show1)
        self.BTN_Device.clicked.connect(self.chooseDevice)
        self.BTN_empty.clicked.connect(self.emptyText)
        self.lineEdit.setText("0")
        self.thread= None
        
        self.comboBox.setCurrentIndex(3)
        self.comboBox_2.setCurrentIndex(3)
        self.comboBox_3.setCurrentIndex(3)
        
    def emptyText(self):
        self.textBrowser.clear()
        pass
    
    def show1(self):
        if self.thread == None:
            self.thread = TH1()     #instance of thread
            self.thread.running = True
            self.thread.signal.connect(self.callback)   #connect to callback
            print("tread set!")
            self.thread.start( )    #start thread
        else:
            self.thread.running = False
            self.thread.quit()
            self.thread = None
            
    def chooseDevice(self):
        global cankit
        #{0:"None", 1:"Virtual", 55:"VN1610", 57:"VN1630", 59:"VN1640"}
        iIndex = self.comboBox_hwType.currentIndex()
        self.logs("device selected " + str(iIndex))
        ret = cankit.SetAppConfig(iIndex)
        if ret!= 0: return
        ret = cankit.OpenPorts()
            

        pass
            
    def callback(self): #callback
        #print("enter Callback...")
        iIn = self.lineEdit.text()
        i = int(iIn)
        i += 10;
        self.lineEdit.setText(str(i))
        self.lcdNumber.display(str(i))
        
    def logs(self,s):
        self.textBrowser.append(s)
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End) 
            
    pass        
        


class TH1(QThread):
    signal = pyqtSignal(int) #fill in para
    def __init__(self):
        super().__init__()
        
    def __del__(self):
        self.wait()
        
    def run(self):
        print("Thread run")
        i = 1;
        for i in range(1000):
            if self.running == False: break
            self.signal.emit(i) #emit signal
            print("signal emitted!"+ str(i))
            time.sleep(0.2)







if __name__ == "__main__":
    app = QApplication(sys.argv[1:])

    window = CanKitMain()
    
    ########################
    cankit = CanKit(None)
    cankit.GetAppConfig()

    
    
    ########################
    window.show()

    sys.exit(app.exec_())