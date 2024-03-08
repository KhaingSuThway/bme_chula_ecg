import os
import wfdb
import numpy as np
import pandas as pd 


#Checking the records were flipped or not

def check_record_flipping(folder_path):
    flipped_records=[]
    files=[f[:-4] for f in os.listdir(folder_path) if f.endswith('.hea')]
    for file in files:
        signal=wfdb.rdrecord(os.path.join(folder_path,file)).p_signal[:,0]
        symbol_index=wfdb.rdann(os.path.join(folder_path,file),'atr').sample
        check_array=signal[symbol_index[:-1]]
        if np.mean(check_array)<0:
            flipped_records.append(file)
    print(f"There are {len(flipped_records)} flipped records")
    return flipped_records