import os
import wfdb
import numpy as np

def check_record_flipping(file_path):
    """
    Check if ECG records are flipped or not.

    Parameters:
    - file_path: Path to the directory containing the ECG records.

    Returns:
    - True if records are flipped, False otherwise.
    """
    try:
        files = os.listdir(file_path)
    except FileNotFoundError:
        print("Directory not found.")
        return False

    for file in files:
        if not file.endswith('.hea'):  # Assuming ECG records have a .hea extension
            continue

        try:
            record = wfdb.rdrecord(os.path.join(file_path, file))
            annotations = wfdb.rdann(os.path.join(file_path, file[:-4]), 'atr')
        except Exception as e:
            print(f"Error reading file {file}: {e}")
            continue

        signal = record.p_signal[:, 0]
        symbol_index = annotations.sample
        check_array = signal[symbol_index[:-1]]

        if np.mean(check_array) < 0:
            print(f"Record {file} is flipped.")
            return True

    print("No flipped records found.")
    return False
