# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2024 Smart Software for Car Technologies Inc. and EXCEEDDATA
#     https://www.smartsct.com
#     https://www.exceeddata.com
#
#                            MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of a copyright holder
# shall not be used in advertising or otherwise to promote the sale, use 
# or other dealings in this Software without prior written authorization 
# of the copyright holder.
#
# Author:  Nick Xie
# Version: 2.9.10
#
# Note: for specification flag compatibility, it is rare that vsw uses snappy.
# Uncomment the following if used and python-snappy is installed.
# import snappy

import sys
import heapq
import snappy
import zstd, gzip, binascii
import struct as _struct
from collections import deque
from math import nan, isnan, floor, log, log10, exp, pow

import logging
logger = logging.getLogger()

__all__ = ['VDataByteReader', 'VDataFrame', 'VDataMeta', 'VDataReader', 'VDataReaderFactory', 'VDataSignalFilter']

class VDataRow:
    def __init__(self, time, values):
        self._time = time
        self._values = values

    def __repr__(self): 
        return '{time=' + str(self._time) + ', values=' + str(self._values) + '}'

class VDataRecord:
    def __init__(self, time, values):
        self._time = time
        self._values = values

    def __repr__(self): 
        return '{time=' + str(self._time) + ', values=' + str(self._values) + '}'

class VDataSeriesPair:
    def __init__(self, time, value):
        self._time = time
        self._value = value

    def __repr__(self): 
        return '{time=' + str(self._time) + ', value=' + str(self._value) + '}'
    
    def time(self):
        return self._time

    def value(self):
        return self._value

class VDataByteReader:
    '''
    A seekable reader class for wrapping around byte array when data file has already been
    read into byte array.
    '''
    def __init__(self, data):
        '''
        The constructor for seekable byte array reader.

        Args:
            data (array_like): underlying byte array 
        '''
        self._data = data
        self._length = len(self._data)
        self._pos = 0

    def read(self, length):
        '''
        Read bytes by the specified length.

        Args:
            length (int): the length to read

        Returns:
            array_like        
        '''
        _end = self._pos + length
        if (_end >= self._length):
            _end = self._length
        _bb = self._data[self._pos:_end]
        self._pos = _end
        return _bb
    
    def seek(self, pos):
        '''
        Seek to the target position. If the target position is less than or equals to zero, 
        seek to the zero position.  If the target position is more than the length of the
        underlying byte array, seek to the end of the byte array.

        Args:
            pos (int): the target position
        '''
        if (pos > 0):
            if (pos >= self._length):
                self._pos = self._length
            else:
                self._pos = pos
        else:
            self._pos = 0

    def skip(self, length):
        '''
        Skip the specified length. If the ending position is more than the length of the
        underlying byte array, skip to the end of the byte array.

        Args:
            length (int): the length to skip
        '''
        if (length > 0):
            pos = self._pos + length
            if (pos >= self._length):
                self._pos = self._length
            else:
                self._pos = pos
        
    def close(self):
        '''
        Close the reader.
        '''
        pass

class VDataMeta:
    '''
    A class for the metadata info of data files.

    Examples:
        >>> meta = VDataReader.getMeta(file)
        >>> info = meta.extendedInfo()
    '''
    def __init__(self, formatVersion=0, compressMethod=0, encryptMethod=0, blocksCount=0, storageStartTime=0, storageEndTime=0, queryStartTime=0, queryEndTime=0, extendedInfo=None, pageSizeCode=0, keyTypeCode=0):
        '''
        The constructor for the meta info. For valid values see VData format specification.

        Args:
            formatVersion (int): format version
            compressMethod (int): compress method
            encryptMethod (int): encryption method
            blocksCount (int): count of bucket blocks in the data
            storageStartTime (int): earliest time in the data
            storageEndTime (int): last time in the data
            queryStartTime (int): start time filter (inclusive) if the data is generated from an algorithm trigger
            queryEndTime (int): end time filter (inclusive) if the data is generated from an algorithm trigger
            extendedInfo (array_like) extended info whereby implementation may add project-customized information
        '''
        self._formatVersion = formatVersion
        self._compressMethod = compressMethod
        self._encryptMethod = encryptMethod
        self._blocksCount = blocksCount
        self._storageStartTime = storageStartTime
        self._storageEndTime = storageEndTime
        self._queryStartTime = queryStartTime
        self._queryEndTime = queryEndTime
        self._extendedInfo = extendedInfo
        self._pageSizeCode = pageSizeCode
        self._keyTypeCode = keyTypeCode
        

    def __repr__(self): 
        '''
        str() representation.
        '''
        return '{version=' + str(self._formatVersion) + ', compress=' + str(self._compressMethod) + ', encryption=' + str(self._encryptMethod) + ', blocks=' + str(self._blocksCount) + '}'

    def formatVersion(self):
        '''
        Get the data's format version.

        Returns:
            int
        '''
        return self._formatVersion
    
    def compressMethod(self):
        '''
        Get the data's compress method.

        Returns:
            int
        '''
        return self._compressMethod
    
    def encryptMethod(self):
        '''
        Get the data's encryption method.

        Returns:
            int
        '''
        return self._encryptMethod
    
    def blocksCount(self):
        '''
        Get the count of bucket blocks in data.

        Returns:
            int
        '''
        return self._blocksCount
    
    def storageStartTime(self):
        '''
        Get the data's earliest signal time (millisecond) in data. Note that this time 
        may be the evenly-split starting time of the first bucket and slightly 
        different from the actual first signal time.

        Returns:
            millisecond since EPOCH
        '''
        return self._storageStartTime
    
    def storageEndTime(self):
        '''
        Get the data's last signal time (millisecond) in data. Note that this time 
        may be the evenly-split ending time of the last bucket. Also in living bucket
        this time may be slightly different from the actual last signal time.

        Returns:
            millisecond since EPOCH
        '''
        return self._storageEndTime

    def queryStartTime(self):
        '''
        Get the query start time if the data is generated through an algorithm trigger.

        Returns:
            millisecond since EPOCH
        '''
        return self._queryStartTime
    
    def queryEndTime(self):
        '''
        Get the query end time if the data is generated through an algorithm trigger.

        Returns:
            millisecond since EPOCH
        '''
        return self._queryEndTime
    
    def extendedInfo(self):
        '''
        Get the extended info. Custom-implementation may add contents into this part of
        data buffer.

        Returns:
            array_like
        '''
        return self._extendedInfo
    
    def getPageSize(self):
        '''
        get the page size. default is 64k
        '''
        pageSizeCode = self._pageSizeCode & 0x0f
        if  pageSizeCode == 0: #default 64k
            return 0x10000
        if pageSizeCode == 1: #32k
            return  0x8000
        if pageSizeCode == 2: #16k
            return  0x4000
        if pageSizeCode == 3: #8k 
            return  0x2000        
        if pageSizeCode == 4:  #128k 
            return 0x20000  

        return  0x10000  
    
    def getStorageIdLength(self):
        pageSizeCode = self._pageSizeCode & 0x0f
        if (pageSizeCode != 1):
            return 8
        if self._pageSizeCode & 0xf0  == 0:
            return 5
        else:
            return 6 
    
    def getSeriesTimestampLength (self):
        if (self._keyTypeCode & 0x0f ==1 ):
            return 43
        else:
            return 41
            
class VDataBucket(object):
    def __init__(self):
        self.startTime = 0
        self.endTime = 0
        self.living = 0
        self.notime = 0
        self.cycle = 0
        self.crc = 0
        self.seriesBuckets = []

    def getStartTime(self):
        return self.startTime

    def setStartTime(self, time):
        t = str(time)
        if len(t) > 13:
            self.startTime = int(time / int(round(pow(10, len(t) - 13))))
        else:
            self.startTime = time

    def getEndTime(self):
        return self.endTime
    
    def setEndTime(self, time):
        t = str(time)
        if len(t) > 13:
            self.endTime = int(time / int(round(pow(10, len(t) - 13))))
        else:
            self.endTime = time

    def getCycle(self):
        return self.cycle
    
    def setCycle(self, cycle):
        self.cycle = cycle

    def isLiving(self):
        return self.living
    
    def setLiving(self, living):
        self.living = living
    
    def getCrc(self):
        return self.crc
    
    def setCrc(self, crc):
        self.crc = crc
    
    def setNoTime(self, notime):
        self.notime = notime

    def getSeriesBuckets(self):
        return self.seriesBuckets

    def addSeriesBucket(self, seriesBucket):
        self.seriesBuckets.append(seriesBucket)
    
    def intersects(self, b):
        st = b.startTime
        et = b.endTime
        
        if (self.startTime == 0 or st == 0):
            return False                  # extreme case handling, should not happen, always have bucket start time
        
        if (self.endTime == 0 or et == 0):
            return self.startTime == st   # old version with unknown end time

         # check bucket intersect b and b intersect bucket
        return (self.startTime >= st and self.startTime <= et) or (self.endTime >= st and self.endTime <= et) or (st >= self.startTime and st <= self.endTime) or (et >= self.startTime and et <= self.endTime)

    def merge(self, b):
        if len(b.seriesBuckets) > 0:
            sset = {""}
            for i in range(len(self.seriesBuckets)):
                sset.add(self.seriesBuckets[i].name)
            
            for i in range(len(b.seriesBuckets)):
                if (b.seriesBuckets[i].name not in sset):
                    self.seriesBuckets.append(b.seriesBuckets[i])
        
        return self

    def __repr__(self): 
        return '{cycle=' + str(self.cycle) + ', start=' + str(self.startTime) + ', end=' + str(self.endTime) + ', living=' + str(self.living) + ', notime=' + str(self.notime) + '}'

class VDataFormulaNone:
    def __init__(self, name):
        self._name = name
    
    def __repr__(self): 
        return '{name=' + str(self._name) + '}'
    
    def apply(self, val):
        return val

class VDataFormulaLinear:
    def __init__(self, name, factor, offset):
        self._name = name
        self._factor = factor
        self._offset = offset
    
    def apply(self, val):
        return self._factor * val + self._offset

class VDataFormulaPolynomial:
    def __init__(self, name, p0, p1, p2, p3, p4, p5):
        self._name = name
        self._p0 = p0
        self._p1 = p1
        self._p2 = p2
        self._p3 = p3
        self._p4 = p4
        self._p5 = p5
    
    def apply(self, val):
        try:
            numer = self._p1 - (self._p3 * (val - self._p4 - self._p5))
            denom = self._p2 * (val - self._p4 - self._p5) - self._p0
            return numer / denom
        except ZeroDivisionError:
            return None

class VDataFormulaExponential:
    def __init__(self, name, p0, p1, p2, p3, p4, p5, p6):
        self._name = name
        self._p0 = p0
        self._p1 = p1
        self._p2 = p2
        self._p3 = p3
        self._p4 = p4
        self._p5 = p5
        self._p6 = p6
        
        self._p3zero = float(self._p3).is_integer() and int(self._p3) == 0
        self._p0zero = float(self._p0).is_integer() and int(self._p0) == 0

        if self._p3zero:
            if self._p0zero:
                raise Exception('FORMAT_VDATA_FORMULA_EXPONENTIAL_P3_P0_BOTH_ZERO')
            if float(self._p1).is_integer() and int(self._p1) == 0:
                raise Exception('FORMAT_VDATA_FORMULA_EXPONENTIAL_P3_P1_BOTH_ZERO')
        if self._p0zero and (float(self._p4).is_integer() and int(self._p4) == 0):
            raise Exception('FORMAT_VDATA_FORMULA_EXPONENTIAL_P0_P4_BOTH_ZERO')

    def apply(self, val):
        try:
            if self._p3zero:
                return log(((val - self._p6) * self._p5 - self._p2) / self._p0) / self._p1
            if self._p0zero:
                denom = val - self._p6
                return log((self._p2 / denom - self._p5) / self._p3) / self._p4
        except ZeroDivisionError:
            return None


class VDataFormulaLogarithmic:
    def __init__(self, name, p0, p1, p2, p3, p4, p5, p6):
        self._name = name
        self._p0 = p0
        self._p1 = p1
        self._p2 = p2
        self._p3 = p3
        self._p4 = p4
        self._p5 = p5
        self._p6 = p6
        
        self._p3zero = float(self._p3).is_integer() and int(self._p3) == 0
        self._p0zero = float(self._p0).is_integer() and int(self._p0) == 0

        if self._p3zero:
            if self._p0zero:
                raise Exception('FORMAT_VDATA_FORMULA_LOGARITHMIC_P3_P0_BOTH_ZERO')
            if float(self._p1).is_integer() and int(self._p1) == 0:
                raise Exception('FORMAT_VDATA_FORMULA_LOGARITHMIC_P3_P1_BOTH_ZERO')
        if self._p0zero and (float(self._p4).is_integer() and int(self._p4) == 0):
            raise Exception('FORMAT_VDATA_FORMULA_LOGARITHMIC_P0_P4_BOTH_ZERO')

    def apply(self, val):
        try:
            if self._p3zero:
                return exp(((val - self._p6) * self._p5 - self._p2) / self._p0) / self._p1
            if self._p0zero:
                denom = val - self._p6
                return exp((self._p2 / denom - self._p5) / self._p3) / self._p4
        except ZeroDivisionError:
            return None

class VDataFormulaRational:
    def __init__(self, name, p0, p1, p2, p3, p4, p5):
        self._name = name
        self._p0 = p0
        self._p1 = p1
        self._p2 = p2
        self._p3 = p3
        self._p4 = p4
        self._p5 = p5
    
    def apply(self, val):
        try:
            numer = val * val * self._p0 + val * self._p1 + self._p2
            denom = val * val * self._p3 + val * self._p4 + self._p5
            return numer / denom
        except ZeroDivisionError:
            return None

class VDataFormulaDecode:
    def __init__(self, name, _list):
        self._name = name
        if (_list is None or not isinstance(_list, list) or len(_list) == 0):
            raise Exception('FORMAT_VDATA_FORMULA_DECODE_LIST_EMPTY')
        if (len(_list) % 2 != 0):
            raise Exception('FORMAT_VDATA_FORMULA_DECODE_LIST_ODD_SIZE')
               
        self._list = _list
        self._lsize = int(len(self._list) / 2)

    def apply(self, val):
        x = self._list[0]
        y = self._list[1]
        compare = x - val
        if (compare >= 0):
            return y
        for i in range(1, self._lsize):
            compare = self._list[2 * i] - val
            if (compare < 0):
                x = self._list[2 * i]
                y = self._list[2 * i + 1]
            elif (compare == 0):
                return self._list[2 * i + 1]
            else:
                if ((self._list[2 * i] - val) - (val - x) >= 0):
                    return y
                else:
                    return self._list[2 * i + 1]
        
        return self._list[2 * self._lsize -1]

class VDataFormulaInterpolate:
    def __init__(self, name, _list):
        self._name = name
        if (_list is None or not isinstance(_list, list) or len(_list) == 0):
            raise Exception('FORMAT_VDATA_FORMULA_INTERPOLATE_LIST_EMPTY')
        if (len(_list) % 2 != 0):
            raise Exception('FORMAT_VDATA_FORMULA_INTERPOLATE_LIST_ODD_SIZE')
               
        self._list = _list
        self._lsize = int(len(self._list) / 2)

    def apply(self, val):
        try:
            x1 = self._list[0]
            y1 = self._list[1]
            compare = x1 - val
            if (compare > 0):
                x2 = self._list[2]
                y2 = self._list[3]
                a = (y2 - y1) / (x2 - x1)
                return y1 + a * (val - x1)
            elif (compare == 0):
                return y1

            for i in range(1, self._lsize - 1):
                x1 = self._list[2 * i]
                y1 = self._list[2 * i + 1]
                compare = x1 - val
                if (compare > 0):
                    x2 = self._list[2 * i + 2]
                    y2 = self._list[2 * i + 3]
                    a = (y2 - y1) / (x2 - x1)
                    return y1 + a * (val - x1)
                elif (compare == 0):
                    return y1
            
            x2 = self._list[2 * self._lsize - 2]
            y2 = self._list[2 * self._lsize - 1]
            compare = x2 - val
            if (compare == 0):
                return y2
            else:
                a = (y2 - y1) / (x2 - x1)
                return y1 + a * (val - x1)
        except ZeroDivisionError:
            return None

class VDataFormulaArray:
    def __init__(self, name, formulas):
        self._name = name
        self._formulas = formulas
    
    def apply(self, val):
        vals = []
        #for single byte vector data
        if isinstance(val, int):
            vals.append(val)
            return vals
        
        for i in range(len(self._formulas)):
            vals.append(self._formulas[i].apply(val[i]))
        return vals

class VDataFormulaBlob:
    def __init__(self, name):
        self._name = name
        self._signalDecoder = None
    
    def apply(self, val):
        if(self._signalDecoder != None):
            return self._signalDecoder.decode(val)
        else:
            return val
    
    def setSignalDeocder(self,decoder):
        self._signalDecoder = decoder
        
    def getSignalDecoder (self):
        return self._signalDecoder

class VDataFormulaNamedArray (VDataFormulaArray):
    def __init__(self, name, formulas):
        super().__init__(name, formulas)

class VDataFormulaStruct:
    def __init__(self, name, formulas):
        self._name = name
        self._formulas = formulas
    
    def apply(self, val):
        vals = {}
        for i in range(len(self._formulas)):
            vals[self._formulas[i]._name] = self._formulas[i].apply(val)
        return vals

