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
import threading
import datetime

from ctypes import *
import os


g_msg = ""
g_thread_run = False
g_t = 0
g_cnt = 0

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
            window.logs("-------load Dll OK! Welcome to use CAN_Kit-------")
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
        window.logs("------------xlOpenDriver return " + str(ret))
        
        self.hwType = [c_ulong(0),c_ulong(1),c_ulong(55),c_ulong(57),c_ulong(59)]    
                    #{0:"None", 1:"Virtual", 55:"VN1610", 57:"VN1630", 59:"VN1640"}
        self.appChannel=[c_ulong(0),c_ulong(1),c_ulong(2),c_ulong(3)]
        self.hwIndex = c_ulong(0)
        self.hwChannel = [c_ulong(0),c_ulong(1),c_ulong(2),c_ulong(3)]
        self.busType = c_ulong(1)   #XL_BUS_TYPE_CAN
        
        self.hwTypeX = c_ulong(0)
        self.portHandle = c_ulong(0)
        
    def __del__(self):
        self.xlClose()      #close driver
        pass    
    
    def sendOneMsg(self,msg):
        #"18DA10F1 03 22 01 9E 00 00 00 00 "
        list_msg = msg.split()
        _id = list_msg[0]
        iId = int(_id, 16) | 0x80000000
        hexID = hex(iId)
        #print("CANID: ", hexID)
        
        xlEvent = XL_EVENT()
        xlEvent.tag= 10
        xlEvent.tagData.msg.id = iId
        xlEvent.tagData.msg.dlc = 8
        xlEvent.tagData.msg.flags = 0
        xlEvent.tagData.msg.data[0] = int(list_msg[1],16);
        xlEvent.tagData.msg.data[1] = int(list_msg[2],16);
        xlEvent.tagData.msg.data[2] = int(list_msg[3],16);
        xlEvent.tagData.msg.data[3] = int(list_msg[4],16);
        xlEvent.tagData.msg.data[4] = int(list_msg[5],16);
        xlEvent.tagData.msg.data[5] = int(list_msg[6],16);
        xlEvent.tagData.msg.data[6] = int(list_msg[7],16);
        xlEvent.tagData.msg.data[7] = int(list_msg[8],16);
        
        messageCount = c_uint(1)
        pMsgCnt = pointer(messageCount)
        pxlEvent = pointer(xlEvent)
        
        xlStatus = self.xlCanTransmit(self.portHandle,self.Ch1_Mask1, pMsgCnt, pxlEvent)
        #print("xlTransmit = ", xlStatus)
        if xlStatus == 0:
            return 0
        
        pass
    
    
    def OpenPorts(self):
        #3 steps
            #1st, GetChannelMask
        print("enter openports")
        xlChannelMask_1 = self.xlGetChannelMask(self.hwTypeX,self.hwIndex, self.hwChannel[0])
        #print ("xlChannelMask_1",xlChannelMask_1)
        self.Ch1_Mask1 = xlChannelMask_1
        
        if self.hwChannel[1] != None:
            xlChannelMask_2 = self.xlGetChannelMask(self.hwTypeX,self.hwIndex, self.hwChannel[1])
            #print ("xlChannelMask_2",xlChannelMask_2)
        
        xlChannelMask_both = xlChannelMask_1 + xlChannelMask_2
        self.Ch_Mask = xlChannelMask_both
        
            #2nd, Permission
        xlPermission = c_ulong(xlChannelMask_both) #must use c_ulong(), or error
        pXlPermission = pointer(xlPermission)
        
            #3rd, OpenPort
        xLportHandle = c_ulong(0)
        self.portHandle = xLportHandle
        pXLportHandle = pointer(xLportHandle)
        
        xlStatus = self.xlOpenPort(pXLportHandle,self.appName,xlChannelMask_both,pXlPermission,256,3,1)
        #print ("xlOpenport",xlStatus, "xLportHandle",xLportHandle)
        if xlStatus == 0:
            self.Status_openPort = 1
            window.logs("------------xlOpenPort OK-----------")
            window.BTN_SetBitrate.setDisabled(0)
        if xlStatus != 0:
            window.logs("xlOpenport error!")
            return -1    
        return xlStatus
    
    def SetAppConfig(self,iIndex=1):
        
        #1st, get hwType from comboBox
        dict_num = {0:0, 1:2, 2:2, 3:2, 4:2} # use 2 channel for all device firstly- 2021/3/17
        iChannel_num = dict_num[iIndex]
        window.logs("this device has "+ str(iChannel_num) + " channels")
      
        
        #2nd, get hwType
        hwType = self.hwType[iIndex]
        self.hwTypeX = hwType
        
        #3rd, set channels 
        for i in range(iChannel_num):
            xlStatus = self.xlSetApp(self.appName,self.appChannel[i],hwType,self.hwIndex,self.hwChannel[i],self.busType)
            #print(self.appName,"xlstatus_setApp = ",str(xlStatus),str(self.appChannel[i]))
            if xlStatus != 0: break
        
        self.GetAppConfig()
        return xlStatus
    
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
            window.logs("--------CAN"+str(appChannel[i].value)+" "+str(dict_HW[hwType.value])+" "+str(hwIndex.value)+" channel "+str(hwChannel.value))
            i+=1
            xlStatus = self.xlGetApp(self.appName,appChannel[i],pHwType,pHwIndex,pHwChannel,busType)
            if xlStatus != 0: break
            print (xlStatus,self.appName,appChannel[i],hwType.value, hwIndex.value, hwChannel.value, busType)
        
        return xlStatus    

