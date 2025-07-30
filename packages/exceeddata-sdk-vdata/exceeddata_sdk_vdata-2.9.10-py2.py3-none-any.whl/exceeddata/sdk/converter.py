from .vdata import VDataReaderFactory, VDataReader, VDataByteReader

from datetime import datetime
from can import Message, ASCWriter
from .blf import BLFWriter
import math

def colParser(col):
    arr = col.split("_")
    if (len(arr)!= 2):
        return 0,0
    else:
        return int(arr[0]), int (arr[1],base=16)

class VswToBlfConverter:
    '''
    A seekable reader class for wrapping around byte array when data file has already been
    read into byte array.
    '''
    def __init__(self, inputPaths, outputFilename, signals=[]):
        self._seekables = []
        for fname in inputPaths:
            inFile = open(fname, "rb")
            data = inFile.read()
            self._seekables.append(VDataByteReader( data))
        self._outputFilename = outputFilename
        self._signals = signals

    def convert(self, colParserFun=colParser ):
        factory = VDataReaderFactory()
        factory.setDataReaders(self._seekables)
        factory.setSignals(signals=self._signals)
        reader = factory.open()
        vdf = reader.df()
        #print(vdf.cols)
        #store the coloumn index to channel_id, message_id tuple mapping. 
        #这里用来保留信号列与channel_id, message_id之间的对应关系，第一列总是为时间，所以会少一列
        can_info= []
        for signal in vdf.cols(): 
            channel_id, message_id, frame_type = colParserFun(signal)

            can_info.append([channel_id,message_id, frame_type])
            #if (len(arr)!= 2):
            #    can_info.append(None)
            #else:
                #You can customize here for you own column name format.
                #这里需要做容错的处理，如果信号中有下划线，但不是数值就会出错。
            #    channel_id =int(arr[0])
            #    message_id = int (arr[1],base=16)
                
        

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("  " + current_time)
        blfwriter = BLFWriter(self._outputFilename)
        

        #itorator for each row and data column.
        #遍历解出来的每一行数据
        for row in vdf.objects():
            if blfwriter.start_timestamp == None :
                blfwriter.start_timestamp = row[0]//1000
            #第一列是时间，所以从第二列信号数据开始分析
            #time for first column, so we start from the second column.
            for i in range (1, len(row)):
                    #store the signal byte array for not null column data.
                    #如果信号非空，则生成相应的数据
                    if row[i] != None and isinstance (row[i], list) and  can_info[i-1][0]!=-1:
                        msg = Message(timestamp=row[0]/1000.0, channel=can_info[i-1][0] -1 ,arbitration_id=can_info[i-1][1],data= row[i], is_fd=True, is_extended_id = False)
                        frame_type = 0
                        if (can_info[i-1][2] ==2 ):
                            frame_type = 11 #LIN_MESSAGE_TYPE in blf
                        #写入BLF文件
                        blfwriter.on_message_received(msg, frame_type)


                    elif row[i] != None   and  can_info[i-1][0]!=-1:
                        data=[1]
                        data[0] =row[i]
                        msg = Message(timestamp=row[0]/1000.0, channel=can_info[i-1][0] -1 ,arbitration_id=can_info[i-1][1],data= data, is_fd=True, is_extended_id = False)
                        #写入BLF文件
                        blfwriter.on_message_received(msg)

        #finalize the BLF file and flush to disk
        #将BLF文件终结，写入磁盘
        blfwriter.stop()
        
class VswToAscConverter:
    '''
    A seekable reader class for wrapping around byte array when data file has already been
    read into byte array.
    '''
    def __init__(self, inputPaths, outputFilename, signals=[]):
        self._seekables = []
        for fname in inputPaths:
            inFile = open(fname, "rb")
            data = inFile.read()
            self._seekables.append(VDataByteReader( data))
        self._outputFilename = outputFilename
        self._signals = signals

    def convert(self, colParserFun=colParser):
        factory = VDataReaderFactory()
        factory.setDataReaders(self._seekables)
        factory.setSignals(signals=self._signals)
        reader = factory.open()
        vdf = reader.df()
        #print(vdf.cols)
        #store the coloumn index to channel_id, message_id tuple mapping. 
        #这里用来保留信号列与channel_id, message_id之间的对应关系，第一列总是为时间，所以会少一列
        can_info= []
        cols  = vdf.cols()
        for signal in vdf.cols(): 
            channel_id, message_id, frame_type = colParserFun(signal)
            if frame_type!=2:
                can_info.append([channel_id,message_id&0x7fffffff, message_id&0x8000000 != 0]) 
            else:
                can_info.append([-1,-1, -1])
                   

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("  " + current_time)
        writer = ASCWriter(self._outputFilename)

        #itorator for each row and data column.
        #遍历解出来的每一行数据
        for row in vdf.objects():
            #第一列是时间，所以从第二列信号数据开始分析
            #time for first column, so we start from the second column.
            for i in range (1, len(row)):
                    #store the signal byte array for not null column data.
                    #如果信号非空，则生成相应的数据
                    if row[i] != None and isinstance(row[i], (list)) and  can_info[i-1][0]!=-1:
                        msg = Message(timestamp=row[0]/1000.0, channel=can_info[i-1][0]-1,arbitration_id=can_info[i-1][1],data= row[i], is_fd=True, is_extended_id =can_info[i-1][2])
                        #写入ASC文件
                        writer.on_message_received(msg)
                    elif row[i] != None and  can_info[i-1][0]!=-1:
                        data=[1]
                        data[0] =row[i]
                        msg = Message(timestamp=row[0]/1000.0, channel=can_info[i-1][0] -1 ,arbitration_id=can_info[i-1][1],data= data, is_fd=True, is_extended_id = can_info[i-1][2])
                        #写入ASC文件
                        writer.on_message_received(msg)

        #finalize the ASC file and flush to disk
        #将ASC文件终结，写入磁盘
        writer.stop()