class VDataFormulaFactory:
    def build(self, desc, insensitiveCase=False):
        if len(desc) == 0:
            raise Exception('FORMAT_VDATA_KEY_DESC_EMPTY')
        
        if ('|' not in desc):
            name = desc.strip().lower() if insensitiveCase else desc.strip()
            return VDataFormulaNone(name)
        
        idx = desc.find('|')
        if (idx == 0):
            raise Exception('FORMAT_VDATA_KEY_DESC_INVALID: ' + desc)

        name = desc[0:idx].strip()
        if (len(name) == 0):
            raise Exception('FORMAT_VDATA_KEY_DESC_INVALID: ' + desc)
        if (insensitiveCase):
            name = name.lower()

        formula = desc[idx+1:].strip()
        if (len(formula) == 0):
            return VDataFormulaNone(name)
        
        code = formula
        idx = formula.find(':')
        if (idx == 0):
            raise Exception('FORMAT_VDATA_KEY_DESC_INVALID: ' + desc)
        elif (idx > 0):
            code = formula[0:idx]

        if ('8' == code):
            if (idx < 0):
                return self.buildArrayFormula(name, '', insensitiveCase)
            elif (idx > 0):
                formula = formula[idx+1:].strip()
                if (len(formula) == 0):
                    return self.buildArrayFormula(name, '', insensitiveCase)
            
            if (formula[0] != '[' or formula[-1] != ']'):
                raise Exception('FORMAT_VDATA_KEY_DESC_INVALID_ARRAY: ' + desc)

            formula = formula[1:-1].strip()
            if (len(formula) == 0):
                raise Exception('FORMAT_VDATA_KEY_DESC_INVALID_ARRAY: ' + desc)

            return self.buildArrayFormula(name, formula, insensitiveCase)

        if ('9' == code):
            if (idx < 0):
                raise Exception('FORMAT_VDATA_KEY_DESC_INVALID_STRUCT: ' + desc)
            elif (idx > 0):
                formula = formula[idx+1:].strip()
                if (len(formula) == 0):
                    raise Exception('FORMAT_VDATA_KEY_DESC_INVALID_STRUCT: ' + desc)
            
            if (formula[0] != '{' or formula[-1] != '}'):
                raise Exception('FORMAT_VDATA_KEY_DESC_INVALID_STRUCT: ' + desc)
            
            formula = formula[1:-1].strip()
            if (len(formula) == 0):
                raise Exception('FORMAT_VDATA_KEY_DESC_INVALID_STRUCT: ' + desc)
            
            return self.buildStructFormula(name, formula, insensitiveCase)

        return self.buildSimpleFormula(name, formula)

    def buildArrayFormula(self, name, formula, insensitiveCase=False):
        descs = formula.split(',')
        formulas = []
        namedArray = False
        names = {""}

        # first item allow to be either named or not named, but after first item must follow same format
        for i in range(len(descs)):
            desc = descs[i].strip()

            if len(desc) == 0:
                if (namedArray and i != 0):
                    raise Exception ('FORMAT_VDATA_KEY_DESC_ARRAY_MIXED_NAMES_NOT_ALLOWED: ' + name)
                formulas.append(VDataFormulaNone(name))
                continue

            idx = desc.find('|')
            if idx < 0:
                if (desc.find(':') < 0 and '0' != desc): # named with no formula
                    if (not namedArray) and i != 0:
                        raise Exception ('FORMAT_VDATA_KEY_DESC_ARRAY_MIXED_NAMES_NOT_ALLOWED: ' + name)
                    if insensitiveCase:
                        desc = desc.lower()
                    if (desc in names):
                        raise Exception ('FORMAT_VDATA_KEY_DESC_ARRAY_DUPLICATE_NAMES_NOT_ALLOWED: ' + name + ' - ' + desc)
                    formulas.append(VDataFormulaNone(desc))
                    names.add(desc)
                    namedArray = True
                else:   # formula only and not named
                    if namedArray and i != 0:
                        raise Exception ('FORMAT_VDATA_KEY_DESC_ARRAY_MIXED_NAMES_NOT_ALLOWED: ' + name + ' - ' + desc)
                    formulas.append(self.buildSimpleFormula(name, desc))
                continue

            if idx == 0: # special case, formula only and not named, but with |
                if (namedArray and i != 0):
                    raise Exception ('FORMAT_VDATA_KEY_DESC_ARRAY_MIXED_NAMES_NOT_ALLOWED: ' + name)
                desc = desc[1:].strip()
                if (len(desc) == 0):
                    formulas.append(VDataFormulaNone(name))
                else:
                    formulas.append(self.buildSimpleFormula(name, desc))
                continue
            
            # named with formulas
            itemname = desc[0:idx].strip()
            if (len(itemname) == 0):
                raise Exception('FORMAT_VDATA_KEY_DESC_INVALID_ARRAY_ITEM: ' + name)
            if (insensitiveCase):
                itemname = itemname.lower()
            itemformula = desc[idx+1:].strip()
            
            if (itemname in names):
                raise Exception ('FORMAT_VDATA_KEY_DESC_ARRAY_DUPLICATE_NAMES_NOT_ALLOWED: ' + name + ' - ' + itemname)
            else:
                names.add(itemname)
                namedArray = True

            if (len(itemformula) == 0):
                formulas.append(VDataFormulaNone(itemname))
            else:
                formulas.append(self.buildSimpleFormula(itemname, itemformula))
        
        if namedArray:
            return VDataFormulaNamedArray(name, formulas)
        else:
            return VDataFormulaArray(name, formulas)
    
    def buildStructFormula(self, name, formula, insensitiveCase):
        descs = formula.split(',')
        formulas =[]
        
        for i in range(len(descs)):
            desc = descs[i].strip()
            if ('|' not in desc):
                itemname = desc.strip().lower() if insensitiveCase else desc.strip()
                formulas.append(VDataFormulaNone(itemname))
                continue
            
            idx = desc.find('|')
            if (idx == 0):
                raise Exception('FORMAT_VDATA_KEY_DESC_INVALID_STRUCT_ITEM: ' + name)
            
            itemname = desc[0:idx].strip()
            if (len(itemname) == 0):
                raise Exception('FORMAT_VDATA_KEY_DESC_INVALID_STRUCT_ITEM: ' + name)
            if (insensitiveCase):
                itemname = itemname.lower()
            itemformula = desc[idx+1:].strip()
            
            if (len(itemformula) == 0):
                formulas.append(VDataFormulaNone(itemname))
            else:
                formulas.append(self.buildSimpleFormula(itemname, itemformula))
        
        return VDataFormulaStruct(name, formulas)
    
    def buildSimpleFormula(self, fname, formula):
        fitems = formula.split(":")
        formulaType = fitems[0].strip()
        flen = len(fitems)

        if '0' == formulaType:
            if flen == 1:
                return VDataFormulaNone(fname)
            raise Exception('FORMAT_VDATA_KEY_DESC_INVALID: ' + fname + "|" + formula)
       
        if '1' == formulaType:
            if flen == 3:
                factor = float(fitems[1].strip())
                offset = float(fitems[2].strip())
                if factor.is_integer() and int(factor) == 1 and offset.is_integer() and int(offset) == 0:
                    return VDataFormulaNone(fname)
                else:
                    return VDataFormulaLinear(fname, factor, offset)
            raise Exception('FORMAT_VDATA_KEY_DESC_INVALID: ' + fname + "|" + formula)
        
        if '2' == formulaType:
            if flen == 7:
                p0 = float(fitems[1].strip())
                p1 = float(fitems[2].strip())
                p2 = float(fitems[3].strip())
                p3 = float(fitems[4].strip())
                p4 = float(fitems[5].strip())
                p5 = float(fitems[6].strip())
                return VDataFormulaPolynomial(fname, p0, p1, p2, p3, p4, p5)
            raise Exception('FORMAT_VDATA_KEY_DESC_INVALID: ' + fname + "|" + formula)

        if '3' == formulaType:
            if flen == 8:
                p0 = float(fitems[1].strip())
                p1 = float(fitems[2].strip())
                p2 = float(fitems[3].strip())
                p3 = float(fitems[4].strip())
                p4 = float(fitems[5].strip())
                p5 = float(fitems[6].strip())
                p6 = float(fitems[7].strip())
                return VDataFormulaExponential(fname, p0, p1, p2, p3, p4, p5, p6)
            raise Exception('FORMAT_VDATA_KEY_DESC_INVALID: ' + fname + "|" + formula)

        if '4' == formulaType:
            if flen == 8:
                p0 = float(fitems[1].strip())
                p1 = float(fitems[2].strip())
                p2 = float(fitems[3].strip())
                p3 = float(fitems[4].strip())
                p4 = float(fitems[5].strip())
                p5 = float(fitems[6].strip())
                p6 = float(fitems[7].strip())
                return VDataFormulaLogarithmic(fname, p0, p1, p2, p3, p4, p5, p6)
            raise Exception('FORMAT_VDATA_KEY_DESC_INVALID: ' + fname + "|" + formula)

        if '5' == formulaType:
            if flen == 7:
                p0 = float(fitems[1].strip())
                p1 = float(fitems[2].strip())
                p2 = float(fitems[3].strip())
                p3 = float(fitems[4].strip())
                p4 = float(fitems[5].strip())
                p5 = float(fitems[6].strip())
                return VDataFormulaRational(fname, p0, p1, p2, p3, p4, p5)
            raise Exception('FORMAT_VDATA_KEY_DESC_INVALID: ' + fname + "|" + formula)

        if '6' == formulaType:
            if flen >= 3:
                plist = []
                for i in range(1, flen):
                    plist.append(float(fitems[i].strip()))
                return VDataFormulaDecode(fname, plist)
            raise Exception('FORMAT_VDATA_KEY_DESC_INVALID: ' + fname + "|" + formula)

        if '7' == formulaType:
            if flen >= 5:
                plist = []
                for i in range(1, flen):
                    plist.append(float(fitems[i].strip()))
                return VDataFormulaInterpolate(fname, plist)
            raise Exception('FORMAT_VDATA_KEY_DESC_INVALID: ' + fname + "|" + formula)
        if '11' == formulaType:
            return VDataFormulaBlob(fname)
        raise Exception('FORMAT_VDATA_KEY_DESC_INVALID: ' + fname + "|" + formula)

class VDataSeriesMeta:
    def __init__(self, formula, storageid, seriesid, pageSize=0x10000, storageIdLength=5):
        self._name = formula._name
        self._formula = formula
        self._seriesid = seriesid
        if (pageSize != 0x8000):
            self._pageIndex = storageid >> 48  # 48-64-bit
            self._pageOffset = (storageid >> 32) & 65535 # 32-48 bit
            self._dataLength = ((storageid >> 16) & 32767) + 32768 if ((storageid >> 31) & 1) != 0 else ((storageid >> 16) & 32767)
            self._itemCount =  (storageid & 32767) + 32768 if ((storageid >> 15) & 0x01) != 0 else storageid & 32767
        elif (storageIdLength == 5):
            self._pageIndex = (storageid >> 35 ) & 0x1F  # 35-40  5bits
            self._pageOffset = (storageid >> 20 ) & 0x7FFF # 20-34 15bits
            self._dataLength = ((storageid >> 9) & 0x07FF)  #9-19 , 11 bits
            self._itemCount =  (storageid &  0x1ff)  #0 - 8, 9  bits
        else: 
            self._pageIndex = (storageid >> 40 ) & 0xFF  # 40-48  5bits
            self._pageOffset = (storageid >> 25 ) & 0x7FFF # 25-39 15bits
            self._dataLength = ((storageid >> 10) & 0x07FFF)  #10-19 , 24 bits
            self._itemCount =  (storageid &  0x3ff)  #0 - 9, 10  bits           
            
        
    def getSeriesId(self):
        return self._seriesid

    def __repr__(self): 
        return '{name:' + str(self._name) \
             + ', items:' + str(self._itemCount) \
             + ', length:' + str(self._dataLength) \
             + '}'

class BitTracker:
    def __init__(self):
        self.numBits = 0

    def getNumBits(self):
        return self.numBits

    def setNumBits(self, bits):
        self.numBits = bits

    def getByteIndex(self):
        return self.numBits >> 3

    def getNumBytes(self):
        return (self.numBits >> 3) + 1 if (self.numBits & 7) != 0 else self.numBits >> 3
      
    def incrementBit(self):
        self.numBits = self.numBits + 1
    
    def incrementBits(self, bits):
        self.numBits = self.numBits + bits

class TimestampTracker:
    def __init__(self):
        self.timestamp = 0
        self.timestampDelta = 0

    def getTimestamp(self):
        return self.timestamp

    def setTimestamp(self, _value):
        self.timestamp = _value

    def getTimestampDelta(self):
        return self.timestampDelta

    def setTimestampDelta(self, _value):
        self.timestampDelta = _value

class TimeMicrosTracker (TimestampTracker):
    def __init__(self):
        TimestampTracker.__init__(self)
        self.micros = 0

    def getMicros(self):
        return self.micros

    def setMicros(self, _value):
        self.micros = _value

class StringTracker:
    def __init__(self, formula):
        self.signalValue = ""

    def getSignalValue(self):
        return self.signalValue

    def setSignalValue(self, value):
        self.signalValue = value

    def getPhysicalValue(self):
        return self.signalValue

class Float32Tracker:
    def __init__(self, formula):
        self.formula = formula
        self.bitValue = 0
        self.leadingZeros = 0
        self.trailingZeros = 0

    def getBitValue(self):
        return self.bitValue

    def setBitValue(self, value):
        self.bitValue = value
    
    def getSignalValue(self):
        return self.intBitsToFloat(self.bitValue)
    
    def getPhysicalValue(self):
        return self.formula.apply(self.intBitsToFloat(self.bitValue))

    def getLeadingZeros(self):
        return self.leadingZeros

    def setLeadingZeros(self, value):
        self.leadingZeros = value

    def getTrailingZeros(self):
        return self.trailingZeros

    def setTrailingZeros(self, _value):
        self.trailingZeros = _value

    def intBitsToFloat(self, bits):
        return _struct.unpack('f', _struct.pack('L', bits))[0]

class Float64Tracker:
    def __init__(self, formula):
        self.formula = formula
        self.bitValue = 0
        self.signalValue = 0
        self.leadingZeros = 0
        self.trailingZeros = 0
        self.updatedBits = False

    def getBitValue(self):
        return self.bitValue

    def setBitValue(self, value):
        self.bitValue = value
        self.updatedBits = True
    
    def getSignalValue(self):
        if (self.updatedBits):
            self.signalValue = self.longBitsToDouble(self.bitValue)
            self.updatedBits = False
        return self.signalValue
    
    def setSignalValue(self, value):
        self.signalValue = value
        self.updatedBits = False
    
    def getPhysicalValue(self):
        return self.formula.apply(self.getSignalValue())

    def getLeadingZeros(self):
        return self.leadingZeros

    def setLeadingZeros(self, value):
        self.leadingZeros = value

    def getTrailingZeros(self):
        return self.trailingZeros

    def setTrailingZeros(self, _value):
        self.trailingZeros = _value
    
    def longBitsToDouble(self, bits):
        return _struct.unpack('d', _struct.pack('Q', bits))[0]


class UInt64Tracker:
    def __init__(self, formula):
        self.formula = formula
        self.bitValue = 0
        self.signalValue = 0
        self.leadingZeros = 0
        self.trailingZeros = 0
        self.updatedBits = False

    def getBitValue(self):
        return self.bitValue

    def setBitValue(self, value):
        self.bitValue = value
        self.updatedBits = True
    
    def getSignalValue(self):
        if (self.updatedBits):
            self.signalValue = self.longBitsToDouble(self.bitValue)
            self.updatedBits = False
        return self.signalValue
    
    def setSignalValue(self, value):
        self.signalValue = value
        self.updatedBits = False
    
    def getPhysicalValue(self):
        return self.formula.apply(self.getSignalValue())

    def getLeadingZeros(self):
        return self.leadingZeros

    def setLeadingZeros(self, value):
        self.leadingZeros = value

    def getTrailingZeros(self):
        return self.trailingZeros

    def setTrailingZeros(self, _value):
        self.trailingZeros = _value
    
    def longBitsToDouble(self, bits):
        return bits #_struct.unpack('d', _struct.pack('Q', bits))[0]

class Int64Tracker:
    def __init__(self, formula):
        self.formula = formula
        self.bitValue = 0
        self.signalValue = 0
        self.leadingZeros = 0
        self.trailingZeros = 0
        self.updatedBits = False

    def getBitValue(self):
        return self.bitValue

    def setBitValue(self, value):
        self.bitValue = value
        self.updatedBits = True
    
    def getSignalValue(self):
        if (self.updatedBits):
            self.signalValue = self.longBitsToDouble(self.bitValue)
            self.updatedBits = False
        return self.signalValue
    
    def setSignalValue(self, value):
        self.signalValue = value
        self.updatedBits = False
    
    def getPhysicalValue(self):
        return self.formula.apply(self.getSignalValue())

    def getLeadingZeros(self):
        return self.leadingZeros

    def setLeadingZeros(self, value):
        self.leadingZeros = value

    def getTrailingZeros(self):
        return self.trailingZeros

    def setTrailingZeros(self, _value):
        self.trailingZeros = _value
    
    def longBitsToDouble(self, bits):
        return _struct.unpack('q', _struct.pack('Q', bits))[0]

class IntTracker:
    def __init__(self, formula):
        self.formula = formula
        self.signalValue = 0
        self.deltaSigBits = 0
        self.leadingZeros = 0
        self.trailingZeros = 0

    def getSignalValue(self):
        return self.signalValue

    def setSignalValue(self, value):
        self.signalValue = value
    
    def getPhysicalValue(self):
        return self.formula.apply(self.signalValue)

    def getDeltaSignificantBits(self):
        return self.deltaSigBits

    def setDeltaSignificantBits(self, numBits):
        self.deltaSigBits = numBits

    def getLeadingZeros(self):
        return self.leadingZeros

    def setLeadingZeros(self, value):
        self.leadingZeros = value

    def getTrailingZeros(self):
        return self.trailingZeros

    def setTrailingZeros(self, _value):
        self.trailingZeros = _value

class VDataConstants:
    PAGE_LENGTH = 65536
    BIT_MASKS = [-128, 64, 32, 16, 8, 4, 2, 1]
    BIT_POWER2 = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608, 16777216, 33554432, 67108864, 134217728, 268435456, 536870912, 1073741824, 2147483648]
    
    TIMESTAMP_INIT_DELTA = 60
    TIMESTAMP_VALUE_ENCODING = [7, 9, 12, 32]
    
    TIMESTAMP_FIRST_VALUE_BITS = 41 # Works until 2038.
    MICROSECOND_BITS = 10           # Microsecond bits
    XOR_LEADING_ZERO_LENGTH_BITS = 5
    XOR_BLOCK_SIZE_LENGTH_BITS = 6
    XOR_BLOCK_SIZE_ADJUSTMENTS = 1
    ENCODE_LEADING_BITS = [0, 8, 12, 16, 18, 20, 22, 24]

    POLL_QUEUE_MIN_SIZE = 10

class DType:
    Float64 = 0 
    String = 1
    Boolean = 2
    Int8 = 3
    UInt8 = 4
    Int16 = 5
    Int32 = 6
    Int64 = 7
    Array = 8
    Struct = 9
    Float32 = 10
    Blob = 11
    UInt64 = 12

class DEncoder:
    NONE = 0
    XOR = 1
    GZIP = 2
    DELTA = 3
    CHIMP = 4
    ERASURE = 5
    PLAIN = 6

class DExpand:
    NONE = 0
    FLAT = 1
    FULL = 2

class VDataUtils:
    def getColumnExpandMode(mode):
        if (mode is not None):
            m = mode
            if isinstance(m, str):
                m = m.lower().strip()
                if (m == "none"):
                    return DExpand.NONE
                elif (m == "flat"):
                    return DExpand.FLAT
                elif (m == "full"):
                    return DExpand.FULL
            try:
                m = int(float(m))
            except ValueError:
                return DExpand.FLAT
            if (m == DExpand.NONE):
                return DExpand.NONE
            elif (m == DExpand.FULL):
                return DExpand.FULL
        return DExpand.FLAT
    
    def getSignalQueueMode(mode):
        if (mode):
            m = str(mode).lower().strip()
            if (m == "first"):
                return "first"
            if (m == "all"):
                return "all"
        return "last"
    
    def isQualifiedExpandName(mode):
        return VDataUtils.getColumnExpandMode(mode) == DExpand.FULL

    def isAllSignalQueueMode(mode):
        return "all" == VDataUtils.getSignalQueueMode(mode)
    
    def insertion_order_set_list(names):
        if (names is None or len(names) == 0):
            return []
        
        st = set(names)
        ns = []
        for nm in names:
            if (nm in st):
                ns.append(nm)
                st.remove(nm)
        return ns
    
class VDataDecodeUtils:
    def sortAddDecoder(decoders, decoder):
        size = len(decoders)
        if (size == 0):
            logger.info("Add decoder " + str(decoder))
            decoders.append(decoder)
            return
        
        decoderStartTime = decoder._meta.storageStartTime()
        for i in reversed(range(size)):
            dc = decoders[i]
            st = dc._meta.storageStartTime()
            if (st <= decoderStartTime):
                logger.info("Add decoder " + str(decoder))
                decoders.insert(i + 1, decoder)
                return

        logger.info("Add decoder " + str(decoder))
        decoders.insert(0, decoder)

    def readValueFromBitOne(page, bitTracker):
        bitpos = bitTracker.getNumBits()
        #value = 0 if ((page[bitpos >> 3] & VDataConstants.BIT_MASKS[bitpos & 7]) == 0) else 1
        value =  (((page[bitpos >> 3]) >> (7-(bitpos & 7))))   & 1
        #if (value != value2 ):
        #    value2 =value
        bitTracker.setNumBits(bitpos + 1)

        return value

    def readValueFromBitString(page, bitsToRead, bitTracker):
        
        bitpos = bitTracker.getNumBits()

        value = 0
        for i in range(bitsToRead):
            value = value * 2 if ((page[bitpos >> 3] & VDataConstants.BIT_MASKS[bitpos & 7]) == 0) else value * 2 + 1
            bitpos += 1
        
        bitTracker.setNumBits(bitpos)
        
        return value