##------------------Class Cankit end--------------------##

g_b_29bit = False

class CanKitMain(QWidget,Ui_Form):
    def __init__(self):
        super(CanKitMain, self).__init__()
        self.setupUi(self)  
        self.init_ui()  

    def init_ui(self):
        
        #self.pushButton.clicked.connect(self.show1)
        self.BTN_Device.clicked.connect(self.chooseDevice)
        self.BTN_empty.clicked.connect(self.emptyText)
        #self.lineEdit.setText("0")
        self.thread= None
        
        
        
        self.comboBox.setCurrentIndex(3)
        self.comboBox_2.setCurrentIndex(3)
        self.comboBox_3.setCurrentIndex(3)
        self.BTN_SetBitrate.clicked.connect(self.setBitRate)
        self.BTN_online.clicked.connect(self.online)
        self.BTN_offline.clicked.connect(self.offline)
        self.BTN_send1.clicked.connect(self.send1msgTest)
        self.BTN_sendmsgs.clicked.connect(self.sendMsgs)
        
        self.BTN_online.setDisabled(1)
        self.BTN_offline.setDisabled(1)
        self.BTN_SetBitrate.setDisabled(1)
        self.BTN_send1.setDisabled(1)
        #self.BTN_sendmsgs.setDisabled(1)
        
        self.sends = {}
        if os.path.exists("sendMsgs.in"):
            self.listWidget.clear()
#             print("file in")
            fp = open("sendMsgs.in")
            slist = fp.readlines()
            
            for ss in slist:
                sky = ss.strip("\n").split(":")
                msgs = sky[1]
                msgs = msgs.replace(",","\n")
                self.sends[sky[0]] = msgs
                self.listWidget.addItem(sky[0])
            print (self.sends)
