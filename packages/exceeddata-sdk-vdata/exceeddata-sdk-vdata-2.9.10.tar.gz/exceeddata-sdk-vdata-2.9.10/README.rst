ExceedData vData SDK for Python.
========

Copyright (C) 2016-2024 Smart Software for Car Technologies Inc. and EXCEEDDATA
     https://www.smartsct.com
     https://www.exceeddata.com



ExceedData vData SDK for Python.  Use this SDK to decode vData extreme-compression
vehicle signal data.

Examples:

     >>> from exceeddata.sdk.vdata import VDataReaderFactory 
     >>> import pandas as _pd 

     >>> inputPath = "... .vsw" 
     >>> outputPath="/tmp/output.csv" 
     >>> signals=None # "name1, name2, name3....."
     >>> file = open(inputPath, "rb") 
     >>> 
     >>> factory = VDataReaderFactory() 
     >>> factory.setDataReaders(file) 
     >>> factory.setSignals(signals) 
     
     >>> reader = factory.open() 
     >>> frame = reader.df() 
     >>> df = _pd.DataFrame(frame.objects(), columns=frame.cols(True)) 

Installation
------------

Install vData SDK for Python by running:

    pip3 install vdata

Dependencies
------------

python-snappy, zstd

Support
-------

If you are having issues, please let us know and contact support@smartsct.com

License
-------

The project is licensed under the MIT license.