class VDataFloat32NoneDecode:
    def __init__(self, _page, _formula, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker
        self.fltTracker = Float32Tracker(_formula)

    def first(self):
        self.next()

    def next(self):
        value = VDataDecodeUtils.readValueFromBitString(self.page, 32, self.bitTracker)
        self.fltTracker.setBitValue(value)

    def get(self):
        return self.fltTracker.getPhysicalValue()

    def raw(self):
        return self.fltTracker.getSignalValue()

    def bits(self):
        return self.fltTracker.getBitValue()

class VDataFloat64NoneDecode:
    def __init__(self, _page, _formula, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker
        self.fltTracker = Float64Tracker(_formula)

    def first(self):
        self.next()

    def next(self):
        value = VDataDecodeUtils.readValueFromBitString(self.page, 64, self.bitTracker)
        self.fltTracker.setBitValue(value)

    def get(self):
        return self.fltTracker.getPhysicalValue()

    def raw(self):
        return self.fltTracker.getSignalValue()

    def bits(self):
        return self.fltTracker.getBitValue()

class VDataFloat64ChimpDecode:
    def __init__(self, _page, _formula, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker
        self.fltTracker = Float64Tracker(_formula)

    def first(self):
        self.next()

    def next(self):
        xorValue = 0
        trailingZeros = VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) 
        data_change = VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) 
        if (trailingZeros == 0): #trailing zeros > 6
            if (data_change == 0): #no data change
                return
            else:
                leadingZeros = VDataConstants.ENCODE_LEADING_BITS[VDataDecodeUtils.readValueFromBitString(self.page, 3, self.bitTracker)]
                significantBits = VDataConstants.readValueFromBitString(self.page, 6, self.bitTracker)
                if(significantBits == 0):
                    significantBits = 64
                trailingZeros = 64 - significantBits - leadingZeros
                xorValue = VDataDecodeUtils.readValueFromBitString(self.page, significantBits, self.bitTracker)
                xorValue = xorValue << trailingZeros

                self.fltTracker.setLeadingZeros(leadingZeros)
        else:
            if (data_change == 0): #use previous block info
                leadingZeros = self.fltTracker.getLeadingZeros()
                xorValue = VDataDecodeUtils.readValueFromBitString(self.page, 64 - leadingZeros, self.bitTracker)
            else:
                leadingZeros = VDataConstants.ENCODE_LEADING_BITS[VDataDecodeUtils.readValueFromBitString(self.page, 3, self.bitTracker)]
                xorValue = VDataDecodeUtils.readValueFromBitString(self.page, 64 - leadingZeros, self.bitTracker)

                self.fltTracker.setLeadingZeros(leadingZeros)

        value = xorValue ^ self.fltTracker.getBitValue()
        self.fltTracker.setBitValue(value)

    def get(self):
        return self.fltTracker.getPhysicalValue()

    def raw(self):
        return self.fltTracker.getSignalValue()

    def bits(self):
        return self.fltTracker.getBitValue()

class VDataFloat64ErasureDecode:
    POWER_P10 = [1, 10, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10]
    POWER_N10 = [1, 1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9, 1e-10]
    POWER_P20 = [1, 10, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10, 1e11, 1e12, 1e13, 1e14, 1e15, 1e16, 1e17, 1e18, 1e19, 1e20]
    POWER_N20 = [1, 1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9, 1e-10, 1e-11, 1e-12, 1e-13, 1e-14, 1e-15, 1e-16, 1e-17, 1e-18, 1e-19, 1e-20]

    def __init__(self, _page, _formula, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker
        self.fltTracker = Float64Tracker(_formula)
        self.beta = sys.maxsize

    def first(self):
        self.bitTracker.incrementBits(2)

        trailingZeros = VDataDecodeUtils.readValueFromBitString(self.page, 7, self.bitTracker)
        if (trailingZeros < 64):
            value = ((VDataDecodeUtils.readValueFromBitString(self.page, 63 - trailingZeros, self.bitTracker) << 1) + 1) << trailingZeros
            self.fltTracker.setBitValue(value)

    def next(self):
        decodePower = VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker)
        if (decodePower == 0):
            self.decodeToPower()
        elif (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0):
            self.decodeBase()
        else:
            self.beta = VDataDecodeUtils.readValueFromBitString(self.page, 4, self.bitTracker)
            self.decodeToPower()

    def decodeBase(self):
        bits = VDataDecodeUtils.readValueFromBitString(self.page, 2, self.bitTracker)
        if (bits == 1):
            return; #no data change

        xorValue = 0
        
        if (bits == 0):
            leadingZeros = self.fltTracker.getLeadingZeros()
            trailingZeros = self.fltTracker.getTrailingZeros()
            centerBits = 64 - leadingZeros - trailingZeros;
            xorValue = VDataDecodeUtils.readValueFromBitString(self.page, centerBits, self.bitTracker) << trailingZeros
        elif (bits == 2):
            leadCenter = VDataDecodeUtils.readValueFromBitString(self.page, 7, self.bitTracker)
            leadingZeros = VDataConstants.ENCODE_LEADING_BITS[(leadCenter % 0x100000000) >> 4] # implementation for [leadCenter >>> 4]
            centerBits = 0xF & leadCenter
            if(centerBits == 0):
                centerBits = 16

            trailingZeros = 64 - leadingZeros - centerBits
            xorValue = ((VDataDecodeUtils.readValueFromBitString(self.page, centerBits - 1, self.bitTracker) << 1) + 1) << trailingZeros
            
            self.fltTracker.setLeadingZeros(leadingZeros)
            self.fltTracker.setTrailingZeros(trailingZeros)
        elif (bits == 3):
            leadCenter = VDataDecodeUtils.readValueFromBitString(self.page, 9, self.bitTracker)
            leadingZeros = VDataConstants.ENCODE_LEADING_BITS[(leadCenter % 0x100000000) >> 6] # implementation for [leadCenter >>> 6]
            centerBits = 0x3F & leadCenter
            if(centerBits == 0):
                centerBits = 64
            
            trailingZeros = 64 - leadingZeros - centerBits
            xorValue = ((VDataDecodeUtils.readValueFromBitString(self.page, centerBits - 1, self.bitTracker) << 1) + 1) << trailingZeros
                
            self.fltTracker.setLeadingZeros(leadingZeros)
            self.fltTracker.setTrailingZeros(trailingZeros)

        value = xorValue ^ self.fltTracker.getBitValue()
        self.fltTracker.setBitValue(value)
    
    def decodeToPower(self):
        self.decodeBase()
        
        base = self.fltTracker.getSignalValue()
        power = self.getTensPower(abs(base))
        value = 0
        
        if (self.beta == 0):
            value = self.toTenthPower(-power - 1)
            if (base < 0):
                value = -value
        else:
            scale = self.beta - power - 1
            value = round(base, scale)
        
        self.fltTracker.setSignalValue(value)

    def getTensPower(self, v):
        if (v >= 1):
            for i in range(1, len(VDataFloat64ErasureDecode.POWER_P10)):
                if (v < VDataFloat64ErasureDecode.POWER_P10[i]):
                    return i - 1
        else:
            for i in range(1, len(VDataFloat64ErasureDecode.POWER_N10)):
                if (v >= VDataFloat64ErasureDecode.POWER_N10[i]):
                    return -i
        
        return floor(log10(v))

    def toTenthPower(self, i):
        if (i >= len(VDataFloat64ErasureDecode.POWER_N20)):
            return pow(10, i)
        else:
            return VDataFloat64ErasureDecode.POWER_N20[i]

    def toTenPower(self, i):
        if (i >= len(VDataFloat64ErasureDecode.POWER_P20)):
            return round(pow(10, i))
        else:
            return VDataFloat64ErasureDecode.POWER_P20[i]

    def get(self):
        return self.fltTracker.getPhysicalValue()

    def raw(self):
        return self.fltTracker.getSignalValue()

    def bits(self):
        return self.fltTracker.getBitValue()

class VDataUint64XorDecode:
    def __init__(self, _page, _formula, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker
        self.intTracker = UInt64Tracker(_formula)

    def first(self):
        self.next()

    def next(self):
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0): #no data change
            return
        
        xorValue = 0
        
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) != 0): #use previous block info
            previousLeadingZeros = self.intTracker.getLeadingZeros()
            previousTrailingZeros = self.intTracker.getTrailingZeros()
            xorValue = VDataDecodeUtils.readValueFromBitString(self.page, 64 - previousLeadingZeros - previousTrailingZeros, self.bitTracker)
            xorValue = xorValue << previousTrailingZeros
        else:
            leadingZeros = VDataDecodeUtils.readValueFromBitString(self.page, VDataConstants.XOR_LEADING_ZERO_LENGTH_BITS, self.bitTracker)
            blockSize = VDataDecodeUtils.readValueFromBitString(self.page, VDataConstants.XOR_BLOCK_SIZE_LENGTH_BITS, self.bitTracker) + VDataConstants.XOR_BLOCK_SIZE_ADJUSTMENTS

            trailingZeros = 64 - blockSize - leadingZeros
            xorValue = VDataDecodeUtils.readValueFromBitString(self.page, blockSize, self.bitTracker)
            xorValue = xorValue << trailingZeros
            
            self.intTracker.setLeadingZeros(leadingZeros)
            self.intTracker.setTrailingZeros(trailingZeros)

        value = xorValue ^ self.intTracker.getBitValue()
        self.intTracker.setBitValue(value)

    def get(self):
        return self.intTracker.getPhysicalValue()

    def raw(self):
        return self.intTracker.getSignalValue()

    def bits(self):
        return self.intTracker.getBitValue()

class VDataInt64XorDecode(VDataUint64XorDecode):
    def __init__(self, _page, _formula, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker
        self.intTracker = Int64Tracker(_formula)

class VDataFloat64XorDecode:
    def __init__(self, _page, _formula, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker
        self.fltTracker = Float64Tracker(_formula)

    def first(self):
        self.next()

    def next(self):
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0): #no data change
            return
        
        xorValue = 0
        
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) != 0): #use previous block info
            previousLeadingZeros = self.fltTracker.getLeadingZeros()
            previousTrailingZeros = self.fltTracker.getTrailingZeros()
            xorValue = VDataDecodeUtils.readValueFromBitString(self.page, 64 - previousLeadingZeros - previousTrailingZeros, self.bitTracker)
            xorValue = xorValue << previousTrailingZeros
        else:
            leadingZeros = VDataDecodeUtils.readValueFromBitString(self.page, VDataConstants.XOR_LEADING_ZERO_LENGTH_BITS, self.bitTracker)
            blockSize = VDataDecodeUtils.readValueFromBitString(self.page, VDataConstants.XOR_BLOCK_SIZE_LENGTH_BITS, self.bitTracker) + VDataConstants.XOR_BLOCK_SIZE_ADJUSTMENTS

            trailingZeros = 64 - blockSize - leadingZeros
            xorValue = VDataDecodeUtils.readValueFromBitString(self.page, blockSize, self.bitTracker)
            xorValue = xorValue << trailingZeros
            
            self.fltTracker.setLeadingZeros(leadingZeros)
            self.fltTracker.setTrailingZeros(trailingZeros)

        value = xorValue ^ self.fltTracker.getBitValue()
        self.fltTracker.setBitValue(value)

    def get(self):
        return self.fltTracker.getPhysicalValue()

    def raw(self):
        return self.fltTracker.getSignalValue()

    def bits(self):
        return self.fltTracker.getBitValue()

class VDataUInt8PlainDecode:
    def __init__(self, _page, _formula, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker
        self.intTracker = IntTracker(_formula)

    def first(self):
        self.next()

    def next(self):
        value = int(VDataDecodeUtils.readValueFromBitString(self.page, 8, self.bitTracker))
        self.intTracker.setSignalValue(value)

    def get(self):
        return self.intTracker.getPhysicalValue()

    def raw(self):
        return self.intTracker.getSignalValue()

    def bits(self):
        return self.raw()

class VDataUInt8NoneDecode:
    def __init__(self, _page, _formula, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker
        self.intTracker = IntTracker(_formula)

    def first(self):
        self.next()

    def next(self):
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0): #no data change
            return        
        value = int(VDataDecodeUtils.readValueFromBitString(self.page, 8, self.bitTracker))
        self.intTracker.setSignalValue(value)

    def get(self):
        return self.intTracker.getPhysicalValue()

    def raw(self):
        return self.intTracker.getSignalValue()

    def bits(self):
        return self.raw()

class VDataUInt8XorDecode:
    def __init__(self, _page, _formula, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker
        self.intTracker = IntTracker(_formula)

    def first(self):
        self.next()

    def next(self):
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0): #no data change
            return
        
        diff = 0
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0):
            diff = int(VDataDecodeUtils.readValueFromBitString(self.page, 3, self.bitTracker)) + 1 
        else: 
            diff = int(VDataDecodeUtils.readValueFromBitString(self.page, 8, self.bitTracker))
        value = diff ^ self.intTracker.getSignalValue()
        self.intTracker.setSignalValue(value)

    def get(self):
        return self.intTracker.getPhysicalValue()

    def raw(self):
        return self.intTracker.getSignalValue()

    def bits(self):
        return self.raw()

class VDataInt8NoneDecode:
    def __init__(self, _page, _formula, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker
        self.intTracker = IntTracker(_formula)

    def first(self):
        self.next()

    def next(self):
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0): #no data change
            return
        
        value = int(VDataDecodeUtils.readValueFromBitString(self.page, 8, self.bitTracker))
        if (value > 0x7F):
            value = value - 0x0100 
        self.intTracker.setSignalValue(value)

    def get(self):
        return self.intTracker.getPhysicalValue()

    def raw(self):
        return self.intTracker.getSignalValue()

    def bits(self):
        return self.raw()

class VDataInt32DeltaDecode:
    def __init__(self, _page, _formula, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker
        self.intTracker = IntTracker(_formula)

    def first(self):
        self.next()

    def next(self):
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0): #no data change
            return
        
        usesb = VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) != 0
        sigbits = 0
        if (usesb): #use previous block info
            sigbits = self.intTracker.getDeltaSignificantBits()
        else:
            sigbits = VDataDecodeUtils.readValueFromBitString(self.page, VDataConstants.XOR_LEADING_ZERO_LENGTH_BITS, self.bitTracker)
            self.intTracker.setDeltaSignificantBits(sigbits)
        
        neg = VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) != 0
        deltaValue = VDataDecodeUtils.readValueFromBitString(self.page, sigbits, self.bitTracker)
        value = 0

        if (neg):
            value = self.intTracker.getSignalValue() - deltaValue
            if (-value > 0x80000000):
                value = value + 0x0100000000
        else:
            value = self.intTracker.getSignalValue() + deltaValue
            if (value > 0x7FFFFFFF):
                value = value - 0x0100000000
        
        self.intTracker.setSignalValue(value)

    def get(self):
        return self.intTracker.getPhysicalValue()

    def raw(self):
        return self.intTracker.getSignalValue()

    def bits(self):
        return self.raw()

class VDataBlobNoneDecode:
    def __init__(self, _page, _formula, _bitTracker, _blob_data):
        self.page = _page
        self.bitTracker = _bitTracker
        self.intTracker = IntTracker(_formula)
        self.offsetDecode = VDataInt32DeltaDecode(_page, VDataFormulaNone(_formula._name) , _bitTracker)
        self._data = _blob_data
        self._formula = _formula

    def first(self):
        self.next()

    def next(self):
        self.offsetDecode.next()

    def get(self):
        offset = self.offsetDecode.get()
        return self._formula.apply( self.getBlobData( offset))

    def raw(self):
        offset = self.offsetDecode.get()
        return self.getBlobData( offset)

    def bits(self):
        return self.raw()
    
    def getBlobData(self, offset):
        (header_length,_, data_length)=_struct.unpack('<hhi', self._data[offset:offset+8] )
        return self._data[offset+header_length:offset+header_length+data_length]

class VDataBooleanNoneDecode:
    def __init__(self, _page, _formula, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker
        self.intTracker = IntTracker(_formula)

    def first(self):
        self.next()

    def next(self):
        self.intTracker.setSignalValue(VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker))

    def get(self):
        return self.intTracker.getPhysicalValue()

    def raw(self):
        return self.intTracker.getSignalValue()

    def bits(self):
        return self.raw()

class VDataStringNoneDecode:
    def __init__(self, _page, _formula, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker
        self.stringTracker = StringTracker(_formula)

    def first(self):
        self.next()

    def next(self):
        bb = []
        
        while(1):
            b = VDataDecodeUtils.readValueFromBitString(self.page, 8, self.bitTracker)
            if (b == 0):
                break
            
            bb.append(b)
        
        if (len(bb) == 0):
            self.stringTracker.setSignalValue("")
        else:
            self.stringTracker.setSignalValue(bytearray(bb).decode("utf-8"))

    def get(self):
        return self.stringTracker.getPhysicalValue()

    def raw(self):
        return self.stringTracker.getSignalValue()

    def bits(self):
        return self.raw()

class VDataNumberArrayDecode:
    def __init__(self, _page, _dtype, _encoder, _length, _matchLength, _formula, _bitTracker):
        self.page = _page
        self.decoders = []
        self.bitTracker = _bitTracker

        if (isinstance(_formula, VDataFormulaArray)):
            formulas = _formula._formulas
            flen = len(formulas)
            if (flen == 0):
                fn = VDataFormulaNone(_formula._name)
                for i in range(_length):
                    self.decoders.append(self.buildDecoder(_page, _dtype, _encoder, fn, _bitTracker))
            else:
                if (_length != flen and _matchLength):
                    raise Exception('FORMAT_VDATA_ARRAY_LENGTH_MISMATCH: length=' + str(_length) + ', formula is ' + _formula._name)
                s = _length if _length < flen else flen
                for i in range(s):
                    self.decoders.append(self.buildDecoder(_page, _dtype, _encoder, formulas[i], _bitTracker))
                for i in range(flen, _length):
                    self.decoders.append(self.buildDecoder(_page, _dtype, _encoder, formulas[flen - 1], _bitTracker))
        else:
            for i in range(_length):
                self.decoders.append(self.buildDecoder(_page, _dtype, _encoder, _formula, _bitTracker))

    def buildDecoder(self, _page, _dtype, _encoder, _formula, _bitTracker):
        if (_dtype == DType.UInt8):
            if (_encoder == DEncoder.XOR):
                return VDataUInt8XorDecode(_page, _formula, _bitTracker)
            elif (_encoder == DEncoder.PLAIN) :
                return VDataUInt8PlainDecode(_page, _formula, _bitTracker)
            else:
                return VDataUInt8NoneDecode(_page, _formula, _bitTracker)
        if (_dtype == DType.Float64 ):
            if (_encoder == DEncoder.XOR):
                return VDataFloat64XorDecode(_page, _formula, _bitTracker)
            elif (_encoder == DEncoder.CHIMP):
                return VDataFloat64ChimpDecode(_page, _formula, _bitTracker)
            elif (_encoder == DEncoder.ERASURE):
                return VDataFloat64ErasureDecode(_page, _formula, _bitTracker)
            elif (_encoder == DEncoder.NONE):
                return VDataFloat64NoneDecode(_page, _formula, _bitTracker)
            else:
                return VDataFloat64XorDecode(_page, _formula, _bitTracker)
        if (_dtype == DType.Int8):
            return VDataInt8NoneDecode(_page, _formula, _bitTracker)
        if (_dtype == DType.Int16 or _dtype == DType.Int32):
            return VDataInt32DeltaDecode(_page, _formula, _bitTracker)
        if (_dtype == DType.Boolean):
            return VDataBooleanNoneDecode(_page, _formula, _bitTracker)
        if (_dtype == DType.Float32):
            return VDataFloat32NoneDecode(_page, _formula, _bitTracker)
        if (_dtype == DType.UInt64):
            return VDataUint64XorDecode(_page, _formula, _bitTracker)
        if (_dtype == DType.Int64):
            return VDataInt64XorDecode(_page, _formula, _bitTracker)        
        raise Exception ('FORMAT_VDATA_DATA_TYPE_NOT_SUPPORTED: ' + str(_dtype))

    def first(self):
        self.next()

    def next(self):
        for i in range(len(self.decoders)):
            self.decoders[i].next()

    def get(self):
        vals = []
        for i in range(len(self.decoders)):
            vals.append(self.decoders[i].get())
        return vals
    
    def raw(self):
        vals = []
        for i in range(len(self.decoders)):
            vals.append(self.decoders[i].raw())
        return vals

    def bits(self):
        vals = []
        for i in range(len(self.decoders)):
            vals.append(self.decoders[i].bits())
        return vals
    
class VDataStringArrayDecode:
    def __init__(self, _page, _dtype, _encoder, _length, _matchLength, _formula, _bitTracker):
        self.page = _page
        self.decoders = []
        self.bitTracker = _bitTracker

        if (isinstance(_formula, VDataFormulaArray)):
            formulas = _formula._formulas
            flen = len(formulas)
            if (flen == 0):
                fn = VDataFormulaNone(_formula._name)
                for i in range(_length):
                    self.decoders.append(self.buildDecoder(_page, _dtype, _encoder, fn, _bitTracker))
            else:
                if (_length != flen and _matchLength):
                    raise Exception('FORMAT_VDATA_ARRAY_LENGTH_MISMATCH: length=' + str(_length) + ', formula is ' + _formula.name())
                s = _length if _length < flen else flen
                for i in range(s):
                    self.decoders.append(self.buildDecoder(_page, _dtype, _encoder, formulas[i], _bitTracker))
                for i in range(flen, _length):
                    self.decoders.append(self.buildDecoder(_page, _dtype, _encoder, formulas[flen - 1], _bitTracker))
        else:
            for i in range(_length):
                self.decoders.append(self.buildDecoder(_page, _dtype, _encoder, _formula, _bitTracker))

    def buildDecoder(self, _page, _dtype, _encoder, _formula, _bitTracker):
        return VDataStringNoneDecode(_page, _formula, _bitTracker)

    def first(self):
        self.next()

    def next(self):
        for i in range(len(self.decoders)):
            self.decoders[i].next()

    def get(self):
        vals = []
        for i in range(len(self.decoders)):
            vals.append(self.decoders[i].get())
        return vals
    
    def raw(self):
        vals = []
        for i in range(len(self.decoders)):
            vals.append(self.decoders[i].raw())
        return vals

    def bits(self):
        vals = []
        for i in range(len(self.decoders)):
            vals.append(self.decoders[i].bits())
        return vals
    
class VDataNullDecode:
    def __init__(self, _page, _bitTracker):
        self.page = _page
        self.bitTracker = _bitTracker

    def isNull(self):
        return VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 1

    def isNotNull(self):
        return VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0

class VDataStructDecode:
    def __init__(self, _page, _dtypes, _encoders, _length, _formula, _bitTracker):
        self.page = _page
        self.decoders = []
        self.notnulls = []
        self.bitTracker = _bitTracker
        self.nullDecoder = VDataNullDecode(_page, _bitTracker)

        if (not isinstance(_formula, VDataFormulaStruct)):
            raise Exception('FORMAT_VDATA_STRUCT_FORMULA_MISMATCH: ' + _formula._name)
        
        formulas = _formula._formulas
        flen = len(formulas)
        if (_length != flen):
            raise Exception('FORMAT_VDATA_STRUCT_LENGTH_MISMATCH: ' + _formula._name)

        self.subLength = flen
        for i in range(flen):
            self.decoders.append(self.buildDecoder(_page, _dtypes[i], _encoders[i], formulas[i], _bitTracker))
            self.notnulls.append(True)

    def buildDecoder(self, _page, _dtype, _encoder, _formula, _bitTracker):
        if (_dtype == DType.UInt8):
            if (_encoder == DEncoder.XOR):
                return VDataUInt8XorDecode(_page, _formula, _bitTracker)
            else:
                return VDataUInt8NoneDecode(_page, _formula, _bitTracker)
        if (_dtype == DType.Float64 ):
            if (_encoder == DEncoder.XOR):
                return VDataFloat64XorDecode(_page, _formula, _bitTracker)
            elif (_encoder == DEncoder.CHIMP):
                return VDataFloat64ChimpDecode(_page, _formula, _bitTracker)
            elif (_encoder == DEncoder.ERASURE):
                return VDataFloat64ErasureDecode(_page, _formula, _bitTracker)
            elif (_encoder == DEncoder.NONE):
                return VDataFloat64NoneDecode(_page, _formula, _bitTracker)
            else:
                return VDataFloat64XorDecode(_page, _formula, _bitTracker)
        if (_dtype == DType.Int8):
            return VDataInt8NoneDecode(_page, _formula, _bitTracker)
        if (_dtype == DType.Int16 or _dtype == DType.Int32):
            return VDataInt32DeltaDecode(_page, _formula, _bitTracker)
        if (_dtype == DType.Boolean):
            return VDataBooleanNoneDecode(_page, _formula, _bitTracker)
        if (_dtype == DType.String):
            return VDataStringNoneDecode(_page, _formula, _bitTracker)
        if (_dtype == DType.Float32):
            return VDataFloat32NoneDecode(_page, _formula, _bitTracker)
        raise Exception ('FORMAT_VDATA_DATA_TYPE_NOT_SUPPORTED: ' + str(_dtype))

    def first(self):
        self.next()

    def next(self):
        for i in range(len(self.decoders)):
            self.notnulls[i] = self.nullDecoder.isNotNull()
            if (self.notnulls[i]):
                self.decoders[i].next()

    def get(self):
        vals = []
        for i in range(len(self.decoders)):
            vals.append(self.decoders[i].get() if self.notnulls[i] else None)
        return vals
    
    def raw(self):
        vals = []
        for i in range(len(self.decoders)):
            vals.append(self.decoders[i].raw() if self.notnulls[i] else None)
        return vals
    
    def bits(self):
        vals = []
        for i in range(len(self.decoders)):
            vals.append(self.decoders[i].bits() if self.notnulls[i] else None)
        return vals
       
class VDataTimeDeltaDecode:
    def __init__(self, _page, _bitTracker, timestampLength):
        self.page = _page
        self.bitTracker = _bitTracker
        self.timeTracker = TimestampTracker()
        self.timestampLength = timestampLength

    def first(self):
        #VDataConstants.TIMESTAMP_FIRST_VALUE_BITS
        self.timeTracker.setTimestamp(VDataDecodeUtils.readValueFromBitString(self.page, self.timestampLength, self.bitTracker))
        self.timeTracker.setTimestampDelta(VDataConstants.TIMESTAMP_INIT_DELTA)

    def next(self):
        previousTimestampDelta = self.timeTracker.getTimestampDelta()
        ttype = self.findTheFirstZeroBit4()
        if (ttype > 0):
            bitsForValue = VDataConstants.TIMESTAMP_VALUE_ENCODING[ttype - 1]
            decodedValue = VDataDecodeUtils.readValueFromBitString(self.page, bitsForValue, self.bitTracker) - VDataConstants.BIT_POWER2[bitsForValue - 1] # [0,255] becomes [-128,127]
            # [-128,127] becomes [-128,128] without the zero in the middle
            previousTimestampDelta += decodedValue + 1 if decodedValue >= 0 else decodedValue

        self.timeTracker.setTimestamp(self.timeTracker.getTimestamp() + previousTimestampDelta)
        self.timeTracker.setTimestampDelta(previousTimestampDelta)

    def findTheFirstZeroBit4(self):
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0):
            return 0
        
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0):
            return 1
        
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0):
            return 2
        
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0):
            return 3
        
        return 4

    def get(self):
        return self.timeTracker.getTimestamp()

    def raw(self):
        return self.timeTracker.getTimestamp()
    
    def timestamp(self):
        return self.timeTracker.getTimestamp()

