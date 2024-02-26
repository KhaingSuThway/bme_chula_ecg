import os
import wfdb
import neurokit2 as nk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

folder_path="D:/CPSC2021/Training_set_I"
file_list=os.listdir(folder_path)
record_name=[f[:-4] for f in file_list if f.endswith('.hea')]
print(f'There are {len(record_name)} records in this folder')



# Initialize a list to hold the data
data = []

# Loop over the record names
for i in range(len(record_name)):
    # Read the record
    record = wfdb.rdrecord(os.path.join(folder_path, record_name[i]))
    
    # Extract the data
    RecordName = record.record_name
    SamplingFrequency = record.fs
    RecordLength = record.sig_len / SamplingFrequency
    RecordLabel = record.comments[0]
    
    # Append the data to the list
    data.append([RecordName, SamplingFrequency, RecordLength, RecordLabel])

# Convert the list to a DataFrame
summary_of_record = pd.DataFrame(data,
                                 columns=['RecordName', 'SamplingFrequency(hz)', 'RecordLength(s)', 'RecordLabel'])

print(summary_of_record)   
    
summary_of_record.describe()