#             self.listWidget.takeItem(3)
#             print(self.listWidget.count())   
        else:
            pass
        
    def emptyText(self):
        self.textBrowser.clear()
        pass
    
    def listClicked(self):
        #print(12345)
        iIndex = self.listWidget.currentRow()       #########################################2021/3/19 here...
        text1 = self.listWidget.item(iIndex).text()
        output1 = text1+":="+self.sends[text1]
        self.plainTextEdit.setPlainText(self.sends[text1])
        self.logs(output1)
        pass
    
    def online(self):
        global g_thread_run,g_b_29bit
        ##### 6 Thread start.......
        if self.thread == None:
            self.thread = TH1()     #instance of thread
            g_thread_run = True
            self.thread.signal.connect(self.UI_update)   #connect to callback
            print("tread set!")
            self.thread.start( )    #start thread
            self.BTN_online.setDisabled(1)
            self.BTN_offline.setDisabled(0)
            self.BTN_send1.setDisabled(0)
            self.BTN_sendmsgs.setDisabled(0)
            
            s = self.checkBox.checkState()
            if s == 2:g_b_29bit = True
            else: g_b_29bit = False
        
        pass
    
    def offline(self):
        global g_thread_run
        g_thread_run = False
        self.thread.quit()
        self.thread = None
        self.BTN_online.setDisabled(0)
        self.BTN_offline.setDisabled(1)
        self.BTN_send1.setDisabled(1)
        #self.BTN_sendmsgs.setDisabled(1)
        pass
    
    def Timer_1(self):
        global g_t,g_cnt
        
        ss = self.s_list[g_cnt]
        print("ss",ss)
        cankit.sendOneMsg(ss)
        g_cnt += 1
        if g_cnt < len(self.s_list):
            g_t= threading.Timer(self.t_intv,self.Timer_1)
            g_t.start()
        else:
            pass
        pass
    
    def sendMsgs(self):
        global g_t,g_cnt
        s_msgs = self.plainTextEdit.toPlainText()
        
        i_interval = self.Combo_10ms.currentIndex()
        #print("interval_index", i_interval)
        dict_time = {0:0.01, 1:0.1, 2:1}
        t_interval = dict_time[i_interval]
        self.t_intv = t_interval
        self.s_list = s_msgs.split("\n")
        g_cnt = 0
        g_t= threading.Timer(t_interval,self.Timer_1)
        g_t.start()
        
        
     
        pass
    
    def send1msgTest(self):
        
        #cankit.sendOneMsg("18DA10F1 03 22 01 9E 00 00 00 00 ")
               
        
        
        #18dacbf1 05 31 01 05 01 00 01    SGM Unlock
        xlEvent = XL_EVENT()
        xlEvent.tag= 10
        xlEvent.tagData.msg.id = 0x98dacbf1
        xlEvent.tagData.msg.dlc = 6
        xlEvent.tagData.msg.flags = 0
        xlEvent.tagData.msg.data[0] = 0x05;
        xlEvent.tagData.msg.data[1] = 0x31;
        xlEvent.tagData.msg.data[2] = 0x01;
        xlEvent.tagData.msg.data[3] = 0x05;
        xlEvent.tagData.msg.data[4] = 0x00;
        xlEvent.tagData.msg.data[5] = 0x01;
        #xlEvent.tagData.msg.data[6] = 0x00;
        #xlEvent.tagData.msg.data[7] = 0x00;
        
        xlCanTransmit = cankit.dll.xlCanTransmit
        messageCount = c_uint(1)
        pMsgCnt = pointer(messageCount)
        pxlEvent = pointer(xlEvent)
        
        xlStatus = xlCanTransmit(cankit.portHandle,cankit.Ch1_Mask1,pMsgCnt, pxlEvent)
        #print ("xltransmit", xlStatus)
        
        pass
    
    def setBitRate(self):
        global g_thread_run
        ##### 3 SetChannelBitrate
        xlStatus = cankit.xlCanSetChannelBitrate(cankit.portHandle,cankit.Ch_Mask, 500000)
        print ("setbitrate", xlStatus)
        if xlStatus != 0: return
        
        ##### 4 ActivateChannel
        xlStatus = cankit.xlActivateChannel(cankit.portHandle,cankit.Ch_Mask,1,8)
        print ("xlActivateChannel", xlStatus)
        if xlStatus != 0: return
        
        ##### 5 SetNotification
        m_hMsgEvent = c_ulong()
        pMsgEvent = pointer(m_hMsgEvent)
        xlStatus = cankit.xlSetNotification (cankit.portHandle, pMsgEvent, 1);
        print ("xlSetNotification", xlStatus)
        if xlStatus != 0: return
        self.BTN_online.setDisabled(0)
        
        
        pass
    
    def show1(self):
        global g_thread_run
        if self.thread == None:
            self.thread = TH1()     #instance of thread
            g_thread_run = True
            self.thread.signal.connect(self.callback)   #connect to callback
            print("tread set!")
            self.thread.start( )    #start thread
        else:
            g_thread_run = False
            self.thread.quit()
            self.thread = None
            
    def chooseDevice(self):
        global cankit
        #{0:"None", 1:"Virtual", 55:"VN1610", 57:"VN1630", 59:"VN1640"}
        iIndex = self.comboBox_hwType.currentIndex()
        self.logs("device selected " + str(iIndex))
        ret = cankit.SetAppConfig(iIndex)
        if ret!= 0: return
        print("------------openPorts-----------------")
        ret = cankit.OpenPorts()
            

        pass
    def UI_update(self):
        global g_msg
        #print("receive emits")
        #print(g_msg)
        tt2 = datetime.datetime.time(datetime.datetime.now())
        s_tt2 = "["+str(tt2)[:-3]+"]  "
        out = s_tt2 + g_msg
        self.logs(out)
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
    global g_thread_run
    global g_b_29bit
    signal = pyqtSignal(int) #fill in para
    def __init__(self):
        super().__init__()
        
    def __del__(self):
        self.wait()
        
    def run(self):
        global g_msg
        print("Thread run")
        while(g_thread_run):
            xlReceive = cankit.dll.xlReceive
            msgsrx = c_uint(1)
            pMsgsrx = pointer(msgsrx)
            xlEvent = XL_EVENT()
            pxlEvent = pointer(xlEvent)
            #xlString = dll.xlGetEventString
            xlStatus = xlReceive(cankit.portHandle,pMsgsrx,pxlEvent)
            if (xlStatus != 10):
                #print ("xlReceive = ", xlStatus)
                id = xlEvent.tagData.msg.id
                CanType = xlEvent.tagData.msg.id & 0x80000000   # CanType = 0 :11 bit msg
                CanBypass = xlEvent.tagData.msg.id & 0x7fff0000 # Bypass some abnormal 29 bit msg.
                
                id_hex = hex(id)
                list1 = []
                for i in range(8):
                    iData = xlEvent.tagData.msg.data[i]
                    hexData = hex(iData)[2:].zfill(2)
                    list1.append(hexData)
                chanX = xlEvent.chanIndex 
                #print ("channel is ", chanX)
                sData = " ".join(list1)
                Sout =  "CH"+ str(chanX) + ", "+ str( id_hex)+ " "+ sData+" " 
                
###------------save to .ASC file------------###

###-----------------end ASC file------------###             


######-------PID show and save--------

###############################################

##########---CCP show and save--------

###############################################   
                
                if (g_b_29bit):
                    if( CanType== 0):
                        continue
                    else:
                        if (CanBypass==0x1E340000 or CanBypass == 0x1E360000):continue  #bypass some 29bit msg
                        g_msg = Sout
                        self.signal.emit(1) #emit signal
                else:
                    g_msg = Sout
                    self.signal.emit(1) #emit signal
            
            
            
#             print("signal emitted!"+ str(i))
#             time.sleep(0.2)







if __name__ == "__main__":
    app = QApplication(sys.argv[1:])

    window = CanKitMain()
    
    ########################
    cankit = CanKit(None)
    cankit.GetAppConfig()

    
    
    ########################
    window.show()

    sys.exit(app.exec_())