class VDataTimeMicrosDecode:
    def __init__(self, _page, _bitTracker, timestampLength):
        self.page = _page
        self.bitTracker = _bitTracker
        self.timeTracker = TimeMicrosTracker()
        self._timestampLength = timestampLength

    def first(self):
        self.timeTracker.setTimestamp(VDataDecodeUtils.readValueFromBitString(self.page, self._timestampLength, self.bitTracker))
        self.timeTracker.setTimestampDelta(VDataConstants.TIMESTAMP_INIT_DELTA)

        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) != 0):
            self.timeTracker.setMicros(VDataDecodeUtils.readValueFromBitString(self.page, VDataConstants.MICROSECOND_BITS, self.bitTracker))
        else:
            self.timeTracker.setMicros(0)

    def next(self):
        previousTimestampDelta = self.timeTracker.getTimestampDelta()
        ttype = self.findTheFirstZeroBit4()
        if (ttype > 0):
            bitsForValue = VDataConstants.TIMESTAMP_VALUE_ENCODING[ttype - 1]
            decodedValue = VDataDecodeUtils.readValueFromBitString(self.page, bitsForValue, self.bitTracker) - VDataConstants.BIT_POWER2[bitsForValue - 1] # [0,255] becomes [-128,127]
            # [-128,127] becomes [-128,128] without the zero in the middle
            previousTimestampDelta += decodedValue + 1 if decodedValue >= 0 else decodedValue

        self.timeTracker.setTimestamp(self.timeTracker.getTimestamp() + previousTimestampDelta)
        self.timeTracker.setTimestampDelta(previousTimestampDelta)

        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) != 0):
            self.timeTracker.setMicros(VDataDecodeUtils.readValueFromBitString(self.page, VDataConstants.MICROSECOND_BITS, self.bitTracker))
        else:
            self.timeTracker.setMicros(0)
        
    def findTheFirstZeroBit4(self):
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0):
            return 0
        
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0):
            return 1
        
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0):
            return 2
        
        if (VDataDecodeUtils.readValueFromBitOne(self.page, self.bitTracker) == 0):
            return 3
        
        return 4

    def get(self):
        time = self.timeTracker.getTimestamp()
        micros = self.timeTracker.getMicros()

        if (micros == 0):
            return time

        return time + micros / 1000.0

    def raw(self):
        time = self.timeTracker.getTimestamp()
        micros = self.timeTracker.getMicros()

        if (micros == 0):
            return time

        return time + micros / 1000.0

    def timestamp(self):
        return self.timeTracker.getTimestamp()

class VDataObjectValueArray:
    def __init__(self, time, colsize):
        self._time = time
        self._colsize = colsize
    
    def getTime(self):
        return self._time

class VDataDenseArray (VDataObjectValueArray):
    def __init__(self, time, colsize):
        super().__init__(time, colsize)
        self._values = [None] * colsize
        self._values[0] = self._time

    def isEmptyAt(self, position):
        return self._values[position] is None

    def add(self, position, value):
        self._values[position] = value

    def toObjects(self):
        return self._values

class VDataDenseArrayFirstMode (VDataDenseArray):
    def __init__(self, time, colsize):
        super().__init__(time, colsize)

    def add(self, position, value):
        if self._values[position] is None:
            self._values[position] = value

class VDataSparseArray (VDataObjectValueArray):
    def __init__(self, time, colsize):
        super().__init__(time, colsize)
        self._posits = []
        self._values = []
        self._posits.append(0)
        self._values.append(time)

    def isEmptyAt(self, position):
        for i in range (1, len(self._posits)):
            if (self._posits[i] == position):
                return self._values[i] is None
        return True

    def add(self, position, value):
        self._posits.append(position)
        self._values.append(value)

    def toObjects(self):
        vals = [None] * self._colsize
        for i in range(len(self._posits)):
            vals[self._posits[i]] = self._values[i]
        
        return vals

class VDataSparseArrayFirstMode (VDataSparseArray):
    def __init__(self, time, colsize):
        super().__init__(time, colsize)

    def toObjects(self):
        vals = [None] * self._colsize
        for i in range(len(self._posits)):
            pos = self._posits[i]
            if (vals[pos] is None):
                vals[pos] = self._values[i]
        
        return vals

class VDataSparseArrayAllMode (VDataSparseArray):
    def __init__(self, time, colsize):
        super().__init__(time, colsize)

    def isEmptyAt(self, position):
        low = 1
        high = len(self._posits) - 1
        mid = floor((low + high) / 2)
        pos = 0
        
        while (low < high):
            pos = self._posits[mid]
            if (position == pos):
                return False
            elif (position < pos):
                high = mid - 1
            else:
                low = mid + 1
            
            mid = floor((low + high) / 2)
        
        if (high == low and position == self._posits[low]):
            return False
        
        return True
    
    def add(self, position, value):
        if (position == 0):
            return;  # index 0 is time

        low = 1
        high = len(self._posits) - 1
        mid = floor((low + high) / 2)
        pos = 0
        
        while (low < high):
            pos = self._posits[mid]
            if (position == pos):
                self._values[mid] = value
                return
            elif (position < pos):
                high = mid - 1
            else:
                low = mid + 1

            mid = floor((low + high) / 2)
        
        if (low == high):
            pos = self._posits[low]
            if (position == pos):
                self._values[low] = value
            elif (position < pos):
                self._posits.insert(low, position)
                self._values.insert(low, value)
            else:
                self._posits.insert(low + 1, position)
                self._values.insert(low + 1, value)
        else:
            self._posits.insert(low, position)
            self._values.insert(low, value)

class VDataSeriesDecodeBuilder(object):
    def build(_data):
        _version = _data.getFormatVersion()
        if (_version < 26):
            return VDataSeriesDecodeNumber(_data, 0, DType.Float64, DEncoder.XOR)

        _bt = _data.getPage()
        btreader = VDataByteReader(_bt)
        firstbyte = btreader.read(1)[0]
        _type = (firstbyte >> 4) & 0x0F
        _offset = 8

        if (_type == DType.Array):
            high_len = btreader.read(1)[0]
            low_len = btreader.read(1)[0]
            _length = ((high_len & 0xFF) << 8) | (low_len & 0xFF)
            
            sub = btreader.read(1)[0]
            _subtype = (sub >> 4) & 0x0F
            _encoder = sub & 0x0F
            _offset = 32
            
            element_exist_array = []

            if (_version > 27 ):
                #for nullable element array, load null element map.
                _byte_length = 2 if _length<=16 else (_length+7)//8 
                _offset = 32 + _byte_length *8 
                _bitmap = btreader.read(_offset)
                for i in range(_length):
                    element_exist_array.append(True)
                    byte_index =  i // 8
                    bit_index = 7- i % 8

                    element_exist_array.append( (((_bitmap[byte_index]>> bit_index) & 0x01) == 1 ))

            else :
                for i in range(_length):
                    element_exist_array.append( True)
                _offset = 32
            

            if (isinstance(_data.getFormula(), VDataFormulaNamedArray)):
                return VDataSeriesDecodeNamedArray(_data, _offset, _subtype, _encoder, _length)
            elif (_subtype == DType.String):
                return VDataSeriesDecodeStringArray(_data, _offset, _subtype, _encoder, _length, False)
            else:
                return VDataSeriesDecodeNumberArray(_data, _offset, _subtype, _encoder, _length, False)

        if (_type == DType.Struct):
            high_len = btreader.read(1)[0]
            low_len = btreader.read(1)[0]
            _length = ((high_len & 0xFF) << 8) | (low_len & 0xFF)
            _subtypes = []
            _encoders = []
            _offset = 8 + 16 + 8 * _length

            for i in range(_length):
                sub = btreader.read(1)[0]
                _subtypes.append((sub >> 4) & 0x0F)
                _encoders.append(sub & 0x0F)

            return VDataSeriesDecodeStruct(_data, _offset, _subtypes, _encoders, _length)
        
        _encoder = firstbyte & 0x0F
        if (_type == DType.String):
            return VDataSeriesDecodeString(_data, _offset, _type, _encoder)
        
        if (_type == DType.Blob):
            return VDataSeriesDecodeBlob(_data, _offset, _type, _encoder)
                
        return VDataSeriesDecodeNumber(_data, _offset, _type, _encoder)

    def builds(_datas):
        decoders = []
        for _data in _datas:
            decoders.append(VDataSeriesDecodeBuilder.build(_data))
        return decoders

class VDataSeriesBucket(object):
    def __init__(self):
        self.name = None
        self.formatVersion = 0
        self.bucketCycle = 0
        self.dtype = DType.Float64
        self.sstime = 0 # storage start time
        self.setime = 0 # storage end time
        self.qstime = 0 # query start time
        self.qetime = 0 # query end time

        self.page = None
        self.formula = None
        self.itemCount = 0
        self.firstTime = None
        self.blobData = None
        self.timestampLength =41 

    def getFormatVersion(self):
        return self.formatVersion
    
    def setFormatVersion(self, version):
        self.formatVersion = version

    def getName(self):
        return self.name

    def getFormula(self):
        return self.formula

    def getItemCount(self):
        return self.itemCount
    
    def setMeta(self, meta):
        self.name = meta._name
        self.formula = meta._formula
        self.itemCount = meta._itemCount

    def getPage(self):
        return self.page

    def setPage(self, page):
        self.page = page

    def getFirstTime(self):
        return self.firstTime

    def setFirstTime(self, time):
        self.firstTime = time

    def getBucketCycle(self):
        return self.bucketCycle

    def setBucketCycle(self, cycle):
        self.bucketCycle = cycle

    def getBucketStartTime(self):
        return self.sstime

    def setBucketStartTime(self, time):
        self.sstime = time if time > 0 else 0

    def getBucketEndTime(self):
        return self.setime

    def setBucketEndTime(self, time):
        self.setime = time if time > 0 else 0
    
    def getQueryStartTime(self):
        return self.qstime

    def setQueryStartTime(self, time):
        self.qstime = time

    def getQueryEndTime(self):
        return self.qetime

    def setQueryEndTime(self, qetime):
        self.qetime = qetime
    
    def getType(self):
        return self.dtype
    
    def setBlobData(self, blob):
        self.blobData = blob
        
    def getBlobData(self):
        return self.blobData
    
    def setSeriesTimestampLength(self, length):
        self.timestampLength = length
        
    def getSeriesTimestampLength(self):
        return self.timestampLength

class VDataSeriesDecode(object):
    def __init__(self, data, offset, dtype):
        self.name = data.getName()
        self.formula = data.getFormula()
        self.itemCount = data.getItemCount()
        self.page = data.getPage()
        self.dtype = dtype
        self.bucketCycle = data.getBucketCycle()
        self.sstime = data.getBucketStartTime()
        self.setime = data.getBucketEndTime()
        self.qstime = data.getQueryStartTime()
        self.qetime = data.getQueryEndTime()

        self.bitTracker = BitTracker()
        self.bitTracker.setNumBits(offset)
        self.timeDecode = VDataTimeDeltaDecode(self.page, self.bitTracker, data.getSeriesTimestampLength())

        self.readCount = 0
        self.emptied = 1

    def getName(self):
        return self.name

    def getFormula(self):
        return self.formula
    
    def getItemCount(self):
        return self.itemCount

    def getQueryStartTime(self):
        return self.qstime

    def getQueryEndTime(self):
        return self.qetime
    
    def time(self):
        return self.timeDecode.get()

    def timestamp(self):
        return self.timeDecode.timestamp()
    
    def getType(self):
        return self.dtype
    
    def isEmpty(self):
        return self.emptied
    
    def getSubNames(self):
        return None


class VDataSeriesDecodeNumber(VDataSeriesDecode):
    def __init__(self, data, offset, dtype, encoder):
        super().__init__(data, offset, dtype)

        if (dtype == DType.UInt8):
            if (encoder == DEncoder.XOR):
                self.valueDecode = VDataUInt8XorDecode(self.page, self.formula, self.bitTracker)
            elif (encoder == DEncoder.PLAIN):
                self.valueDecode = VDataUInt8PlainDecode(self.page, self.formula, self.bitTracker)
            else:
                self.valueDecode = VDataUInt8NoneDecode(self.page, self.formula, self.bitTracker)
        elif (dtype == DType.Float64 ):
            if (encoder == DEncoder.XOR):
                self.valueDecode = VDataFloat64XorDecode(self.page, self.formula, self.bitTracker)
            elif (encoder == DEncoder.CHIMP):
                self.valueDecode = VDataFloat64ChimpDecode(self.page, self.formula, self.bitTracker)
            elif (encoder == DEncoder.ERASURE):
                self.valueDecode = VDataFloat64ErasureDecode(self.page, self.formula, self.bitTracker)
            elif (encoder == DEncoder.NONE):
                self.valueDecode = VDataFloat64NoneDecode(self.page, self.formula, self.bitTracker)
            else:
                self.valueDecode = VDataFloat64XorDecode(self.page, self.formula, self.bitTracker)
        elif (dtype == DType.Int8):
            self.valueDecode = VDataInt8NoneDecode(self.page, self.formula, self.bitTracker)
        elif (dtype == DType.Int16 or dtype == DType.Int32):
            self.valueDecode = VDataInt32DeltaDecode(self.page, self.formula, self.bitTracker)
        elif (dtype == DType.Boolean):
            self.valueDecode = VDataBooleanNoneDecode(self.page, self.formula, self.bitTracker)
        elif (dtype == DType.Float32):
            self.valueDecode = VDataFloat32NoneDecode(self.page, self.formula, self.bitTracker)
        elif (dtype == DType.UInt64):
            self.valueDecode = VDataUint64XorDecode(self.page, self.formula, self.bitTracker)
        elif (dtype == DType.Int64):
            self.valueDecode = VDataInt64XorDecode(self.page, self.formula, self.bitTracker)        
        else:
            raise Exception ('FORMAT_VDATA_DATA_TYPE_NOT_SUPPORTED: ' + str(dtype))

        if (self.readCount < self.itemCount):
            self.timeDecode.first()
            self.valueDecode.first()
            self.emptied = 0
            self.readCount += 1
    
    def value(self):
        return self.valueDecode.get()

    def rawBits(self):
        return self.valueDecode.bits()
    
    def pair(self):
        return VDataSeriesPair(self.time(), self.value())

    def pollAndAdd(self):
        if (self.readCount < self.itemCount):
            self.timeDecode.next()
            self.valueDecode.next()
            self.readCount += 1
        else:
            self.emptied = 1

class VDataSeriesDecodeNumberArray(VDataSeriesDecode):
    def __init__(self, data, offset, dtype, encoder, length , matchLength=False):
        super().__init__(data, offset, DType.Array)
        if (encoder == DEncoder.PLAIN):
            self.timeDecode = VDataTimeDeltaDecode(self.page, self.bitTracker, data.getSeriesTimestampLength())
            self.isPlainEncode = True
        else:
            self.timeDecode = VDataTimeMicrosDecode(self.page, self.bitTracker, data.getSeriesTimestampLength())
            self.isPlainEncode = False
        self.valueDecode = VDataNumberArrayDecode(self.page, dtype, encoder, length, matchLength, self.formula, self.bitTracker)

        if (self.readCount < self.itemCount):
            self.timeDecode.first()
            bitPos = self.bitTracker.getNumBits()
            if(self.isPlainEncode & (bitPos %8 !=0)):
                self.bitTracker.setNumBits((bitPos//8 +1) *8 )
            self.valueDecode.first()
            self.emptied = 0
            self.readCount += 1
    
    def value(self):
        return self.valueDecode.get()

    def rawBits(self):
        return self.valueDecode.bits()
    
    def pair(self):
        return VDataSeriesPair(self.time(), self.value())

    def pollAndAdd(self):
        if (self.readCount < self.itemCount):
            self.timeDecode.next()
            bitPos = self.bitTracker.getNumBits()
            if(self.isPlainEncode & (bitPos %8 !=0)):
                self.bitTracker.setNumBits((bitPos//8 +1) *8 )
            self.valueDecode.next()
            self.readCount += 1
        else:
            self.emptied = 1


class VDataSeriesDecodeStringArray(VDataSeriesDecode):
    def __init__(self, data, offset, dtype, encoder, length,  matchLength=False):
        super().__init__(data, offset, DType.Array)

        self.timeDecode = VDataTimeMicrosDecode(self.page, self.bitTracker, data.getSeriesTimestampLength())
        self.valueDecode = VDataStringArrayDecode(self.page, dtype, encoder, length, matchLength, self.formula, self.bitTracker)

        if (self.readCount < self.itemCount):
            self.timeDecode.first()
            self.valueDecode.first()
            self.emptied = 0
            self.readCount += 1
    
    def value(self):
        return self.valueDecode.get()

    def rawBits(self):
        return self.valueDecode.bits()

    def pair(self):
        return VDataSeriesPair(self.time(), self.value())

    def pollAndAdd(self):
        if (self.readCount < self.itemCount):
            self.timeDecode.next()
            self.valueDecode.next()
            self.readCount += 1
        else:
            self.emptied = 1

class VDataSeriesDecodeNamedArray(VDataSeriesDecode):
    def __init__(self, data, offset, dtype, encoder, length):
        super().__init__(data, offset, DType.Array)

        self.timeDecode = VDataTimeMicrosDecode(self.page, self.bitTracker, data.getSeriesTimestampLength())
        if (dtype != DType.String):
            self.valueDecode = VDataNumberArrayDecode(self.page, dtype, encoder, length, False, self.formula, self.bitTracker)
        else:
            self.valueDecode = VDataStringArrayDecode(self.page, dtype, encoder, length, True, self.formula, self.bitTracker)

        formulas = self.formula._formulas
        self.subNames =[]
        for i in range(len(formulas)):
            self.subNames.append(formulas[i]._name)

        if (self.readCount < self.itemCount):
            self.timeDecode.first()
            self.valueDecode.first()
            self.emptied = 0
            self.readCount += 1
    
    def value(self):
        return self.valueDecode.get()

    def rawBits(self):
        return self.valueDecode.bits()

    def pair(self):
        return VDataSeriesPair(self.time(), self.value())

    def pollAndAdd(self):
        if (self.readCount < self.itemCount):
            self.timeDecode.next()
            self.valueDecode.next()
            self.readCount += 1
        else:
            self.emptied = 1

    def getSubNames(self):
        return self.subNames

class VDataSeriesDecodeString (VDataSeriesDecode):
    def __init__(self, data, offset, dtype, encoder):
        super().__init__(data, offset, dtype)
        
        self.valueDecode = VDataStringNoneDecode(self.page, self.formula, self.bitTracker)

        if (self.readCount < self.itemCount):
            self.timeDecode.first()
            self.valueDecode.first()
            self.emptied = 0
            self.readCount += 1

    def value(self):
        return self.valueDecode.get()

    def rawBits(self):
        return self.valueDecode.bits()

    def pair(self):
        return VDataSeriesPair(self.time(), self.value())

    def pollAndAdd(self):
        if (self.readCount < self.itemCount):
            self.timeDecode.next()
            self.valueDecode.next()
            self.readCount += 1
        else:
            self.emptied = 1

class VDataSeriesDecodeStruct(VDataSeriesDecode):
    def __init__(self, data, offset, dtypes, encoders, length):
        super().__init__(data, offset, DType.Struct)

        self.timeDecode = VDataTimeMicrosDecode(self.page, self.bitTracker, data.getSeriesTimestampLength())
        self.valueDecode = VDataStructDecode(self.page, dtypes, encoders, length, self.formula, self.bitTracker)
        self.dtypes = dtypes

        formulas = self.formula._formulas
        self.subNames =[]
        for i in range(len(formulas)):
            self.subNames.append(formulas[i]._name)

        if (self.readCount < self.itemCount):
            self.timeDecode.first()
            self.valueDecode.first()
            self.emptied = 0
            self.readCount += 1
    
    def value(self):
        return self.valueDecode.get()

    def rawBits(self):
        return self.valueDecode.bits()

    def pair(self):
        return VDataSeriesPair(self.time(), self.value())

    def pollAndAdd(self):
        if (self.readCount < self.itemCount):
            self.timeDecode.next()
            self.valueDecode.next()
            self.readCount += 1
        else:
            self.emptied = 1
    
    def getSubNames(self):
        return self.subNames

class VDataSeriesDecodeBlob(VDataSeriesDecode):
    def __init__(self, data, offset, dtype, encoder):
        super().__init__(data, offset, dtype)
        self.valueDecode = VDataBlobNoneDecode(self.page, self.formula, self.bitTracker, data.getBlobData())


        if (self.readCount < self.itemCount):
            self.timeDecode.first()
            self.valueDecode.first()
            self.emptied = 0
            self.readCount += 1
    
    def value(self):
        return self.valueDecode.get()

    def rawBits(self):
        return self.valueDecode.bits()
    
    def pair(self):
        return VDataSeriesPair(self.time(), self.value())

    def pollAndAdd(self):
        if (self.readCount < self.itemCount):
            self.timeDecode.next()
            self.valueDecode.next()
            self.readCount += 1
        else:
            self.emptied = 1

class VDataSeries:
    def __init__(self, name):
        self._name = name
        self._buckets = []
        self._itemCounts = {}

    def __repr__(self): 
        return 'name={0}, buckets={1}'.format(str(self._name),len(self._buckets) )

    def name(self):
        return self._name
    
    def buckets(self):
        return self._buckets

    def numBuckets(self):
        return len(self._buckets)
    
    def getMaxBucketItemCount(self):
        maxcnt = 0;
        for cnt in self._itemCounts.values():
            if (cnt > maxcnt):
                maxcnt = cnt
        return maxcnt

    def updateBucketItemCounts(self, bucketNum, itemCount):
        cnt = self._itemCounts.get(bucketNum, None)
        if (cnt is None):
            self._itemCounts[bucketNum] = itemCount
        else:
            self._itemCounts[bucketNum] = cnt + itemCount

    def addBucket(self, bucket):
        if len(self._buckets) == 0:
            self._buckets.append(bucket)
            return
        
        bucketStartTime = bucket.getQueryStartTime() if bucket.getQueryStartTime() > bucket.getBucketStartTime() else bucket.getBucketStartTime()
        if bucketStartTime <= 0:
            self._buckets.append(bucket) #no start time for bucket, just add to end of list
            return
        
        for i in reversed(range(len(self._buckets))):
            b = self._buckets[i]
            s = b.getQueryStartTime() if b.getQueryStartTime() > b.getBucketStartTime() else b.getBucketStartTime()
            if (s <= 0):
                continue

            if (bucketStartTime > s):
                self._buckets.insert(i + 1, bucket)
                return
            
            if (bucketStartTime == s):
                if (bucket.getBucketCycle() < b.getBucketCycle()):   #higher frequency (smaller interval) or raw bucket, replace current bucket, else duplicate or lower freq bucket
                    index = i
                    while (index - 1 >= 0):
                        probe = self._buckets[index - 1]
                        if (probe.getBucketStartTime() == s and probe.getBucketCycle() >= b.getBucketCycle()):
                            index = index - 1
                        else:
                            break

                    begin = i
                    while (begin > index):
                        self._buckets.pop(begin)
                        begin = begin - 1
                    self._buckets[index] = b
                elif (bucket.getBucketCycle() == b.getBucketCycle()): #sort the pages by time in case it is unordered
                    index = i
                    while (index >= 0):
                        probe = self._buckets[index]
                        if (probe.getBucketStartTime() == s and VDataSeriesUtils.getFirstDataTime(probe) > VDataSeriesUtils.getFirstDataTime(bucket)):
                            index = index - 1
                        else:
                            break
                    self._buckets.insert(index + 1, bucket)
                return

        self._buckets.insert(0, bucket) #all the way to the beginning

    def getType(self):
        return self._buckets[0].getType()

    def formula(self):
        return self._buckets[0].formula
    
class VDataSeriesPoll:
    def __init__(self, series, qsize=0, qmode=None):
        self._name = series._name
        self._decoders = VDataSeriesDecodeBuilder.builds(series._buckets)
        self._qsize = qsize if qsize > 0 else VDataConstants.POLL_QUEUE_MIN_SIZE
        self._qstime = 0
        self._qetime = 0

        maxItemCount = series.getMaxBucketItemCount()
        if (self._qsize < maxItemCount + VDataConstants.POLL_QUEUE_MIN_SIZE):
            self._qsize = maxItemCount + VDataConstants.POLL_QUEUE_MIN_SIZE

        self._decoder = None
        self._decoderIndex = 0
        self._pair = None

        self._queue = None
        if (len(self._decoders) > 0):
            self._queue = self.buildQueue(qmode)
            self._decoder = self._decoders[0]
            self._qstime = self.getQueryStartTime(self._decoder)
            self._qetime = self.getQueryEndTime(self._decoder)

            pair = self._decoder.pair()
            _time = pair.time()
            rcount = 0

            if (_time > self._qstime and _time < self._qetime):
                self._queue.put(pair)
                rcount = rcount + 1
            
            while (rcount < self._qsize):
                pair = self.poll()
                if (pair is None):
                    break
                
                _time = pair.time()
                if (_time > self._qstime and _time < self._qetime and self._queue.put(pair)):
                    rcount = rcount + 1
            if (self._queue.empty()):
                self._queue = None
            else:
                self._pair = self._queue.poll()

    def __repr__(self): 
        return 'name={0}, buckets={1}'.format(str(self._name),len(self._buckets)  )

    def buildQueue(self, qmode):
        if (qmode is None):
            return VDataPairQueueLastIn()

        m = str(qmode).lower().strip()
        if (m == 'all'):
            return VDataPairQueueAllIn()
        elif (m == 'first'):
            return VDataPairQueueFirstIn()
        else:
            return VDataPairQueueLastIn()
     
    def name(self):
        return self._name

    def time(self):
        return self._pair.time()

    def value(self):
        return self._pair.value()
    
    def isEmpty(self):
        return self._queue is None

    def poll(self):
        if (self._decoder is not None):
            self._decoder.pollAndAdd()
            if (self._decoder.isEmpty()):
                self._decoderIndex += 1
                if (len(self._decoders) > self._decoderIndex):
                    self._decoder = self._decoders[self._decoderIndex]
                    self._qstime = self.getQueryStartTime(self._decoder)
                    self._qetime = self.getQueryEndTime(self._decoder)
                    return self._decoder.pair()
                else:
                    self._decoder = None
                    return None
            else:
                return self._decoder.pair()
        
        return None
    
    def pollAndAdd(self):
        while (self._decoder is not None):
            self._decoder.pollAndAdd()

            if (self._decoder.isEmpty()):
                self._decoderIndex += 1
                if (len(self._decoders) > self._decoderIndex):
                    self._decoder = self._decoders[self._decoderIndex]
                    self._qstime = self.getQueryStartTime(self._decoder)
                    self._qetime = self.getQueryEndTime(self._decoder)

                    pair = self._decoder.pair()
                    _time = pair.time()
                    if (_time > self._qstime and _time < self._qetime and self._queue.put(pair)):
                        break
                else:
                    self._decoder = None
            else:
                pair = self._decoder.pair()
                _time = pair.time()
                if (_time > self._qstime and _time < self._qetime and self._queue.put(pair)):
                    break
        
        if (self._queue.empty()):
            self._queue = None
        else:
            self._pair = self._queue.poll()

    def getQueryStartTime(self, _decoder):
        return _decoder.getQueryStartTime() - 1 if _decoder.getQueryStartTime() > 0 else 0 # query start time is inclusive
    
    def getQueryEndTime(self, _decoder):
        return _decoder.getQueryEndTime() + 1 if _decoder.getQueryEndTime() > 0 else sys.maxsize # query end time is inclusive

    def formula(self):
        return self._decoders[0].formula

    def getSubNames(self):
        return self._decoders[0].getSubNames()

class VDataPollQueue:
    def __init__(self):
        self.times = []
        self.data = {}

    def empty(self):
        return False if self.times else True

    def put(self, item):
        t = item.time()
        if (t not in self.data):
            heapq.heappush(self.times, t)
            self.data[t] = deque()
        self.data[t].append(item)

    def poll(self):
        t = self.times[0]
        d = self.data[t]
        v = d.popleft()

        if not d:
            heapq.heappop(self.times)
            self.data.pop(t)

        return v

    def pop(self):
        return self.data.pop(heapq.heappop(self.times))

    def peek(self):
        t = self.times[0]
        d = self.data[t]
        
        return d[0]

class VDataPairQueueAllIn:
    def __init__(self):
        self.times = []
        self.data = {}

    def empty(self):
        return False if self.times else True

    def put(self, item):
        t = item.time()
        if (t not in self.data):
            heapq.heappush(self.times, t)
            self.data[t] = item
            return True
        
        current = self.data[t]
        if (isinstance(current, deque)):
            current.append(item)
        else:
            self.data[t] = deque([current, item])

        return True

    def poll(self):
        current = self.data[self.times[0]]
        if (isinstance(current, deque)):
            if (len(current) == 1):
                return self.data.pop(heapq.heappop(self.times)).popleft()
            else:
                return self.data[self.times[0]].popleft()
        
        return self.data.pop(heapq.heappop(self.times))

    def peek(self):
        current = self.data[self.times[0]]
        if (isinstance(current, deque)):
            return current[0]
        else:
            return current

class VDataPairQueueFirstIn:
    def __init__(self):
        self.times = []
        self.data = {}

    def empty(self):
        return False if self.times else True

    def put(self, item):
        t = item.time()
        if (t not in self.data):
            heapq.heappush(self.times, t)
            self.data[t] = item
            return True
        return False #true if a new pair has been added, false if not added or merely replaced an existing series pair with identical time.

    def poll(self):
        return self.data.pop(heapq.heappop(self.times))

    def peek(self):
        return self.data[self.times[0]]

class VDataPairQueueLastIn:
    def __init__(self):
        self.times = []
        self.data = {}

    def empty(self):
        return False if self.times else True

    def put(self, item):
        t = item.time()
        r = False  #true if a new pair has been added, false if not added or merely replaced an existing series pair with identical time.
        if (t not in self.data):
            heapq.heappush(self.times, t)
            r = True
        self.data[t] = item
        return r

    def poll(self):
        return self.data.pop(heapq.heappop(self.times))

    def peek(self):
        return self.data[self.times[0]]

class VDataSignalFilter:
    '''
    A class for filter conditions on the signal names.
    '''
    def __init__(self):
        '''
        The constructor of the filter.
        '''
        self._signals = set()
        self._prefixes = set()
        self._signal_names = []
    
    def getSignals(self):
        '''
        Get the set of signal names to filter on.

        Returns:
            set(str)
        '''
        return self._signals
    
    def setSignals(self, signals):
        '''
        Set the set of signal names to filter on.

        Args:
            signals (array_like(str)): signal names
        '''
        if (signals is not None):
            self._signal_names = VDataUtils.insertion_order_set_list(signals)
            self._signals = set(self._signal_names)
        else:
            self._signals = set()

    def getPrefixes(self):
        '''
        Get the set of signal prefixes to match on

        Returns:
            set(str)
        '''
        return self._prefixes
    
    def setPrefixes(self, prefixes):
        '''
        Set the list of signal prefixes to match on.

        Args:
            prefixes (array_like(str)): signal prefixes
        '''
        if (prefixes is not None):
            self._prefixes = set(prefixes)
        else:
            self._prefixes = set()
    
    def getSignalNames(self):
        '''
        Get an ordered list of signal names that is same as the order of the signal name filter.

        Returns:
            array_like(str)
        '''
        return self._signal_names
    
    def isEmpty(self):
        '''
        True if no filter at all, otherwise False.

        Returns:
            bool
        '''
        return len(self._signals) == 0 and len(self._prefixes) == 0
    
    def hasNameFilterOnly(self):
        '''
        True if the filter only applies on exact signal name and no prefix matching, False otherwise.

        Returns:
            bool
        '''
        return len(self._signals) > 0 and len(self._prefixes) == 0

class VDataFrame:
    '''
    A class for two-dimensional tabular data frame that holds signal time-values.
    Column names can be accessed via method cols(), and signal time-values can be
    accessed through methods values(), objects(), sampling(), object1s depending
    on the usage scenario.

    Examples:
        >>> import pandas as _pd
        >>> ...
        >>> reader = factory.open()
        >>> frame = reader.df()
        >>> df = _pd.DataFrame(frame.objects(), columns=frame.cols(True))

    '''
    def __init__(self, buckets, series, signalFilter=None, columnExpandMode=None, signalQueueMode=None):
        '''
        The constructor for the data frame.  It is called via VDataReader.

        Args:
            buckets (array_like): the list of buckets.
            series (dict): the map of signal series.
            signalFilter (VDataSignalFilter, optional): the signal filter, default is None.
            columnExpandMode (int, optional): the column expand mode, default is None.
            signalQueueMode (str, optional): the signal queue mode, default is None.
        '''
        self._signalFilter = signalFilter if (signalFilter and isinstance(signalFilter, VDataSignalFilter)) else VDataSignalFilter()
        self._columnExpandMode = VDataUtils.getColumnExpandMode(columnExpandMode)
        self._qualifiedExpandName = VDataUtils.isQualifiedExpandName(columnExpandMode)
        self._signalQueueMode = VDataUtils.getSignalQueueMode(signalQueueMode)
        self._startTime = 0
        self._endTime = 0
        
        self._buckets = buckets
        self._series = {}
        for k in series:
            if (series[k].numBuckets() > 0):
                self._series[series[k].name()] = series[k]

    def __repr__(self):
        return str(self._series.keys())
    
    def getSignalFilter(self):
        '''
        Get the signal filter.

        Returns:
            VDataSignalFilter
        '''
        return self._signalFilter

    def setSignalFilter(self, signalFilter):
        '''
        Set the signal filter.

        Args:
            signalFilter (VDataSignalFilter): the filter
        '''
        if (signalFilter and isinstance(signalFilter, VDataSignalFilter)):
            self._signalFilter = signalFilter

    def getColumnExpandMode(self):
        '''
        Get the column expand mode for expanding complex type.

        Returns:
            int
        '''
        return self._columnExpandMode

    def setColumnExpandMode(self, mode):
        '''
        Set the column expand mode for expanding complex type.

        Args:
            mode (int): the expand mode
        '''
        self._columnExpandMode = VDataUtils.getColumnExpandMode(mode)
        self._qualifiedExpandName = VDataUtils.isQualifiedExpandName(mode)

    def getSignalQueueMode(self):
        '''
        Get the signal queue mode for value triage when there are multiple
        values at the same time.

        Returns:
            str
        '''
        return self._signalQueueMode

    def setSignalQueueMode(self, mode):
        '''
        Set the signal queue mode for value triage when there are multiple
        values at the same time.

        Args:
            mode (str): the queue mode
        '''
        self._signalQueueMode = VDataUtils.getSignalQueueMode(mode)
    
    def getStartTime(self):
        '''
        Get the earliest time of signals in the frame.  Note that this time may be
        the evenly-split start time of the first bucket and slightly different
        from the actual first signal time.

        Returns:
            int: millisecond since EPOCH
        '''
        return self._startTime
    
    def setStartTime(self, time):
        '''
        Set the start time of the frame.

        Args:
            time (int): millisecond since EPOCH
        '''
        self._startTime = time
    
    def getEndTime(self):
        '''
        Get the last time of signals in the frame.  Note that this time may be
        the evenly-split end time of the last bucket and slightly different
        from the actual last signal time.

        Returns:
            int: millisecond since EPOCH
        '''
        return self._endTime
    
    def setEndTime(self, time):
        '''
        Set the end time of the frame.

        Args:
            time (int): millisecond since EPOCH
        '''
        self._endTime = time
    
    def cols(self, includeTime=False):
        '''
        Get a list of column names.  The order of the column names is same as order
        of signal values in each row.  To include the time column at first index set 
        the includeTime parameter to true.

        Args:
            includeTime(bool, optional): whether to include time column at first index, default is False.
        
        Returns:
            array_like(str) the array of column names
        '''
        columns = VDataSeriesUtils.seriesToColumns(self._series, self._signalFilter, self._columnExpandMode, self._qualifiedExpandName)
        if (includeTime):
            columns.insert(0, 'time')
        return columns

    def series(self):
        '''
        Get a dict of all selected signal series.

        Returns:
            dict: map of series by their names
        '''
        return self._series
    
    def values(self, densifyRowsAhead=0, densifyOutputItv=0, signalQueueRows=0):
        '''
        Get a sorted 2-d array (row-columns) of time and all data values. The values are 
        read via a iterator-like processing which is more memory-efficient but consumes 
        more CPU. Therefore, this method is suitable for reading data files larger than 10MB.

        The first item of each row is time, followed by values.

        Args:
            densifyRowsAhead (int, optional): number of rows to look ahead to fill sparse data, default is 0.
            densifyOutputItv (int, optional): millis interval to down-sample data, default is 0 (no sampling).
            signalQueueRows (int, optional): number of rows to hold in queue for sorting, default is 0 (auto). 
        
        Returns:
            array_like(array_like)
        '''
        queue = VDataPollQueue()
        templateable = {}
        data = []
        interval = densifyOutputItv if densifyOutputItv > 0 else 0
        denseitv = interval != 0
        nextTime = 0

        columns = VDataSeriesUtils.seriesToColumns(self._series, self._signalFilter, self._columnExpandMode, self._qualifiedExpandName)
        templateable = VDataSeriesUtils.seriesToTemplate(self._series, columns, self._columnExpandMode, self._qualifiedExpandName)
        
        selectall = self._signalFilter.isEmpty()
        for column in self._series:
            if selectall or VDataSeriesUtils.serieContainsSignal(templateable, self._series[column].formula(), self._columnExpandMode, self._qualifiedExpandName):
                poll = VDataSeriesPoll(self._series[column], qsize=signalQueueRows, qmode=self._signalQueueMode)
                if (not poll.isEmpty()):
                    queue.put(poll)
        
        if (densifyRowsAhead <= 0):
            while(not queue.empty()):
                values = templateable.copy()
                polls = queue.pop()
                _time = polls[0].time()
                for _i in range(len(polls)):
                    poll = polls[_i]
                    self.__put(values, poll)

                    poll.pollAndAdd()
                    if (not poll.isEmpty()):
                        queue.put(poll)

                row = [_time]
                row.extend(values.values())
                data.append(row)
        else:
            records = []
            cnt = 0
            while(cnt <= densifyRowsAhead):
                cnt = cnt + 1
                if (queue.empty()):
                    break

                values = {}
                polls = queue.pop()
                _time = polls[0].time()
                for _i in range(len(polls)):
                    poll = polls[_i]
                    self.__tut(templateable, values, poll)

                    poll.pollAndAdd()
                    if (not poll.isEmpty()):
                        queue.put(poll)
                
                records.append(VDataRecord(_time, values))
            
            nextTime = self.__cutoffInterval(records[0]._time, interval) if denseitv else 0

            for record in records:
                if denseitv:
                    millis = self.__cutoffInterval(record._time, interval)
                    if millis != nextTime:  # output last dense interval
                        row = [nextTime]
                        row.extend(templateable.values())
                        data.append(row)
                        nextTime = nextTime + interval

                _values = record._values
                for _k in _values.keys():
                    templateable[_k] = _values[_k]

                if not denseitv:
                    row = [record._time]
                    row.extend(templateable.values())
                    data.append(row)

            while(not queue.empty()):
                polls = queue.pop()
                _time = polls[0].time()

                if denseitv:
                    millis = self.__cutoffInterval(_time, interval)
                    if millis != nextTime:  # output last dense interval
                        row = [nextTime]
                        row.extend(templateable.values())
                        data.append(row)
                        nextTime = nextTime + interval

                for _i in range(len(polls)):
                    poll = polls[_i]
                    self.__put(templateable, poll)

                    poll.pollAndAdd()
                    if (not poll.isEmpty()):
                        queue.put(poll)

                if not denseitv:
                    row = [_time]
                    row.extend(templateable.values())
                    data.append(row)
        
        if (denseitv and nextTime != 0):  # output last dense interval
            row = [nextTime]
            row.extend(templateable.values())
            data.append(row)

        return data 

    def __put(self, values, poll):
        pname = poll.name()
        pval = poll.value()
        subNames = poll.getSubNames()
        if (subNames is None):
            values[pname] = pval # simple type has been filtered by poll name, just put
        elif (self._columnExpandMode == DExpand.NONE):
            subValues = pval
            pmap = {}
            for i in range(len(subNames)):
                pmap[subNames[i]] = subValues[i]
            values[pname] = pmap # no expand has been filtered by poll name, reassemble to map
        else:
            subValues = pval
            for i in range(len(subNames)):
                subName = pname + "." + subNames[i] if self._qualifiedExpandName else subNames[i]
                if (subName in values):
                    values[subName] = subValues[i] # check if sub name is included then put

    def __tut(self, templateable, values, poll):
        pname = poll.name()
        pval = poll.value()
        subNames = poll.getSubNames()
        if (subNames is None):
            val = templateable.get(pname)
            if (val is None):
                templateable[pname] = pval
            else:
                vtype = type(val)
                if (vtype == float and isnan(val)) or (vtype == str and val == ''): # nan is float
                    templateable[pname] = pval
            values[pname] = pval # simple type has been filtered by poll name, just put
        elif (self._columnExpandMode == DExpand.NONE):
            subValues = pval
            pmap = {}
            for i in range(len(subNames)):
                pmap[subNames[i]] = subValues[i]
            val = templateable.get(pname)
            if (val is None):
                templateable[pname] = pmap
            else:
                vtype = type(val)
                if (vtype == float and isnan(val)) or (vtype == str and val == ''): # nan is float
                    templateable[pname] = pmap
            values[pname] = pmap # no expand has been filtered by poll name, reassemble to map
        else:
            subValues = pval
            for i in range(len(subNames)):
                subName = pname + "." + subNames[i] if self._qualifiedExpandName else subNames[i]
                if (subName in templateable):
                    val = values.get(subName)
                    if (val is None):
                        templateable[subName] = subValues[i]
                    else:
                        vtype = type(val)
                        if (vtype == float and isnan(val)) or (vtype == str and val == ''): # nan is float
                            templateable[subName] = val
                    values[subName] = subValues[i] # check if sub name is included then put
    
    def objects(self, densifyRowsAhead=0, densifyOutputItv=0):
        '''
        Get a sorted 2-d array (row-columns) of time and all data values. The values are 
        read all into memory and avoid sorting.  It is CPU-efficient but consumes more memory. 
        Therefore, this method is suitable for reading data files smaller than 10MB.

        The first item of each row is time, followed by values.

        Args:
            densifyRowsAhead (int, optional): number of rows to look ahead to fill sparse data, default is 0.
            densifyOutputItv (int, optional): millis interval to down-sample data, default is 0 (no sampling).
        
        Returns:
            array_like(array_like)
        '''
        if self._endTime - self._startTime > 3600000:
            return self.values(densifyRowsAhead, densifyOutputItv)
        oread = None
        if "all" == self._signalQueueMode:
            oread = VDataObjectsSeriesAllMode(self._series, self._signalFilter, self._columnExpandMode, self._qualifiedExpandName, self._startTime, self._endTime)
        elif "first" == self._signalQueueMode:
            oread = VDataObjectsSeriesFirstMode(self._series, self._signalFilter, self._columnExpandMode, self._qualifiedExpandName, self._startTime, self._endTime)
        else:
            oread = VDataObjectsSeriesReader(self._series, self._signalFilter, self._columnExpandMode, self._qualifiedExpandName, self._startTime, self._endTime)
        
        objects = oread.read()
        if (densifyRowsAhead <= 0 or len(objects) <= 1): # less than one row no need to densify
            return objects
        
        # first, detect and set the first non-null value for each column. col=0 is time so we skip it
        for col in range(1, len(objects[0])):
            if (objects[0][col] is None):
                for row in range(1, densifyRowsAhead):
                    if (objects[row][col] is not None): # found the first non-null
                        objects[0][col] = objects[row][col]
                        break
        
        # densify
        for row in range(1, len(objects)): # row=0 is already densified
            for col in range(1, len(objects[row])): # col=0 is time so we skip it
                if (objects[row][col] is None):
                    objects[row][col] = objects[row - 1][col]
        
        if (densifyOutputItv <= 0):
            return objects
        
        # densify to interval
        itv = []
        nextTime = self.__cutoffInterval(objects[0][0], densifyOutputItv)
        millis = nextTime
        row = 0
        rows = len(objects)
        lastpos = -1
        pos = 0

        while (row < rows):
            while (millis == nextTime):
                row = row + 1
                if (row >= rows):
                    break;
                millis = self.__cutoffInterval(objects[row][0], densifyOutputItv)
            
            pos = row - 1
            if (lastpos != pos): # row not yet used
                objects[pos][0] = nextTime
                itv.append(objects[pos])
                lastpos = pos
            else: # row already used, need to make a copy
                objcopy = (objects[pos])[:]
                objcopy[0] = nextTime
                itv.append(objcopy)
            
            nextTime = nextTime + densifyOutputItv
        
        return itv

    def object1s(self):
        '''
        Return a sorted 2-d array (row-columns) of all data objects at the sampled 1-Hz interval.

        The first item of each row is time, followed by values.

        Returns:
            array_like(array_like)
        '''
        return self.sampling(1000)
    
    def sampling(self, frequency):
        '''
        Return a sorted 2-d array (row-columns) of all data objects sampled down to the specified 
        frequency in milliseconds. For example, 1-Hz equals a frequency of 1000 (ms).

        The first item of each row is time, followed by values.

        Args:
            frequency (int): the sampled frequency with value greater than 1.
        
        Returns:
            array_like(array_like)
        '''
        if (frequency <= 1):
            raise Exception('Sampling frequency must be greater than 1')
        
        oread = None
        if ("first" == self._signalQueueMode):
            oread = VDataObjectsSeriesFirstMode(self._series, self._signalFilter, self._columnExpandMode, self._qualifiedExpandName, self._startTime, self._endTime)
        else:
            oread = VDataObjectsSeriesReader(self._series, self._signalFilter, self._columnExpandMode, self._qualifiedExpandName, self._startTime, self._endTime)
        
        return oread.sampling(frequency)

    def __cutoffInterval(self, time, interval):
        millis = floor(time)
        cutoff = floor(millis / interval) * interval
        return cutoff + interval if millis > cutoff else cutoff

class VDataDecoder:
    def __init__(self, reader, meta):
        self._reader = reader
        self._meta = meta
        self._signals = {}
        self._prefixes = {}
        self._insensitiveCase = False
        self._readLivingData = True
        self._queryFilter = True
        self._queryStartTime = 0
        self._queryEndTime = 0
        self._columnExpandMode = None
        self._qualifiedExpandName = False
        self._signalQueueMode = None
        self._buckets = None
        self._keys = None
        self._signalDecoders={}
        
    def __repr__(self): 
        if self._meta is None:
            return '{}'

        return '{start=' + (str(self._meta.queryStartTime()) if self._meta.queryStartTime() > 0 else str(self._meta.storageStartTime())) + ', end=' + (str(self._meta.queryEndTime()) if self._meta.queryEndTime() > 0 else str(self._meta.storageEndTime())) + ', buckets=' + str(len(self._buckets)) + ', keys=' + str(len(self._keys)) + '}'

    def setSignalFilter(self, signalFilter):
        if (signalFilter is not None):
            self._signals = signalFilter.getSignals()
            self._prefixes = signalFilter.getPrefixes()
        else:
            self._signals = {}
            self._prefixes = {}
    
    def setInsensitiveCase(self, insensitiveCase):
        self._insensitiveCase = insensitiveCase

    def setReadLivingData(self, readLivingData):
        self._readLivingData = readLivingData

    def setQueryFilter(self, queryFilter):
        self._queryFilter = queryFilter

    def setQueryRange(self, qstime, qetime):
        self._queryStartTime = qstime
        self._queryEndTime = qetime

    def setColumnExpandMode(self, columnExpandMode):
        self._columnExpandMode = columnExpandMode

    def setSignalQueueMode(self, signalQueueMode):
        self._signalQueueMode = signalQueueMode
    
    def setSignalDecoders(self, signalDecoders):
        self._signalDecoders = signalDecoders

    def initialize(self):
        hasSignalFilter = len(self._signals) > 0 or len(self._prefixes) > 0
        formulas = {}
        self._keys = {}
        self._columnExpandMode = VDataUtils.getColumnExpandMode(self._columnExpandMode)
        self._qualifiedExpandName = VDataUtils.isQualifiedExpandName(self._columnExpandMode)
        if self._queryStartTime ==0 and self._meta.queryStartTime() ==0 :
            self._queryStartTime = self._meta.storageStartTime()
        if self._queryEndTime ==0 and self._meta.queryEndTime() ==0 :
            self._queryEndTime = self._meta.storageEndTime()

        formatVersion = self._meta.formatVersion()
        compressMethod = self._meta.compressMethod()
        # encryptMethod = self._meta.encryptMethod()
        blocksCount = self._meta.blocksCount()
        storageIdLength = self._meta.getStorageIdLength()

        logger.debug("file format verion: " + str(formatVersion))
        logger.debug("file bucket count: " + str(blocksCount))
        if (formatVersion >= 26):
            logger.debug("file query start time: " + str(self._meta.queryStartTime()))
            logger.debug("file query end time: " + str(self._meta.queryEndTime()))

        if self._meta.getPageSize() != 0x8000:
            self.readKeys()
        else:
            self.readStfKeys()

        for name, key in self._keys.items():
            formulas[key._seriesid] = key._formula
            if (self._signalDecoders !=None) & (name in self._signalDecoders):
                if (isinstance(key._formula , VDataFormulaBlob)):
                    de = self._signalDecoders[name]
                    key._formula.setSignalDeocder(de)
                else:
                    key._formula=VDataFormulaBlob(name)
                    key._formula.setSignalDeocder(self._signalDecoders[name])
                    formulas[key._seriesid] = key._formula
                            
        self._buckets = []
        for b in range(blocksCount):
            crc = 0
            length = 0
            bucketCycle = 0
            bucketStartTime = 0
            bucketEndTime = 0
            living = 0
            
            blobCompressType=0
            position = 0
            dataStartTime = 0
            dataEndTime =0
            blobCount=0
            blobDataLength=0
            blobCrc=0

            if (formatVersion < 24):
                crc = _struct.unpack('<q', self._reader.read(8))[0]
                living = self._reader.read(1)[0] & 1
                self._reader.read(7) #ignore
                length = _struct.unpack('<i', self._reader.read(4))[0] - 24 #include header
                self._reader.read(4) #ignore
            elif (formatVersion < 27):
                crc = _struct.unpack('<q', self._reader.read(8))[0]
                living = self._reader.read(1)[0] & 1
                self._reader.read(3) #ignore
                bucketCycle = _struct.unpack('<i', self._reader.read(4))[0]
                bucketStartTime = _struct.unpack('<q', self._reader.read(8))[0]
                bucketEndTime = _struct.unpack('<q', self._reader.read(8))[0]
                length = _struct.unpack('<i', self._reader.read(4))[0] - 40 #include header
                self._reader.read(4) #ignore
            elif (self._meta.getPageSize () != 0x8000):
                #default 64 page 
                crc = _struct.unpack('<q', self._reader.read(8))[0]
                living = self._reader.read(1)[0] & 1
                self._reader.read(3) #ignore
                bucketCycle = _struct.unpack('<i', self._reader.read(4))[0]
                bucketStartTime = _struct.unpack('<q', self._reader.read(8))[0]
                bucketEndTime = _struct.unpack('<q', self._reader.read(8))[0]
                length = _struct.unpack('<i', self._reader.read(4))[0] - 72 #include header
                
                position = _struct.unpack('<i', self._reader.read(4))[0]
                dataStartTime = _struct.unpack('<q', self._reader.read(8))[0]
                dataEndTime = _struct.unpack('<q', self._reader.read(8))[0]
                blobCrc = _struct.unpack('<q', self._reader.read(8))[0]
                blobCount = _struct.unpack('<i', self._reader.read(4))[0]
                blobDataLength = _struct.unpack('<i', self._reader.read(4))[0]
            else: 
                # 32k page
                crc = _struct.unpack('<q', self._reader.read(8))[0]
                living = self._reader.read(1)[0] & 1
                self._reader.read(3) #ignore
                bucketCycle = _struct.unpack('<i', self._reader.read(4))[0]
                bucketStartTime = _struct.unpack('<q', self._reader.read(8))[0]
                bucketEndTime = _struct.unpack('<q', self._reader.read(8))[0]
                length = _struct.unpack('<i', self._reader.read(4))[0] - 48 #include header
                
                position = _struct.unpack('<i', self._reader.read(4))[0]
                blobCount = _struct.unpack('<i', self._reader.read(4))[0]
                blobDataLength = _struct.unpack('<i', self._reader.read(4))[0]                
                
            if (length <= 0):
                raise Exception('FORMAT_VDATA_BUCKET_LENGTH_INVALID')

            databytes = self.decompress(self._reader.read(length), compressMethod)
            
            if (crc != 0):
                # when CRC is non-zero, let's verify CRC
                if (crc != binascii.crc32(databytes)):
                    raise Exception('FORMAT_VDATA_CRC_MISMATCH')
            if (living != 0 and not self._readLivingData):
                continue
            
            seriesCount = 0
            activePages = 0
            seriesMetas = []
            storageIds = []
            seriesIds = []
            index = 8
            
            (seriesCount, activePages) = _struct.unpack('<ii', databytes[0:8])
            if (seriesCount <= 0):
                raise Exception('FORMAT_VDATA_SERIES_COUNT_ZERO')
            if (activePages <= 0):
                raise Exception('FORMAT_VDATA_ACTIVE_PAGES_ZERO')

            if (self._meta.getPageSize() != 0x8000):
                for i in range(seriesCount):
                    seriesIds.append(_struct.unpack('<i', databytes[index:index+4])[0])
                    index += 4
                for i in range(seriesCount):
                    storageIds.append(_struct.unpack('<q', databytes[index:index+8])[0])
                    index += 8
            else:
                #5 byte storageId for 32k page size vsw
                for i in range(len(self._keyIds)):
                    if (((databytes [index+(i>>3)] >> (i&0x7)) & 0x01) == 1):
                        seriesIds.append(self._keyIds[i])
                        
                index = (len(self._keyIds) +7 )//8 + index
                for i in range(seriesCount):
                    storageId = _struct.unpack('<i', databytes[index:index+4])[0]
                    storageId = storageId& 0xffffffff
                    if (storageIdLength ==5):
                        storageId = ((databytes[index+4] &0xff) << 32 ) + storageId
                    else:
                        storageId = ((databytes[index+5] &0xff) << 40 ) + ((databytes[index+4] &0xff) << 32 ) + storageId
                    storageIds.append(storageId)
                    index += storageIdLength
            
            blobSeriesIds =[]
            blobOffsetVec =[]
            blobLengthVec = []
            sid_to_blob_idx={}
            for i in range (blobCount):  
                blobSeriesIds.append(_struct.unpack('<i', databytes[index:index+4])[0])
                sid_to_blob_idx[blobSeriesIds[i]]=i
                index += 4
            for i in range (blobCount):  
                blobOffsetVec.append(_struct.unpack('<i', databytes[index:index+4])[0])
                index += 4            
            for i in range (blobCount):  
                blobLengthVec.append(_struct.unpack('<i', databytes[index:index+4])[0])
                index += 4             
            
            for i in range(seriesCount):
                if seriesIds[i] not in formulas:
                    raise Exception('FORMAT_VDATA_SERIES_NOT_FOUND' + str(seriesIds[i]))
                if (hasSignalFilter and not VDataSeriesUtils.serieMatchSignalFilter(self._signals, self._prefixes, formulas[seriesIds[i]], self._columnExpandMode, self._qualifiedExpandName)):
                    continue
                mt = VDataSeriesMeta(formulas[seriesIds[i]], storageIds[i], i , self._meta.getPageSize(), storageIdLength)
                if (mt._dataLength == 0 or mt._itemCount == 0):
                    raise Exception('FORMAT_VDATA_SERIES_DATA_EMPTY')

                
                seriesMetas.append(mt)
            
            bucket = VDataBucket()
            bucket.setStartTime(bucketStartTime)
            bucket.setEndTime(bucketEndTime)
            bucket.setCycle(bucketCycle)
            bucket.setLiving(living)
            bucket.setCrc(crc)
            
            blobDatabytes = []
            if (blobDataLength>0):
                blobDatabytes =self.decompress(self._reader.read(blobDataLength), compressMethod)
            
            for i in range(len(seriesMetas)):
                mt = seriesMetas[i]
                bstart = index + mt._pageIndex * self._meta.getPageSize() + mt._pageOffset
                bend = bstart + mt._dataLength
                bt = databytes[bstart:bend]
                
                seriesBucket = VDataSeriesBucket()
                seriesBucket.setFormatVersion(formatVersion)
                seriesBucket.setMeta(mt)
                seriesBucket.setPage(bt)
                seriesBucket.setBucketCycle(bucketCycle)
                seriesBucket.setBucketStartTime(bucketStartTime)
                seriesBucket.setBucketEndTime(bucketEndTime)
                seriesBucket.setSeriesTimestampLength(self._meta.getSeriesTimestampLength())
                if (mt.getSeriesId() in sid_to_blob_idx):
                    idx = sid_to_blob_idx[mt.getSeriesId()]
                    seriesBucket.setBlobData(blobDatabytes [blobOffsetVec[idx]:blobOffsetVec[idx]+blobLengthVec[idx]])
                if (seriesBucket.getItemCount() > 0):
                    bucket.addSeriesBucket(seriesBucket)

                    

            if (len(bucket.seriesBuckets) > 0):
                if (bucket.getStartTime() == 0): # old version with unknown start time
                    serieDecoders = VDataSeriesDecodeBuilder.builds(bucket.getSeriesBuckets())
                    minSeriesStartTime = serieDecoders[0].time()
                    for i in range(1, len(serieDecoders)):
                        tm = serieDecoders[i].time()
                        if (tm < minSeriesStartTime):
                            minSeriesStartTime = tm
                    bucket.setStartTime(minSeriesStartTime)
                    bucket.setNoTime(1)
                    
                VDataBucketUtils.sortAddBucket(self._buckets, bucket, False, self._signalQueueMode)
        
        # Set the query range for each series of the bucket
        VDataBucketUtils.updateBucketQueryRange(self._buckets, self._meta, self._signalQueueMode, self._queryFilter, self._queryStartTime, self._queryEndTime)

    def readKeys(self):
        compressMethod = self._meta._compressMethod

        (keysCount, length) = _struct.unpack('<ii', self._reader.read(8))
        if (keysCount <= 0):
            raise Exception('FORMAT_VDATA_KEYS_COUNT_INVALID')
        if (length <= 0):
            raise Exception('FORMAT_VDATA_KEYS_LENGTH_INVALID')
        databytes = self.decompress(self._reader.read(length), compressMethod)

        fmbulider = VDataFormulaFactory()
        datareader = VDataByteReader(databytes)
        for i in range(keysCount):
            keyid = _struct.unpack('<i', datareader.read(4))[0]
            keydesc = ''
            b = datareader.read(1)
            while (b[0] != 0):
                keydesc += chr(b[0])
                b = datareader.read(1)
            formula = fmbulider.build(keydesc, self._insensitiveCase)
            sname = self.getUniqueName(self._keys, formula._name)
            if (sname != formula._name):
                logger.warn("Replace series " + str(keyid) + " duplicate name {" + formula._name + "} with name {" + sname + "}")
                formula._name = sname
            self._keys[sname] = VDataSeriesSpec(sname, keyid, formula, keydesc)
    
    def readStfKeys(self):
        (keysCount, length) = _struct.unpack('<ii', self._reader.read(8))
        if (keysCount <= 0):
            raise Exception('FORMAT_VDATA_KEYS_COUNT_INVALID')
        if (length <= 0):
            raise Exception('FORMAT_VDATA_KEYS_LENGTH_INVALID')       
        databytes = self._reader.read(length)
        noneFormula = VDataFormulaNone('keys')
        decode = VDataInt32DeltaDecode(databytes, noneFormula, BitTracker())
        
        self._keyIds = {}
        for i in range (keysCount):
            decode.next()
            self._keyIds[i] = decode.get()
            sname ="0x%08X"%self._keyIds[i]
            self._keys[sname] =  VDataSeriesSpec(sname, self._keyIds[i] , VDataFormulaNone(sname), '')
        

    def getUniqueName(self, keys, key):
        if key not in keys:
            return key
        
        counter = 2
        backup = key + '_duplicate_{:05d}'.format(counter)

        while backup in keys and counter < 100000:
            counter = counter + 1
            backup = key + '_duplicate_{:05d}'.format(counter)
        
        if (counter == 100000):
            raise Exception('FORMAT_VDATA_KEY_NAME_BACKUP_EXHAUSTED: ' + key)

        return backup

    def decompress(self, _bytes, _compressMethod):
        if (_compressMethod == 1):
            return gzip.decompress(_bytes)
        if (_compressMethod == 2):
            return snappy.decompress(_bytes)
        if (_compressMethod == 3):
            return zstd.uncompress(_bytes)
        return _bytes

    def buckets(self):
        return self._buckets
    
    def keys(self):
        return self._keys
    
    def meta(self):
        return self._meta

class VDataBucketUtils:
    def sortAddBucket(buckets, bucket, dropMultiFileIntersects, signalQueueMode):
        if VDataUtils.isAllSignalQueueMode(signalQueueMode):
            VDataBucketUtils.sortAllBucketForAllQueueMode(buckets, bucket, dropMultiFileIntersects)
        else:
            VDataBucketUtils.sortAllBucketForSingleQueueMode(buckets, bucket)
    
    def sortAllBucketForSingleQueueMode(buckets, bucket):
        size = len(buckets)
        if (size == 0):
            logger.info("Add bucket " + str(bucket))
            buckets.append(bucket)
            return
        
        bucketStartTime = bucket.getStartTime()
        for i in reversed(range(size)):
            bk = buckets[i]
            st = bk.getStartTime()
            if (st == bucketStartTime):
                if (bucket.getCrc() != 0):
                    for j in reversed(range(i)):
                        stbk = buckets[j]
                        if (stbk.getStartTime() != st):
                            break
                        if (bucket.getCrc() == stbk.getCrc()): #when non-zero CRC are identical, we know they are same
                            reason = "identical"
                            logger.warn("Keep " + reason + " bucket " + str(stbk) + " discard bucket " + str(bucket))
                            return
                logger.info("Add bucket " + str(bucket))
                buckets.insert(i + 1, bucket)
                return
            elif (st < bucketStartTime):
                logger.info("Add bucket " + str(bucket))
                buckets.insert(i + 1, bucket)
                return
        
        logger.info("Add bucket " + str(bucket))
        buckets.insert(0, bucket)

    def sortAllBucketForAllQueueMode(buckets, bucket, dropMultiFileIntersects): 
        size = len(buckets)
        if (size == 0):
            logger.info("Add bucket " + str(bucket))
            buckets.append(bucket)
            return
        
        bucketStartTime = bucket.getStartTime()
        for i in reversed(range(size)):
            bk = buckets[i]
            st = bk.getStartTime()
            if (bk.intersects(bucket)):
                if (st == bucketStartTime):
                    if (not bucket.isLiving()):  # bucket is final
                        if (bk.isLiving() or bk.getCycle() >= bucket.getCycle()):
                            reason = "final" if bk.isLiving() else ("higher freq" if bk.getCycle() > bucket.getCycle() else "later")
                            logger.warn("Keep " + reason + " bucket " + str(bucket) + " discard bucket " + str(bk))
                            buckets[i] = bucket.merge(bk)
                            return
                    elif (bk.isLiving()): # bucket is living and bk is living
                        bucketEndTime = bucket.getEndTime()
                        et = bk.getEndTime()
                        if (bucketEndTime > et or (bucketEndTime == et and bk.getCycle() > bucket.getCycle())):
                            reason = "longer" if bucketEndTime > et else "higher freq"
                            logger.warn("Keep " + reason + " bucket " + str(bucket) + " discard bucket " + str(bk))
                            buckets[i] = bucket.merge(bk)
                            return
                    elif (bk.getEndTime() != 0 and bucket.getEndTime() > bk.getEndTime()): #bucket is living and bk is final, but bucket has extra end time
                        logger.warn("Keep longer bucket " + str(bucket) + " discard bucket " + str(bk))
                        buckets[i] = bucket.merge(bk)
                        return
                    bk.merge(bucket)
                    logger.warn("Keep bucket " + str(bk) + " discard bucket" + str(bucket))
                else:
                    if (dropMultiFileIntersects and not bucket.isLiving()):
                        logger.warn("Keep final bucket " + str(bucket) + " discard bucket " + str(bk))
                        buckets[i] = bucket.merge(bk)
                        return
                    if (bucket.isLiving()):
                        if (bk.getEndTime() != 0 and bucket.getEndTime() > bk.getEndTime()): #overlapping living, lets do extra
                            logger.warn("Add bucket " + str(bucket) + ", but only start from the last bucket's end time of " + str(bk.getEndTime()))
                            bucket.setStartTime(bk.getEndTime() + 1)
                            buckets.insert(i + 1, bucket)
                            return
                    else:
                        if (bk.isLiving()): #we cannot be completely sure how much living bucket actually covers so we keep both
                            logger.warn("Add bucket " + str(bucket) + ", also keep living bucket " + str(bk))
                            buckets.insert(i + (1 if st < bucketStartTime else 0), bucket)
                            return
                        else:
                            logger.warn('Time intersection problem with two final buckets')
                    bk.merge(bucket)
                    logger.warn("Keep bucket " + str(bk) + " discard bucket" + str(bucket))
                return
            elif (st < bucketStartTime):
                logger.info("Add bucket " + str(bucket))
                buckets.insert(i + 1, bucket)
                return
        
        logger.info("Add bucket " + str(bucket))
        buckets.insert(0, bucket)

    def updateBucketQueryRange(buckets, meta, signalQueueMode, queryFilter, queryStartTime, queryEndTime):
        _qstime = (queryStartTime if queryStartTime > 0 else meta._queryStartTime) if queryFilter else 0 #override if provided
        
        if (VDataUtils.isAllSignalQueueMode(signalQueueMode)):
            _qetime = (queryEndTime if queryEndTime > 0 else meta._queryEndTime) if queryFilter else 0 #override if provided
            for b in range(len(buckets)):
                bucket = buckets[b]
                letime = 0 if b == 0 else buckets[b - 1].getEndTime()               # last end time
                cetime = sys.maxsize - 1 if bucket.isLiving() else bucket.getEndTime()  # current end time
                qstime = max(_qstime, (0 if b == 0 else (0 if letime <= 0 else letime + 1)))
                qetime = min(_qetime, cetime) if _qetime > 0 else cetime
                
                for j in range (len(bucket.seriesBuckets)):
                    seriesBucket = bucket.seriesBuckets[j]
                    seriesBucket.setQueryStartTime(qstime)
                    seriesBucket.setQueryEndTime(qetime)
        else:
            _qetime = (queryEndTime if queryEndTime > 0 else meta._queryEndTime) if queryFilter else sys.maxsize - 1 #override if provided
            for b in range(len(buckets)):
                bucket = buckets[b]
                for j in range (len(bucket.seriesBuckets)):
                    seriesBucket = bucket.seriesBuckets[j]
                    seriesBucket.setQueryStartTime(_qstime)
                    seriesBucket.setQueryEndTime(_qetime)

class VDataSeriesSpec:
    def __init__(self, name, seriesid, formula, desc):
        self._name = name
        self._seriesid = seriesid
        self._formula = formula
        self._desc = desc

class VDataSeriesUtils:
    def seriesToColumns(series, signalFilter, columnExpandMode, qualifiedExpandName):
        if (signalFilter.hasNameFilterOnly()):
            return signalFilter.getSignalNames()

        allcols = []
        if (columnExpandMode == DExpand.NONE):
            allcols = list(series.keys())
        else:
            for k in series:
                ss = series[k]
                if (ss.numBuckets() == 0):
                    continue
                
                formula = ss.formula()
                if (isinstance(formula, VDataFormulaStruct) or isinstance(formula, VDataFormulaNamedArray)):
                    for f in formula._formulas:
                        if (qualifiedExpandName):
                            allcols.append(k + '.' + f._name)
                        else:
                            allcols.append(f._name)
                    continue
                
                allcols.append(formula._name)
        
        # no filter
        if (signalFilter.isEmpty()):
            return VDataUtils.insertion_order_set_list(allcols)
        
        selected = []
        smap = signalFilter.getSignals()
        spfx = signalFilter.getPrefixes()
        for col in allcols:
            if (VDataSeriesUtils.containsSignal(smap, spfx, col)):
                selected.append(col)

        return VDataUtils.insertion_order_set_list(selected)
    
    def seriesToTemplate(series, columns, columnExpandMode, qualifiedExpandName):
        templateable = {}

        for column in columns:
            templateable[column] = None
        
        if (columnExpandMode == DExpand.NONE):
            for k in series:
                ss = series[k]
                if (ss.numBuckets() == 0):
                    continue
                if (ss._name in templateable):
                    templateable[ss._name] = VDataSeriesUtils.serieColumnDefaultValue(ss.getType())
            return templateable
                
        for k in series:
            ss = series[k]
            if (ss.numBuckets() == 0):
                continue
            
            formula = ss.formula()
            if (isinstance(formula, VDataFormulaNamedArray)):
                for f in formula._formulas:
                    name = k + '.' + f._name if qualifiedExpandName else f._name
                    if (name in templateable):
                        templateable[name] = VDataSeriesUtils.serieColumnDefaultValue(ss.getType())
            elif (isinstance(formula, VDataFormulaStruct)):
                dtypes = VDataSeriesUtils.getSubTypes(ss._buckets[0])
                for i in range(len(formula._formulas)):
                    f = formula._formulas[i]
                    name = k + '.' + f._name if qualifiedExpandName else f._name
                    if (name in templateable):
                        templateable[name] = VDataSeriesUtils.serieColumnDefaultValue(dtypes[i])
            else:
                if (ss._name in templateable):
                    templateable[ss._name] = VDataSeriesUtils.serieColumnDefaultValue(ss.getType())
        
        return templateable
    
    def serieColumnDefaultValue(dtype):
        if (dtype == DType.String):
            return ''
        elif (dtype == DType.Array or dtype == DType.Struct):
            return None
        else:
            return nan
    
    def getSubTypes(serieBucket):
        bt = serieBucket.getPage()
        btreader = VDataByteReader(bt)
        btreader.read(1)[0] # skip first type byte which should be struct

        high_len = btreader.read(1)[0]
        low_len = btreader.read(1)[0]
        length = ((high_len & 0xFF) << 8) | (low_len & 0xFF)
        
        subtypes = []
        for i in range(length):
            sub = btreader.read(1)[0]
            subtypes.append((sub >> 4) & 0x0F)

        return subtypes
    
    def serieContainsSignal(signals, formula, columnExpandMode, qualifiedExpandName):
        if (columnExpandMode == DExpand.NONE):
            return True

        if (isinstance(formula, VDataFormulaStruct) or isinstance(formula, VDataFormulaNamedArray)):
            serieName = formula._name
            for f in formula._formulas:
                name = (serieName + '.' + f._name) if qualifiedExpandName else f._name
                if name in signals:
                    return True
        else:
            return formula._name in signals

        return False

    def serieMatchSignalFilter(signals, prefixes, formula, columnExpandMode, qualifiedExpandName):
        if (columnExpandMode == DExpand.NONE):
            return VDataSeriesUtils.containsSignal(signals, prefixes, formula._name)

        if (isinstance(formula, VDataFormulaStruct) or isinstance(formula, VDataFormulaNamedArray)):
            serieName = formula._name
            for f in formula._formulas:
                name = (serieName + '.' + f._name) if qualifiedExpandName else f._name
                if VDataSeriesUtils.containsSignal(signals, prefixes, name):
                    return True
        else:
            return VDataSeriesUtils.containsSignal(signals, prefixes, formula._name)

        return False

    def containsSignal(signals, prefixes, name):
        if (name in signals):
            return True
    
        for prefix in prefixes:
            if (name.startswith(prefix)):
                return True

        return False

    def getFirstDataTime(bt):
        time = bt.getFirstTime()
        if (time is not None):
            return time
        
        decoder = VDataSeriesDecodeBuilder.build(bt)
        time = decoder.time()
        bt.setFirstTime(time)
        
        return time

class VDataObjectsSeriesReader:
    def __init__(self, series, signalFilter, columnExpandMode, qualifiedExpandName, startTime, endTime):
        self._series = series
        self._signalFilter = signalFilter
        self._columnExpandMode = columnExpandMode
        self._qualifiedExpandName = qualifiedExpandName
        self._startTime = startTime
        self._endTime = endTime

        timediff = self._endTime - self._startTime + 1
        if (timediff <= 0):
            raise Exception ('invalid negative time range')
        
        if (timediff > sys.maxsize):
            raise Exception ('time range is too big to use objects() method')
        
        self._columns = VDataSeriesUtils.seriesToColumns(series, signalFilter, columnExpandMode, qualifiedExpandName)
        self._indices = {}
        for i in range(len(self._columns)):
            self._indices[self._columns[i]] = i + 1 # offset by time at 0-index;

        self._colsize = len(self._columns) + 1; # time at 0-index

    def read(self):
        if (self._series is None or len(self._series) == 0):
            return []

        hasComplexType = False
        if (self._columnExpandMode != DExpand.NONE):
            for column in self._series:
                serie = self._series[column]
                fm = serie.buckets()[0].getFormula()
                if (isinstance(fm, VDataFormulaArray) or isinstance(fm, VDataFormulaStruct)):
                    hasComplexType = True
                    break
        
        rawobjs = self.__readComplexRawObjects() if hasComplexType else self.__readSimpleRawObjects()
        objs = []
        for rowobj in rawobjs:
            if rowobj is not None:
                for row in rowobj:
                    objs.append(row.toObjects())

        return objs

    def __readComplexRawObjects(self):
        rows = self._endTime - self._startTime + 1
        rawobjs = [None] * rows # 3-d array of millisecond - (List of micro-second level Instant + data)
        comps = [None, None]
        
        for pname in self._series:
            serie = self._series[pname]
            colidx = self._indices.get(pname)
            decoders = VDataSeriesDecodeBuilder.builds(serie.buckets())
            subNames = decoders[0].getSubNames()
            noSubNames = subNames is None
            subIndices = None
            if (not noSubNames) and self._columnExpandMode != DExpand.NONE:
                subIndices = [None] * len(subNames)
                for i in range(len(subNames)):
                    subName = pname + "." + subNames[i] if self._qualifiedExpandName else subNames[i]
                    subIndices[i] = self._indices.get(subName)
            
            for decoder in decoders:
                while not decoder.isEmpty():
                    time = decoder.time()
                    millis = decoder.timestamp()
                    pval = decoder.value()
                    if (millis >= decoder.qstime and millis <= decoder.qetime):
                        rowidx = millis - self._startTime
                        if (rawobjs[rowidx] is None):
                            list = []
                            vals = self.createValueArray(time)
                            list.append(vals)
                            rawobjs[rowidx] = list
                        else:
                            list = rawobjs[rowidx]
                            self.comp(list, time, colidx, subNames, subIndices, comps)
                            
                            if (comps[1] == 1):
                                vals = list[comps[0]]
                            else:
                                vals = self.createValueArray(time)
                                list.insert(comps[0], vals)
                        
                        if (noSubNames):
                            vals.add(colidx, pval)
                        else:
                            subValues = pval
                            for i in range(len(subNames)):
                                if (subIndices[i] is not None):
                                    vals.add(subIndices[i], subValues[i])
                    
                    decoder.pollAndAdd()
        return rawobjs

    def __readSimpleRawObjects(self):
        rows = self._endTime - self._startTime + 1
        rawobjs = [None] * rows # 3-d array of millisecond - (List of micro-second level Instant + data)

        comps = [None, None]
        
        for pname in self._series:
            serie = self._series[pname]
            colidx = self._indices.get(pname)
            decoders = VDataSeriesDecodeBuilder.builds(serie.buckets())
            for decoder in decoders:
                while not decoder.isEmpty():
                    time = decoder.time()
                    millis = decoder.timestamp()
                    pval = decoder.value()
                    if (millis >= decoder.qstime and millis <= decoder.qetime):
                        rowidx = millis - self._startTime
                        if (rawobjs[rowidx] is None):
                            list = []
                            vals = self.createValueArray(time)
                            list.append(vals)
                            rawobjs[rowidx] = list
                        else:
                            list = rawobjs[rowidx]
                            self.comp(list, time, colidx, None, None, comps)
                            
                            if (comps[1] == 1):
                                vals = list[comps[0]]
                            else:
                                vals = self.createValueArray(time)
                                list.insert(comps[0], vals)
                        
                        vals.add(colidx, pval)
                    
                    decoder.pollAndAdd()
        return rawobjs

    def sampling(self, frequency):
        if (self._series is None or len(self._series) == 0):
            return []

        hasComplexType = False
        if (self._columnExpandMode != DExpand.NONE):
            for column in self._series:
                serie = self._series[column]
                fm = serie.buckets()[0].getFormula()
                if (isinstance(fm, VDataFormulaArray) or isinstance(fm, VDataFormulaStruct)):
                    hasComplexType = True
                    break
        
        objs = self.__samplingComplex(frequency) if hasComplexType else self.__samplingSimple(frequency)
        nonEmptyIndex = len(objs) - 1
        wbreak = False
        while (nonEmptyIndex >= 0):
            row = objs[nonEmptyIndex]
            for i in range(1, len(row)):
                if (row[i] is not None):
                    wbreak = True
                    break
            if (wbreak):
                break
            nonEmptyIndex = nonEmptyIndex -1
        
        if (nonEmptyIndex == len(objs) - 1):
            return objs
        elif (nonEmptyIndex < 0):
            return []
        else:
            return objs[0:nonEmptyIndex + 1]

    def __samplingComplex(self, frequency):
        startFreqBase = floor(self._startTime / frequency)
        rows = floor(self._endTime / frequency) - startFreqBase + 1
        rawobjs = [None] * rows # 2-d array of millisecond + data
        for i in range(rows):
            rawobjs[i] = [None] * self._colsize
            rawobjs[i][0] = (startFreqBase + i) * frequency 
        
        for pname in self._series:
            rowidx = 0
            lastrowidx = -1
            serie = self._series[pname]
            colidx = self._indices.get(serie.name())
            decoders = VDataSeriesDecodeBuilder.builds(serie.buckets())
            subNames = decoders[0].getSubNames()
            noSubNames = subNames is None
            subIndices = None
            if (not noSubNames and self._columnExpandMode != DExpand.NONE):
                subIndices = [None] * len(subNames)
                for i in range(len(subNames)):
                    subName = pname + "." + subNames[i] if self._qualifiedExpandName else subNames[i]
                    subIndices[i] = self._indices.get(subName)
            
            for decoder in decoders:
                while not decoder.isEmpty():
                    rowidx = floor(decoder.timestamp() / frequency) - startFreqBase

                    if (rowidx != lastrowidx and rowidx >= 0 and rowidx < rows):
                        lastrowidx = rowidx
                        if (noSubNames):
                            if (rawobjs[rowidx][colidx] is None):
                                rawobjs[rowidx][colidx] = decoder.value()
                        else:
                            subValues = decoder.value()
                            for i in range(len(subNames)):
                                if (subIndices[i] is not None and rawobjs[rowidx][subIndices[i]] is None):
                                    rawobjs[rowidx][subIndices[i]] =subValues[i]
                    
                    decoder.pollAndAdd()
        
        return rawobjs

    def __samplingSimple(self, frequency):
        startFreqBase = floor(self._startTime / frequency)
        rows = floor(self._endTime / frequency) - startFreqBase + 1
        rawobjs = [None] * rows # 2-d array of millisecond + data
        for i in range(rows):
            rawobjs[i] = [None] * self._colsize
            rawobjs[i][0] = (startFreqBase + i) * frequency
        
        rowidx = 0
        
        for pname in self._series:
            lastrowidx = -1
            serie = self._series[pname]
            colidx = self._indices.get(serie.name())
            decoders = VDataSeriesDecodeBuilder.builds(serie.buckets())
            for decoder in decoders:
                while (not decoder.isEmpty()):
                    rowidx = floor(decoder.timestamp() / frequency) - startFreqBase
                    
                    if (rowidx != lastrowidx and rowidx >= 0 and rowidx < rows):
                        lastrowidx = rowidx
                        if (rawobjs[rowidx][colidx] is None):
                            rawobjs[rowidx][colidx] = decoder.value()
                    
                    decoder.pollAndAdd()
        
        return rawobjs

    def createValueArray(self, time):
        return VDataDenseArray(time, self._colsize)

    def comp(self, arrs, time, colidx, subNames, subIndices, result):
        VDataObjectsUtils.compareUniqueMode(arrs, time, result)

class VDataObjectsSeriesFirstMode (VDataObjectsSeriesReader):
    def __init__(self, series, signalFilter, columnExpandMode, qualifiedExpandName, startTime, endTime):
        super().__init__(series, signalFilter, columnExpandMode, qualifiedExpandName, startTime, endTime)

    def createValueArray(self, time):
        return VDataDenseArrayFirstMode(time, self._colsize)

class VDataObjectsSeriesAllMode (VDataObjectsSeriesReader):
    def __init__(self, series, signalFilter, columnExpandMode, qualifiedExpandName, startTime, endTime):
        super().__init__(series, signalFilter, columnExpandMode, qualifiedExpandName, startTime, endTime)

    def createValueArray(self, time):
        return VDataDenseArray(time, self._colsize)

    def comp(self, arrs, time, colidx, subNames, subIndices, result):
        VDataObjectsUtils.compareAllMode(arrs, time, self._columnExpandMode, colidx, subNames, subIndices, result)
        
class VDataSignalDecoder:
    def decode(self, data):
        return data
    
    def getSubNames(self):
        return None
    
    def getSubValues(self, object):
        return object

class VDataObjectsUtils:
    def compareUniqueMode(arrs, time, result):
        size = len(arrs)
        subtime = 0
        comp = 0
    
        # initialize result
        result[0] = result[1] = 0
    
        low = 0
        high = size - 1
        mid = 0

        while (high > low):
            mid = floor((low + high) / 2)
            subtime = arrs[mid].getTime()
            comp = time - subtime
            if (comp == 0):
                result[0] = mid
                result[1] = 1; # found matching sub-millis = true
                return
            elif (comp < 0):
                high = mid - 1
            else:
                low = mid + 1
        
        if (high == low):
            subtime = arrs[low].getTime()
            comp = time - subtime
            if (comp == 0):
                result[0] = low
                result[1] = 1 # found matching sub-millis = true
            elif (comp < 0):
                result[0] = low
            else:
                result[0] = low + 1
        elif (comp < 0):
            result[0] = mid
        else:
            result[0] = mid + 1

    def compareAllMode(arrs, time, expand, colidx, subNames, subIndices, result):
        size = len(arrs)
        subtime = 0
        comp = 0
        
        # initialize result
        result[0] = result[1] = 0
        
        low = 0
        high = size - 1
        mid = 0

        while (high > low):
            mid = floor((low + high) / 2)
            subtime = arrs[mid].getTime()
            comp = time - subtime
            if (comp == 0):
                # found same time, we need to check if this time already has
                # values for this series.  If not, add new rows

                vals = arrs[mid]
                if (VDataObjectsUtils.isEmptyAt(vals, expand, colidx, subNames, subIndices)):
                    while (mid - 1 >= 0):
                        vals = arrs[mid - 1]
                        if (time != vals.getTime()):
                            break
                        if (not VDataObjectsUtils.isEmptyAt(vals, expand, colidx, subNames, subIndices)):
                            break
                        mid = mid - 1
                    
                    result[0] = mid
                    result[1] = 1; # found match and empty position
                    return
                else:
                    while (mid + 1 < size):
                        vals = arrs[mid + 1]
                        if (time != vals.getTime()):
                            result[0] = mid + 1
                            return
                        
                        if (VDataObjectsUtils.isEmptyAt(vals, expand, colidx, subNames, subIndices)):
                            result[0] = mid + 1
                            result[1] = 1 # found match and empty position
                            return
                        
                        mid = mid + 1;   
                    
                    result[0] = mid + 1
                    return
            elif (comp < 0):
                high = mid - 1
            else:
                low = mid + 1
        
        if (high == low):
            subtime = arrs[low].getTime()
            comp = time - subtime
            if (comp == 0):
                vals = arrs[low]
                if (VDataObjectsUtils.isEmptyAt(vals, expand, colidx, subNames, subIndices)):
                    while (low - 1 >= 0 and time == arrs[low - 1].getTime()):
                        low = low - 1

                    result[0] = low
                    result[1] = 1 # found match and empty position
                    return
                else:
                    while (low + 1 < size):
                        if (time != arrs[low + 1].getTime()):
                            result[0] = low + 1
                            return
                        
                        if (VDataObjectsUtils.isEmptyAt(arrs[low + 1], expand, colidx, subNames, subIndices)):
                            result[0] = low + 1
                            result[1] = 1 # found match and empty position
                            return
                        
                        low = low + 1   
                    
                    result[0] = low + 1
                
            elif (comp < 0):
                result[0] = low
            else:
                result[0] = low + 1
        elif (comp < 0):
            result[0] = mid
        else:
            result[0] = mid + 1

    def isEmptyAt(vals, expand, colidx, subNames, subIndices):
        if (subNames is None or expand == DExpand.NONE):
            return vals.isEmptyAt(colidx)
        else:
            for i in range(len(subNames)):
                if (subIndices[i] is not None):
                    if (not vals.isEmptyAt(subIndices[i])):
                        return False
        
        return True

class VDataReaderFactory:
    '''
    A factory class for building VDataReader.

    Examples:
        >>> factory = VDataReaderFactory()
        >>> factory.setDataReaders(file)
        >>> factory.setSignals(signals)
        >>> reader = factory.open()
    '''

    def __init__(self):
        '''
        The constructor of the factory.
        '''
        self._readers = None
        self._signals = None
        self._insensitiveCase = False
        self._readLivingData = True
        self._queryFilter = True
        self._queryStartTime = 0
        self._queryEndTime = 0
        self._columnExpandMode = None
        self._signalQueueMode = None
        self._signalDecoders = {}

    def setDataReaders(self, readers):
        '''
        Set a list of binary readers to vdata file contents.

        Args:
            readers (array_like(reader)): seekable byte readers
        '''
        self._readers = readers

    def setSignals(self, signals):
        '''
        Set the list of signals to select from data contents.

        Args:
            signals (str): comma-separated string of signal names or prefixes
        '''
        self._signals = signals
    
    def setInsensitiveCase(self, insensitiveCase):
        '''
        Set whether to read signal names as case insensitive. If True, it will read the names as lower-case;
        if False, it will read signal names as recorded in vdata.  Default is False.

        Args:
            insensitiveCase (bool): True or False
        '''
        self._insensitiveCase = insensitiveCase
    
    def setReadLivingData(self, readLiving):
        '''
        Set whether to read vdata's living (not finalized) buckets.  Default is True.

        Args:
            readLiving (bool): True or False
        '''
        self._readLivingData = readLiving
    
    def setQueryFilter(self, filter):
        '''
        Set whether to apply query start-end time filter to data contents (including custom start-end
        time and query start-time settings inside data files).  Default is True.

        Args:
            filter (bool): True or False
        '''
        self._queryFilter = filter
    
    def setQueryStartTime(self, time):
        '''
        Set whether to apply a custom query start time (inclusive) to data contents.  This setting is on
        only if queryFilter is true and this value is non-zero. If on, only signal values with time equal 
        to or later than this start time will be output.  Default is 0.

        Args:
            time (int): millisecond since EPOCH
        '''
        self._queryStartTime = time
    
    def setQueryEndTime(self, time):
        '''
        Set whether to apply a custom query end time (inclusive) to data contents.  This setting is on
        only if queryFilter is true and this value is non-zero. If on, only signal values with time equal
        to or earlier than this end time will be output.  Default is 0.

        Args:
            time (int): millisecond since EPOCH
        '''
        self._queryEndTime = time
    
    def setColumnExpandMode(self, mode):
        '''
        Set the column expand mode for expanding sub-items of complex type signals (array/struct) to individual
        signals. Supported values are 'none', 'flat', 'full'. 
        
        'none' means the complex type signal will be output as array  and will not expand to individual sub-items, 
        'flat' means the complex type signal will be expanded to individual sub-items and each sub-item's defined 
        name will be used, 'full' means the complex type signal will be expanded to individual sub-items but the 
        sub-items will use a qualified naming 'signal_name.sub_name'.

        Args:
            mode (str): the column expand mode
        '''
        self._columnExpandMode = mode
    
    def setSignalQueueMode(self, mode):
        '''
        Set the queue mode for value triage when there are mutiple values at same time. Supported values  are 
        'last', 'first', 'all'.  
        
        'last' means the last-read value is used, 'first' means the first-read value is used, and 'all' means for 
        each value read a new row will be generated thereby maintaining all read values in the output.

        Args:
            mode (str): the signal queue mode
        '''
        self._signalQueueMode = mode
    
    def setSignalDecoders(self, signalDecoders):
        '''
        Set SignalDecodeImplementation Dict for Blob Data. 

        Args:
            signalDecoders (dict): key signal name, value implementation of VDataSignalDecoder
        '''       
        self._signalDecoders = signalDecoders

    def open(self):
        '''
        Create the data reader.  

        Returns:
            VDataReader
        '''
        return VDataReader(self._readers, self._signals, self._insensitiveCase, self._queryFilter, self._queryStartTime, self._queryEndTime, self._readLivingData, self._columnExpandMode, self._signalQueueMode, self._signalDecoders)

class VDataReader:
    '''
    A class to read to read and decode data according to format specification.

    Examples:
        >>> reader = factory.open()
        >>> frame = reader.df()
    '''
    
    def __init__(self, readers, signals=None, insensitiveCase=False, queryFilter=True, queryStartTime=0, queryEndTime=0, readLivingData=True, columnExpandMode=None, signalQueueMode=None, signalDecoders={}):
        '''
        The constructor for data reader.  Deprecated since 2.7.1. Use VDataReaderFactory instead.

        Args:
            readers (array_like(reader)): array of seekable file readers or byte readers.
            signals (str, optional): provide a selected list of signals instead of all signals.  Default is null or empty. 
            insensitiveCase (bool, optional): whether to ignore case sensitivity, default is False.
            queryFilter (bool, optional): whether to apply query range filter, default is True.
            queryStartTime (int, optional): the start time of the query filter (inclusive), default is 0 (no filter).
            queryEndTime (int, optional): the end time of the query filter (inclusive), default is 0 (no filter).
            readLivingData (bool, optional): whether to read living (non-finalized) bucket, default is True.
            columnExpandMode (str, optional): the column expand mode
            signalQueueMode (str, optional): the signal expand mode
            signalDecoders (dict, optional): dictionary of signal name to Customer defined Blob Binary Decode
        '''
        signalFilter = self.__filterSignals(signals)
        ndecoders = len(readers) if isinstance(readers, list) else 1
        self._columnExpandMode = VDataUtils.getColumnExpandMode(columnExpandMode)
        self._signalQueueMode = VDataUtils.getSignalQueueMode(signalQueueMode)
        self._readers = readers if isinstance(readers, list) else [readers]
        self._decoders = []
        self._livingDataBuffer = 1000  #1000ms buffer
        self._signalDecoders = signalDecoders
        self.metas =[]
        buckets = []
        
        livingData = readLivingData
        if (readLivingData):
            if (ndecoders > 1 and VDataUtils.isAllSignalQueueMode(self._signalQueueMode)):
                livingData = False # when there are multiple files and all mode is on, avoid data duplication

        for i in range(ndecoders):
            reader = self._readers[i]
            meta = VDataReader._getMeta(reader)
            self.metas.append(meta)
            decoder = VDataDecoder(reader, meta)
            decoder.setSignalFilter(signalFilter)
            decoder.setInsensitiveCase(insensitiveCase)
            decoder.setReadLivingData(livingData)
            decoder.setQueryFilter(queryFilter)
            decoder.setQueryRange(queryStartTime, queryEndTime)
            decoder.setColumnExpandMode(self._columnExpandMode)
            decoder.setSignalQueueMode(self._signalQueueMode)
            decoder.setSignalDecoders(signalDecoders)
            decoder.initialize()
            VDataDecodeUtils.sortAddDecoder(self._decoders, decoder)
    
        #sort all the buckets and consolidate series, when there is only one file, just use the decoder's.
        series = {}
        if (ndecoders > 1):
            logger.debug("Sort and Add buckets for " + str(ndecoders) + " files")
        
        for i in range(ndecoders):
            decoder = self._decoders[i]
            for bucket in decoder.buckets():
                VDataBucketUtils.sortAddBucket(buckets, bucket, True, self._signalQueueMode)
            for name, _ in decoder.keys().items():
                if name not in series:
                    series[name] = VDataSeries(name)
        
        for b in range(len(buckets)):
            bucket = buckets[b]
            for j in range (len(bucket.seriesBuckets)):
                seriesBucket = bucket.seriesBuckets[j]
                serie = series[seriesBucket.name]
                serie.addBucket(seriesBucket)
                serie.updateBucketItemCounts(b, seriesBucket.getItemCount())
        
        self._frame = VDataFrame(buckets, series, signalFilter, columnExpandMode, signalQueueMode)

        objectStartTime = queryStartTime if queryFilter else 0
        objectEndTime = queryEndTime if queryFilter else 0
        for decoder in self._decoders:
            if (queryStartTime == 0):
                meta = decoder.meta()
                st = meta.storageStartTime() if meta.queryStartTime() == 0 else meta.queryStartTime()
                if len(decoder.buckets()) > 0: # confirm with bucket time
                    bucketst = decoder.buckets()[0].getStartTime()
                    if (bucketst > 0 and bucketst > st):
                        st = bucketst
                
                objectStartTime = st if objectStartTime == 0 else min(objectStartTime, st)
            
            if (queryEndTime == 0):
                meta = decoder.meta()
                et = meta.storageEndTime() if meta.queryEndTime() == 0 else meta.queryEndTime()
                objectEndTime = et if objectEndTime == 0 else max(objectEndTime,  et)
                
                if (meta.queryEndTime() == 0):
                    dbuckets = decoder.buckets()
                    if (len(dbuckets) > 0 and dbuckets[len(dbuckets) - 1].isLiving()):
                        objectEndTime = objectEndTime + self._livingDataBuffer
        self._frame.setStartTime(objectStartTime)
        self._frame.setEndTime(objectEndTime)

    def __filterSignals(self, signals):
        signalFilter = VDataSignalFilter()
        if (not signals or len(signals) == 0):
            return signalFilter
        
        fsignals= []
        fprefixes = []

        for s in signals:
            if (not s):
                continue

            name = s.strip()
            if (len(name) == 0):
                continue

            if (name[len(name) - 1] == '*'):
                while(1):
                    name = name[0:len(name) - 1]
                    if (len(name) == 0 or name[len(name) - 1] != '*'):
                        break

                if (len(name) == 0): # '*' special situation all is selected
                    return signalFilter
                
                fprefixes.append(name)
            else:
                fsignals.append(name)
        
        signalFilter.setSignals(fsignals)
        signalFilter.setPrefixes(fprefixes)
        return signalFilter

    def df(self):
        '''
        Get the data frame.

        Returns:
            VDataFrame
        '''
        return self._frame
    
    def getMeta(self, index=0):
        '''
        Get the meta by index.

        Returns:
            VDataMeta
        '''
        return self.metas[index]

    def getSignalDecoders(self):
        return self._signalDecoders

    def _getMeta(_reader):
        '''
        Static method to read the metadata info from a seekable file reader or a byte reader.

        Args:
            _reader (reader): a seekable file reader or a byte reader
        
        Returns:
            VDataMeta
        '''
        if (b'SD' != _reader.read(2)):
            raise Exception('FORMAT_VDATA_MAGIC_NUMBER_INVALID')

        formatFlags = _reader.read(1)[0]
        compressMethod = int(formatFlags & 0x0F)
        encryptMethod = int((formatFlags >> 4) & 0x0F) # reserved for future
        formatVersion = int(_reader.read(1)[0]) # reserved for future
        blocksCount = _struct.unpack('<i', _reader.read(4))[0]
        if (blocksCount <= 0):
            raise Exception('FORMAT_VDATA_BLOCKS_COUNT_INVALID')

        sstime = 0 # storage start time
        setime = 0 # storage end time
        qstime = 0 # query start time
        qetime = 0 # query end time
        extlength = 0
        pageSizeCode = 0
        keyTypeCode = 0 

        if (formatVersion > 0):
            if (formatVersion < 26):
                (sstime, setime) = _struct.unpack('<qq', _reader.read(16))
            else:
                (sstime, setime, qstime, qetime) = _struct.unpack('<qqqq', _reader.read(32))
            extlength = _struct.unpack('<H', _reader.read(2))[0]
            if (formatVersion > 26):
                pageSizeCode = _reader.read(1)[0]
                keyTypeCode = _reader.read(1)[0]
                _reader.read(4) # reserved
            else:
                _reader.read(6) # reserved

        extbytes = _reader.read(extlength) if (extlength > 0) else []
        return VDataMeta(formatVersion=formatVersion, compressMethod=compressMethod, encryptMethod=encryptMethod, blocksCount=blocksCount, storageStartTime=sstime, storageEndTime=setime, queryStartTime=qstime, queryEndTime=qetime, extendedInfo=extbytes, pageSizeCode = pageSizeCode , keyTypeCode= keyTypeCode)

        
        
